from __future__ import annotations

from html import escape
import time

import streamlit as st

from modules.audio_features import analyze_wav
from modules.browser_history import sync_browser_history
from modules.consent import CONSENT_SESSION_KEY
from modules.deepseek_service import (
    DeepSeekServiceError,
    generate_informant_summary,
    generate_reply,
    get_api_key,
    transcribe_audio,
)
from modules.emotion import is_emotionally_distressed
from modules.i18n import (
    get_response_language,
    get_speech_language,
    get_tts_voice,
    localize_service_error,
    tr,
)
from modules.crisis import detects_crisis
from modules.medical_safety import requires_medical_disclaimer
from modules.memory_extractor import extract_memory_from_input
from modules.observation_log import (
    initialize_observation_state,
    render_observation_panel,
    reset_observation_state,
)
from modules.scope_guard import contains_disallowed_content, is_out_of_scope_request
from modules.ui import render_brand
from modules.tts_service import TTSError, autoplay_audio_html, synthesize_speech


MOCK_QUESTION_KEYS = (
    "mock_q1",
    "mock_q2",
    "mock_q3",
    "mock_q4",
)
SUMMARY_BUTTON_AFTER_TURNS = 4
INFORMANT_REPORT_INTERVAL = 5


def _initialize_state() -> None:
    st.session_state.setdefault("chat_messages", [])
    st.session_state.setdefault("user_turns", 0)
    st.session_state["chat_completed"] = False
    st.session_state.setdefault("pending_transcript", None)
    st.session_state.setdefault("pending_speech_ms", None)
    st.session_state.setdefault("empathy_turns_left", 0)
    st.session_state.setdefault("input_error", None)
    st.session_state.setdefault("transcript_revision", 0)
    st.session_state.setdefault("deepseek_usage_tokens", 0)
    st.session_state.setdefault("asr_duration_ms", 0)
    st.session_state.setdefault("audio_input_revision", 0)
    st.session_state.setdefault("tts_autoplay_pending", None)
    st.session_state.setdefault("informant_report", None)
    st.session_state.setdefault("informant_report_turn", 0)
    initialize_observation_state()


def _reset_conversation() -> None:
    st.session_state["chat_messages"] = []
    st.session_state["user_turns"] = 0
    st.session_state["chat_completed"] = False
    st.session_state["pending_transcript"] = None
    st.session_state["pending_speech_ms"] = None
    st.session_state["empathy_turns_left"] = 0
    st.session_state["input_error"] = None
    st.session_state["transcript_revision"] += 1
    st.session_state["deepseek_usage_tokens"] = 0
    st.session_state["asr_duration_ms"] = 0
    st.session_state["audio_input_revision"] += 1
    st.session_state.pop("tts_audio_cache", None)
    st.session_state["tts_autoplay_pending"] = None
    st.session_state["informant_report"] = None
    st.session_state["informant_report_turn"] = 0
    reset_observation_state()


def _clear_inactive_transcript_fields() -> None:
    if st.session_state["pending_transcript"] is None:
        for key in list(st.session_state.keys()):
            if key.startswith("pending_transcript_edit_"):
                st.session_state.pop(key, None)


def _synchronize_mode(live_enabled: bool) -> None:
    previous_mode = st.session_state.get("active_api_mode")
    current_mode = "deepseek" if live_enabled else "local"
    if previous_mode is None:
        st.session_state["active_api_mode"] = current_mode
    elif previous_mode != current_mode:
        _reset_conversation()
        st.session_state["active_api_mode"] = current_mode
        st.session_state["mode_notice"] = tr("mode_changed")


def _mock_reply(user_turns: int) -> str:
    question_key = MOCK_QUESTION_KEYS[(user_turns - 1) % len(MOCK_QUESTION_KEYS)]
    return f"{tr('mock_thanks')} {tr(question_key)}"


def _record_observation(content: str) -> None:
    try:
        note = extract_memory_from_input(content)
    except Exception:
        return
    if isinstance(note, dict) and note.get("summary"):
        st.session_state.setdefault("auto_memory_log", []).append(note)


