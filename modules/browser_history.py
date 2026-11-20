"""Conversation and consent persistence across page refreshes.

Browser storage (localStorage) is unreliable here — tracking-prevention
settings block it. Instead a short token is kept in the page URL
(``?c=...``), which survives F5, and consent flags plus merged chat
messages live in a small JSON store on the app host keyed by that token.
"""

from __future__ import annotations

import time
import uuid

import streamlit as st

from . import session_store

_LOADED_KEY = "browser_history_loaded"
_STATE_KEY = "browser_history"
_CLEARED_KEY = "browser_history_cleared_ts"
_TOKEN_PARAM = "c"
_TOKEN_SESSION = "_dl_token"
_MAX_CONTENT_CHARS = 2000
_MAX_RESTORE_CHARS = 60000


def _token() -> str:
    token = st.session_state.get(_TOKEN_SESSION)
    if isinstance(token, str) and token:
        return token
    token = st.query_params.get(_TOKEN_PARAM)
    if isinstance(token, str) and token:
        st.session_state[_TOKEN_SESSION] = token
        return token
    return ""


def _ensure_token() -> str:
    token = _token()
    if not token:
        token = uuid.uuid4().hex[:16]
    st.session_state[_TOKEN_SESSION] = token
    st.query_params[_TOKEN_PARAM] = token
    return token


def persist_token() -> None:
    """Re-apply the token query param; page navigation strips it."""
    token = st.session_state.get(_TOKEN_SESSION)
    if isinstance(token, str) and token and st.query_params.get(_TOKEN_PARAM) != token:
        st.query_params[_TOKEN_PARAM] = token


def _assign_message_ids() -> None:
    for message in st.session_state.get("chat_messages", []):
        if not message.get("mid"):
            message["mid"] = uuid.uuid4().hex[:12]
        if not message.get("ts"):
            message["ts"] = round(time.time(), 3)


def _serialize_messages() -> list[dict[str, object]]:
    cleared_ts = st.session_state.get(_CLEARED_KEY, 0)
    entries: list[dict[str, object]] = []
    for message in st.session_state.get("chat_messages", []):
        role = message.get("role")
        content = message.get("content")
        ts = message.get("ts") or 0
        if (
            role not in {"user", "assistant"}
            or not isinstance(content, str)
            or not content.strip()
            or ts < cleared_ts
        ):
            continue
        entry: dict[str, object] = {
            "mid": message.get("mid"),
            "ts": ts,
            "role": role,
            "content": content[:_MAX_CONTENT_CHARS],
            "mode": message.get("mode") or "",
            "blocked": bool(message.get("scope_blocked")),
        }
        if isinstance(message.get("speech_cpm"), (int, float)):
            entry["speech_cpm"] = message["speech_cpm"]
        if isinstance(message.get("vocal"), dict):
            entry["vocal"] = message["vocal"]
        entries.append(entry)
    return entries


def _restore_chat(entries: list[dict[str, object]]) -> None:
    if not entries or st.session_state.get("chat_messages"):
        return
    total = 0
    messages: list[dict[str, object]] = []
    user_turns = 0
    for entry in entries:
        content = entry["content"]
        if total + len(content) > _MAX_RESTORE_CHARS:
            break
        total += len(content)
        message: dict[str, object] = {
            "role": entry["role"],
            "content": content,
            "mid": entry["mid"],
            "ts": entry["ts"],
        }
        if entry.get("mode"):
            message["mode"] = entry["mode"]
        if isinstance(entry.get("speech_cpm"), (int, float)):
            message["speech_cpm"] = entry["speech_cpm"]
        if isinstance(entry.get("vocal"), dict):
            message["vocal"] = entry["vocal"]
        if entry.get("blocked"):
            message["scope_blocked"] = True
        elif entry["role"] == "user":
            user_turns += 1
        messages.append(message)
    st.session_state["chat_messages"] = messages
    st.session_state["user_turns"] = user_turns


def sync_browser_history() -> None:
    """Merge session messages into the token store; restore on first load."""
    st.session_state.setdefault("chat_messages", [])
    st.session_state.setdefault("user_turns", 0)
    _assign_message_ids()

    token = _ensure_token()
    stored = session_store.get_messages(token)
    seen = {m.get("mid") for m in stored if isinstance(m, dict)}
    merged = list(stored)
    for entry in _serialize_messages():
        if entry["mid"] not in seen:
            merged.append(entry)
            seen.add(entry["mid"])
    session_store.save_messages(token, merged)
    st.session_state[_STATE_KEY] = merged

    if st.session_state.get(_LOADED_KEY):
        return
    st.session_state[_LOADED_KEY] = True
    if merged and not st.session_state["chat_messages"]:
        _restore_chat(merged)
        st.rerun()


def get_browser_history() -> list[dict[str, object]]:
    entries = st.session_state.get(_STATE_KEY)
    return entries if isinstance(entries, list) else []


def clear_browser_history() -> None:
    session_store.save_messages(_token(), [])
    st.session_state[_STATE_KEY] = []
    st.session_state[_CLEARED_KEY] = time.time()


def read_consent_state() -> str:
    return "1" if session_store.has_consent(_token()) else ""


def set_consent_storage() -> None:
    session_store.set_consent(_ensure_token())


def clear_all_storage() -> None:
    session_store.clear_token(_token())
    if _TOKEN_PARAM in st.query_params:
        del st.query_params[_TOKEN_PARAM]
    st.session_state.pop(_TOKEN_SESSION, None)
    st.session_state[_STATE_KEY] = []
    st.session_state[_CLEARED_KEY] = time.time()
