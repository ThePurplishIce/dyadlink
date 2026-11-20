import streamlit as st

from modules.browser_history import persist_token
from modules.consent import render_consent_controls, render_required_consent
from modules.i18n import render_language_selector, tr
from modules.research_sidebar import render_research_sidebar
from modules.ui import render_global_styles


st.set_page_config(
    page_title="DyadLink",
    page_icon="D",
    layout="wide",
    initial_sidebar_state="collapsed",
)
render_global_styles()
render_required_consent()
persist_token()
render_language_selector()
render_consent_controls()
render_research_sidebar()

navigation = st.navigation(
    [
        st.Page(
            "modules/home.py",
            title=tr("nav_home"),
            icon=":material/chat:",
            default=True,
        ),
        st.Page(
            "modules/history.py",
            title=tr("nav_history"),
            icon=":material/history:",
        ),
        st.Page(
            "modules/dashboard.py",
            title=tr("nav_dashboard"),
            icon=":material/insights:",
        ),
    ],
    position="sidebar",
)
navigation.run()