def _append_user_message(
    content: str,
    api_key: str | None,
    live_enabled: bool,
) -> None:
    clean_content = content.strip()
    if not clean_content:
        return

    if detects_crisis(clean_content):
        st.session_state["crisis_flagged"] = True
        st.session_state["chat_messages"].append(
            {"role": "user", "content": clean_content, "scope_blocked": True}
        )
        st.session_state["chat_messages"].append(
            {
                "role": "assistant",
                "content": tr("crisis_response"),
                "mode": "crisis",
                "scope_blocked": True,
                "speech_language": get_speech_language(),
            }
        )
        st.session_state["tts_autoplay_pending"] = (
            len(st.session_state["chat_messages"]) - 1
        )
        return

    if requires_medical_disclaimer(clean_content):
        st.session_state["chat_messages"].append(
            {
                "role": "user",
                "content": clean_content,
                "scope_blocked": True,
                "medical_guarded": True,
            }
        )
        st.session_state["user_turns"] += 1
        st.session_state["chat_messages"].append(
            {
                "role": "assistant",
                "content": tr("medical_disclaimer"),
                "mode": "medical-guard",
                "scope_blocked": True,
                "speech_language": get_speech_language(),
            }
        )
        st.session_state["tts_autoplay_pending"] = (
            len(st.session_state["chat_messages"]) - 1
        )
        return

    has_life_context = any(
        message.get("role") == "user" and not message.get("scope_blocked")
        for message in st.session_state["chat_messages"]
    )
    if is_out_of_scope_request(clean_content, has_life_context):
        st.session_state["chat_messages"].append(
            {"role": "user", "content": clean_content, "scope_blocked": True}
        )
        st.session_state["chat_messages"].append(
            {
                "role": "assistant",
                "content": tr("scope_refusal"),
                "mode": "scope-guard",
                "scope_blocked": True,
                "speech_language": get_speech_language(),
            }
        )
        st.session_state["tts_autoplay_pending"] = (
            len(st.session_state["chat_messages"]) - 1
        )
        return

    st.session_state["chat_messages"].append(
        {"role": "user", "content": clean_content}
    )
    st.session_state["user_turns"] += 1
    user_turns = st.session_state["user_turns"]

    if is_emotionally_distressed(clean_content):
        st.session_state["empathy_turns_left"] = 3
    elif st.session_state["empathy_turns_left"] > 0:
        st.session_state["empathy_turns_left"] -= 1
    empathy_active = st.session_state["empathy_turns_left"] > 0

    if live_enabled and api_key:
        try:
            result = generate_reply(
                api_key,
                st.session_state["chat_messages"],
                user_turns,
                response_language=get_response_language(),
                empathy=empathy_active,
            )
            reply = result.content
            mode = "deepseek"
            if result.total_tokens is not None:
                st.session_state["deepseek_usage_tokens"] += result.total_tokens
            if contains_disallowed_content(reply):
                reply = tr("scope_refusal")
                mode = "scope-guard"
        except DeepSeekServiceError as error:
            st.session_state["input_error"] = localize_service_error(str(error))
            reply = _mock_reply(user_turns)
            mode = "local-fallback"
    else:
        reply = _mock_reply(user_turns)
        mode = "local-demo"

    st.session_state["chat_messages"].append(
        {
            "role": "assistant",
            "content": reply,
            "mode": mode,
            "speech_language": get_speech_language(),
        }
    )
    st.session_state["tts_autoplay_pending"] = (
        len(st.session_state["chat_messages"]) - 1
    )
    st.session_state["chat_completed"] = False
    _record_observation(clean_content)
    _maybe_generate_informant_report(api_key, live_enabled, user_turns)


def _generate_informant_report(
    api_key: str | None,
    live_enabled: bool,
    user_turns: int,
    manual: bool = False,
) -> bool:
    if not live_enabled or not api_key:
        if manual:
            st.session_state["input_error"] = tr("summary_requires_ai")
        return False

    try:
        with st.spinner(tr("summarizing")):
            report = generate_informant_summary(
                api_key,
                st.session_state["chat_messages"],
                response_language=get_response_language(),
            )
    except DeepSeekServiceError as error:
        st.session_state["input_error"] = localize_service_error(str(error))
        return False

    total_tokens = report.get("total_tokens")
    if type(total_tokens) is int and total_tokens >= 0:
        st.session_state["deepseek_usage_tokens"] += total_tokens

    st.session_state["informant_report"] = {
        "turn": user_turns,
        "generated_at": time.time(),
        **report,
    }
    st.session_state["informant_report_turn"] = user_turns
    return True


def _maybe_generate_informant_report(
    api_key: str | None,
    live_enabled: bool,
    user_turns: int,
) -> None:
    if not live_enabled or not api_key:
        return
    if user_turns < INFORMANT_REPORT_INTERVAL:
        return
    if user_turns % INFORMANT_REPORT_INTERVAL != 0:
        return
    if st.session_state.get("informant_report_turn") == user_turns:
        return
    _generate_informant_report(api_key, live_enabled, user_turns, manual=False)


