import streamlit as st

from modules.i18n import tr
from modules.research_data import PAPER_CITATION, PAPER_DOI


def render_research_sidebar() -> None:
    with st.sidebar.expander(tr("about_research"), expanded=False):
        st.markdown(PAPER_CITATION)
        st.markdown(f"[{tr('paper_link')}]({PAPER_DOI})")
