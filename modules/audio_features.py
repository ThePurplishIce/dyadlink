"""Real acoustic feature extraction from recorded WAV audio.

Computes pause behaviour and pitch variability with numpy only —
these are honest, computable vocal-biomarker proxies used in
digital-phenotyping research (pause rate, F0 variability).
"""

from __future__ import annotations

import io
import wave

import numpy as np

_MAX_ANALYZE_SECONDS = 45.0
_FRAME_HOP = 0.010  # s
_FRAME_WIN = 0.025  # s
_MIN_PAUSE_S = 0.25
_F0_WIN = 0.060  # s
_F0_MIN_HZ = 75.0
_F0_MAX_HZ = 400.0
_F0_PEAK_MIN = 0.55
_MAX_PITCH_FRAMES = 1500


def _decode_wav(wav_bytes: bytes) -> tuple[np.ndarray, int] | None:
    try:
        with wave.open(io.BytesIO(wav_bytes)) as handle:
            channels = handle.getnchannels()
            width = handle.getsampwidth()
            rate = handle.getframerate()
            raw = handle.readframes(handle.getnframes())
    except (wave.Error, EOFError):
        return None
    if width == 2:
        data = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    elif width == 4:
        data = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
    elif width == 1:
        data = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        return None
    if not data.size or rate <= 0:
        return None
    if channels > 1:
        data = data[: data.size - data.size % channels].reshape(-1, channels).mean(axis=1)
    return data, rate


def _frame_rms(x: np.ndarray, rate: int) -> np.ndarray:
    win = max(int(_FRAME_WIN * rate), 1)
    hop = max(int(_FRAME_HOP * rate), 1)
    if x.size < win:
        return np.array([float(np.sqrt(np.mean(x * x)))])
    count = (x.size - win) // hop + 1
    idx = np.arange(count)[:, None] * hop + np.arange(win)[None, :]
    frames = x[idx]
    return np.sqrt(np.mean(frames * frames, axis=1))


def _f0_track(x: np.ndarray, rate: int, rms_floor: float) -> list[float]:
    win = int(_F0_WIN * rate)
    hop = int(_FRAME_HOP * 4 * rate)
    lag_lo = max(int(rate / _F0_MAX_HZ), 1)
    lag_hi = int(rate / _F0_MIN_HZ)
    fft_n = int(2 ** np.ceil(np.log2(win * 2)))
    f0s: list[float] = []
    step = max(1, (x.size - win) // (hop * _MAX_PITCH_FRAMES))
    for start in range(0, max(int(x.size - win), 0), hop * step):
        seg = x[start : start + win]
        seg = seg - seg.mean()
        if float(np.sqrt(np.mean(seg * seg))) < rms_floor:
            continue
        spec = np.fft.rfft(seg * np.hanning(win), n=fft_n)
        acorr = np.fft.irfft(np.abs(spec) ** 2)[: lag_hi + 1]
        if acorr[0] <= 0:
            continue
        acorr = acorr / acorr[0]
        lag = int(np.argmax(acorr[lag_lo:])) + lag_lo
        if acorr[lag] >= _F0_PEAK_MIN:
            f0s.append(rate / lag)
    return f0s


def analyze_wav(wav_bytes: bytes) -> dict[str, float] | None:
    """Return pause/pitch features or None if undecodable/too quiet."""
    decoded = _decode_wav(wav_bytes)
    if not decoded:
        return None
    x, rate = decoded
    x = x[: int(_MAX_ANALYZE_SECONDS * rate)]
    if x.size < rate // 2:
        return None

    rms = _frame_rms(x, rate)
    noise = float(np.percentile(rms, 20))
    peak = float(np.percentile(rms, 90))
    floor = max(min(noise * 2.5, peak * 0.3), 0.008)
    voiced = rms > floor
    voiced_ratio = float(voiced.mean())
    if voiced_ratio < 0.05:
        return None

    silent = ~voiced
    pauses = 0
    pause_lengths: list[float] = []
    run = 0
    for flag in silent:
        if flag:
            run += 1
        else:
            if run * _FRAME_HOP >= _MIN_PAUSE_S:
                pauses += 1
                pause_lengths.append(run * _FRAME_HOP)
            run = 0
    if run * _FRAME_HOP >= _MIN_PAUSE_S:
        pauses += 1
        pause_lengths.append(run * _FRAME_HOP)

    f0s = _f0_track(x, rate, floor)
    f0_sd_st = 0.0
    if len(f0s) >= 8:
        semitones = 12.0 * np.log2(np.asarray(f0s) / np.median(f0s))
        f0_sd_st = float(np.std(semitones))

    duration = x.size / rate
    return {
        "duration_s": round(duration, 2),
        "voiced_ratio": round(voiced_ratio, 3),
        "silence_ratio": round(1.0 - voiced_ratio, 3),
        "pause_count": float(pauses),
        "pause_per_min": round(pauses / (duration / 60.0), 1),
        "mean_pause_s": round(
            float(np.mean(pause_lengths)) if pause_lengths else 0.0, 2
        ),
        "f0_sd_st": round(f0_sd_st, 2),
    }