def _render_conversation(api_key: str | None, live_enabled: bool) -> None:
    messages = st.session_state["chat_messages"]
    if not messages:
        return

    highlight_quote = st.session_state.get("highlight_quote") or ""
    for message_index, message in enumerate(messages):
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message.get("mode") == "crisis":
                st.markdown(
                    f'<div class="crisis-card">{escape(message["content"])}</div>',
                    unsafe_allow_html=True,
                )
                st.caption(tr("crisis_badge"))
                _autoplay_assistant_message(message, message_index)
                continue
            if (
                message["role"] == "assistant"
                and message.get("mode") == "scope-guard"
            ):
                st.markdown(
                    f'<div class="scope-guide-card">{escape(message["content"])}</div>',
                    unsafe_allow_html=True,
                )
                st.caption(tr("scope_badge"))
                _autoplay_assistant_message(message, message_index)
                topic_keys = (
                    ("scope_topic_mood", "scope_prompt_mood"),
                    ("scope_topic_routine", "scope_prompt_routine"),
                    ("scope_topic_memory", "scope_prompt_memory"),
                )
                for label_key, prompt_key in topic_keys:
                    if st.button(
                        tr(label_key),
                        key=f"scope_topic_{message_index}_{label_key}",
                        width="stretch",
                    ):
                        _append_user_message(tr(prompt_key), api_key, live_enabled)
                        st.rerun()
                continue

            if (
                highlight_quote
                and message["role"] == "user"
                and isinstance(message.get("content"), str)
                and highlight_quote[:60] in message["content"]
            ):
                st.markdown(
                    f'<div class="msg-highlight">{escape(message["content"])}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(message["content"])
            if message["role"] == "assistant":
                if message.get("mode") == "deepseek":
                    st.caption(tr("ai_badge"))
                elif message.get("mode") in {"local-demo", "local-fallback"}:
                    st.caption(tr("local_badge"))
                _autoplay_assistant_message(message, message_index)


def _autoplay_assistant_message(
    message: dict[str, str],
    message_index: int,
) -> None:
    if st.session_state.get("tts_autoplay_pending") != message_index:
        return

    st.session_state["tts_autoplay_pending"] = None
    language = message.get("speech_language", get_speech_language())
    cache = st.session_state.setdefault("tts_audio_cache", {})
    cache_key = f"{message_index}:{language}"
    try:
        audio = cache.get(cache_key)
        if audio is None:
            with st.spinner(tr("speaking")):
                audio = synthesize_speech(
                    message["content"],
                    get_tts_voice(language),
                )
            cache[cache_key] = audio
        st.markdown(autoplay_audio_html(audio), unsafe_allow_html=True)
    except TTSError:
        st.warning(tr("tts_error"))


def _render_transcript_review() -> None:
    pending_transcript = st.session_state.get("pending_transcript")
    if pending_transcript is None:
        return
    transcript_key = (
        f"pending_transcript_edit_{st.session_state['transcript_revision']}"
    )

    with st.container(border=True):
        st.markdown(f"### {tr('transcript_title')}")
        st.caption(tr("transcript_help"))
        with st.form("voice_transcript_review"):
            edited_transcript = st.text_area(
                tr("transcript_label"),
                value=pending_transcript,
                height=130,
                max_chars=1500,
                key=transcript_key,
            )
            send_column, cancel_column = st.columns(2, gap="small")
            with send_column:
                send_transcript = st.form_submit_button(
                    tr("send"),
                    type="primary",
                    width="stretch",
                )
            with cancel_column:
                cancel_transcript = st.form_submit_button(
                    tr("cancel"),
                    width="stretch",
                )

    if send_transcript:
        api_key = get_api_key()
        live_enabled = bool(api_key and st.session_state.get(CONSENT_SESSION_KEY))
        st.session_state["pending_transcript"] = None
        speech_ms = st.session_state.pop("pending_speech_ms", None)
        _append_user_message(edited_transcript, api_key, live_enabled)
        _attach_speech_metric(edited_transcript, speech_ms)
        st.rerun()
    if cancel_transcript:
        st.session_state["pending_transcript"] = None
        st.session_state["pending_speech_ms"] = None
        st.session_state.pop("pending_vocal", None)
        st.session_state["transcript_revision"] += 1
        st.rerun()


def _attach_speech_metric(
    transcript: str,
    speech_ms: int | float | None,
) -> None:
    if not isinstance(speech_ms, (int, float)) or speech_ms <= 0:
        return
    chars = len("".join(transcript.split()))
    if not chars:
        return
    cpm = round(chars / (speech_ms / 60000.0), 1)
    for message in reversed(st.session_state["chat_messages"]):
        if message.get("role") == "user" and not message.get("scope_blocked"):
            message["speech_cpm"] = cpm
            message["speech_ms"] = round(speech_ms)
            vocal = st.session_state.pop("pending_vocal", None)
            if isinstance(vocal, dict):
                message["vocal"] = vocal
            return


def main() -> None:
    _initialize_state()
    sync_browser_history()
    render_brand(tr("home_brand"))

    st.markdown(
        f'<h1 class="page-title">{tr("home_title")}</h1>'
        f'<p class="conversation-copy">{tr("home_intro")}</p>'
        f'<p class="conversation-copy">{tr("conversation_purpose")}</p>'
        f'<p class="conversation-copy">{tr("turn_limit")}</p>',
        unsafe_allow_html=True,
    )
    api_key = get_api_key()
    consent = bool(st.session_state.get(CONSENT_SESSION_KEY, False))
    live_enabled = bool(api_key and consent)
    if not api_key:
        st.info(f"{tr('local_mode')} {tr('local_voice_off')}")

    _synchronize_mode(live_enabled)
    _clear_inactive_transcript_fields()
    mode_notice = st.session_state.pop("mode_notice", None)
    if mode_notice:
        st.info(mode_notice)
    if st.session_state["input_error"]:
        st.warning(st.session_state.pop("input_error"))
    if st.session_state.get("empathy_turns_left", 0) > 0:
        st.markdown(
            "<style>.stApp { background: #fdf7ee !important; }</style>",
            unsafe_allow_html=True,
        )
    if st.session_state.get("crisis_flagged"):
        st.markdown(
            f'<div class="crisis-banner">{escape(tr("crisis_banner"))}</div>',
            unsafe_allow_html=True,
        )

    _render_conversation(api_key, live_enabled)
    _render_transcript_review()

    if (
        st.session_state["user_turns"] >= SUMMARY_BUTTON_AFTER_TURNS
        and st.session_state["pending_transcript"] is None
    ):
        if st.button(
            tr("summary_button"),
            type="primary",
            width="stretch",
            key="summary_button",
        ):
            _generate_informant_report(
                api_key,
                live_enabled,
                st.session_state["user_turns"],
                manual=True,
            )
            st.rerun()

    drawer_open = st.session_state.get("obs_drawer_open", False)
    with st.container(key="obs_drawer_btn"):
        if st.button(
            tr("observation_title"),
            key="obs_drawer_button",
            width="content",
        ):
            st.session_state["obs_drawer_open"] = not drawer_open
            st.rerun()
    if drawer_open:
        st.markdown(
            '<span class="obs-open-marker" aria-hidden="true"></span>',
            unsafe_allow_html=True,
        )
    with st.container(key="observation_drawer"):
        render_observation_panel()

    audio_disabled = (
        not live_enabled
        or st.session_state["pending_transcript"] is not None
    )
    recording = st.bottom.audio_input(
        label=tr("mic_speak" if live_enabled else "mic_disabled"),
        sample_rate=16000,
        key=f"voice_recording_{st.session_state['audio_input_revision']}",
        disabled=audio_disabled,
        label_visibility="collapsed",
        width="stretch",
    )
    if recording is not None:
        st.session_state["audio_input_revision"] += 1
        if live_enabled and api_key:
            try:
                with st.spinner(tr("transcribing")):
                    transcription = transcribe_audio(recording.getvalue(), api_key)
                st.session_state["asr_duration_ms"] += transcription.duration_ms
                st.session_state["pending_speech_ms"] = transcription.duration_ms
                st.session_state["pending_vocal"] = analyze_wav(
                    recording.getvalue()
                )
                st.session_state["transcript_revision"] += 1
                st.session_state["pending_transcript"] = transcription.text
            except DeepSeekServiceError as error:
                st.session_state["input_error"] = localize_service_error(str(error))
        else:
            st.session_state["input_error"] = tr("local_voice_off")
        st.rerun()

    submission = st.chat_input(
        tr("chat_placeholder"),
        key="conversation_input",
        max_chars=1500,
        disabled=st.session_state["pending_transcript"] is not None,
    )

    if submission and submission.strip():
        _append_user_message(submission, api_key, live_enabled)
        st.rerun()


if __name__ == "__main__":
    main()
