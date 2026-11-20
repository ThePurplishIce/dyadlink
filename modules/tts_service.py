import asyncio
import base64


class TTSError(Exception):
    pass


def autoplay_audio_html(audio: bytes) -> str:
    encoded_audio = base64.b64encode(audio).decode("ascii")
    return (
        '<audio autoplay="autoplay" playsinline="playsinline" '
        'webkit-playsinline="webkit-playsinline" preload="auto" aria-hidden="true" '
        f'style="display:none" src="data:audio/mpeg;base64,{encoded_audio}"></audio>'
    )


def synthesize_speech(text: str, voice: str) -> bytes:
    if not text.strip():
        raise TTSError("empty_text")
    if len(text) > 1000:
        raise TTSError("text_too_long")

    try:
        import edge_tts
    except ImportError:
        raise TTSError("not_installed") from None

    async def collect_audio() -> bytes:
        communicator = edge_tts.Communicate(text, voice)
        chunks = []
        async for chunk in communicator.stream():
            if chunk.get("type") == "audio":
                chunks.append(chunk["data"])
        return b"".join(chunks)

    try:
        audio = asyncio.run(collect_audio())
    except Exception:
        raise TTSError("service_unavailable") from None
    if not audio:
        raise TTSError("empty_audio")
    return audio
