import streamlit as st

from modules.browser_history import (
    clear_all_storage,
    read_consent_state,
    set_consent_storage,
)
from modules.i18n import render_language_selector, tr
from modules.ui import render_brand


CONSENT_SESSION_KEY = "external_processing_consent_v3"
CONSENT_TERMINATED_KEY = "external_processing_consent_terminated"


def _clear_conversation_state() -> None:
    keys = (
        "chat_messages",
        "user_turns",
        "chat_completed",
        "pending_transcript",
        "input_error",
        "transcript_revision",
        "deepseek_usage_tokens",
        "asr_duration_ms",
        "tts_audio_cache",
        "tts_autoplay_pending",
        "active_api_mode",
        "mode_notice",
        "deepseek_consent",
        "auto_memory_log",
        "informant_report",
        "informant_report_turn",
        "browser_history",
        "browser_history_loaded",
        "browser_history_cleared_ts",
    )
    for key in keys:
        st.session_state.pop(key, None)
    for key in list(st.session_state.keys()):
        if key.startswith("pending_transcript_edit_"):
            st.session_state.pop(key, None)


def _render_exit_screen() -> None:
    render_brand(tr("exit_brand"))
    st.markdown(
        f'<h1 class="page-title">{tr("exit_title")}</h1>'
        f'<p class="page-copy">{tr("exit_copy")}</p>',
        unsafe_allow_html=True,
    )
    st.stop()


def render_required_consent() -> None:
    if st.session_state.get(CONSENT_TERMINATED_KEY):
        _render_exit_screen()
    if st.session_state.get(CONSENT_SESSION_KEY):
        return
    if read_consent_state() == "1":
        st.session_state[CONSENT_SESSION_KEY] = True
        return

    st.markdown(
        """
        <style>
        .st-key-consent_panel {
            display: flex;
            min-height: 76vh;
            max-width: 940px;
            flex-direction: column;
            justify-content: center;
            margin: 3vh auto;
            padding: clamp(1.25rem, 4vw, 3rem);
            border: 1px solid #d7e3ec;
            border-radius: 1.5rem;
            background: rgba(255, 255, 255, 0.96);
            box-shadow: 0 18px 48px rgba(28, 64, 86, 0.09);
        }
        .consent-title {
            margin: 0 0 1rem;
            color: #17364e;
            font-size: clamp(2rem, 5vw, 3.25rem);
            font-weight: 760;
            line-height: 1.2;
        }
        .consent-copy {
            color: #334f63;
            font-size: clamp(1.15rem, 2.2vw, 1.4rem);
            line-height: 1.75;
        }
        .st-key-consent_panel [data-testid="stButton"] button {
            min-height: 4.1rem;
            font-size: 1.12rem;
            font-weight: 700;
        }
        @media (max-width: 700px) {
            .st-key-consent_panel {
                min-height: calc(100vh - 2rem);
                margin: 0.5rem auto;
                padding: 1.25rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.container(key="consent_panel"):
        render_language_selector(in_sidebar=False)
        render_brand(tr("consent_brand"))
        st.markdown(
            f'<h1 class="consent-title">{tr("consent_title")}</h1>'
            f'<p class="consent-copy">{tr("consent_copy")}</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"- {tr('consent_reflection')}\n"
            f"- {tr('consent_session')}\n"
            f"- {tr('consent_local')}\n"
            f"- {tr('consent_observation')}"
        )
        st.markdown(
            f"[DeepSeek {tr('privacy_link')}](https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-privacy-policy.html)"
            f" · [{tr('microsoft_policy')}](https://privacy.microsoft.com/privacystatement)"
        )
        agree_column, decline_column = st.columns(2, gap="medium")
        with agree_column:
            agree = st.button(
                tr("agree_enter"),
                type="primary",
                key="accept_external_processing",
                width="stretch",
            )
        with decline_column:
            decline = st.button(
                tr("decline_exit"),
                key="decline_external_processing",
                width="stretch",
            )

    if agree:
        set_consent_storage()
        st.session_state[CONSENT_SESSION_KEY] = True
        st.session_state[CONSENT_TERMINATED_KEY] = False
        st.session_state.pop("deepseek_consent", None)
        st.rerun()
    if decline:
        st.session_state[CONSENT_SESSION_KEY] = False
        st.session_state[CONSENT_TERMINATED_KEY] = True
        st.session_state.pop("deepseek_consent", None)
        st.rerun()
    st.stop()


def render_consent_controls() -> None:
    if not st.session_state.get(CONSENT_SESSION_KEY):
        return
    with st.sidebar:
        if st.button(
            tr("revoke_exit"),
            key="withdraw_external_processing_consent",
            width="stretch",
        ):
            _clear_conversation_state()
            clear_all_storage()
            st.session_state[CONSENT_SESSION_KEY] = False
            st.session_state[CONSENT_TERMINATED_KEY] = True
            st.rerun()
