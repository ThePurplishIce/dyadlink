from __future__ import annotations

from datetime import datetime
from html import escape

import streamlit as st

from modules.browser_history import (
    clear_browser_history,
    get_browser_history,
    sync_browser_history,
)
from modules.i18n import tr
from modules.ui import render_brand


def _group_by_date(
    entries: list[dict[str, object]],
) -> list[tuple[str, list[dict[str, object]]]]:
    groups: list[tuple[str, list[dict[str, object]]]] = []
    current_label: str | None = None
    for entry in entries:
        ts = entry.get("ts")
        if isinstance(ts, (int, float)) and ts > 0:
            label = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        else:
            label = tr("history_undated")
        if label != current_label:
            groups.append((label, []))
            current_label = label
        groups[-1][1].append(entry)
    return groups


def main() -> None:
    sync_browser_history()
    render_brand(tr("history_brand"))

    st.markdown(
        f'<h1 class="page-title">{tr("history_title")}</h1>'
        f'<p class="conversation-copy">{tr("history_intro")}</p>',
        unsafe_allow_html=True,
    )

    entries = get_browser_history()
    if not entries:
        st.info(tr("history_empty"))
    else:
        st.caption(tr("history_count", count=len(entries)))
        for date_label, day_entries in _group_by_date(entries):
            st.markdown(f"#### {date_label}")
            for entry in day_entries:
                ts = entry.get("ts")
                time_label = (
                    datetime.fromtimestamp(ts).strftime("%H:%M")
                    if isinstance(ts, (int, float)) and ts > 0
                    else ""
                )
                role_label = tr(
                    "history_you" if entry["role"] == "user" else "history_assistant"
                )
                st.markdown(
                    f'<div class="history-entry history-{entry["role"]}">'
                    f'<span class="history-meta">{escape(role_label)}'
                    f'{" · " + escape(time_label) if time_label else ""}</span>'
                    f'<span class="history-text">{escape(entry["content"])}</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button(
        tr("history_clear"),
        key="history_clear_button",
        disabled=not entries,
    ):
        clear_browser_history()
        st.session_state["history_notice"] = tr("history_cleared")
        st.rerun()
    notice = st.session_state.pop("history_notice", None)
    if notice:
        st.success(notice)


if __name__ == "__main__":
    main()
