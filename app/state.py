"""Shared Streamlit helpers: per-browser-session pseudonymous id, DB handle, CSS."""
from pathlib import Path

import streamlit as st

from src.database.database import Database, new_session_id
from src.recommendations.recommendation_rules import DISCLAIMER

CSS = Path(__file__).parent / "styles" / "custom.css"


@st.cache_resource
def get_db() -> Database:
    return Database()


def session_id() -> str:
    if "sid" not in st.session_state:
        st.session_state["sid"] = new_session_id()
    return st.session_state["sid"]


def header(title: str, subtitle: str = ""):
    if CSS.exists():
        st.markdown(f"<style>{CSS.read_text()}</style>", unsafe_allow_html=True)
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def disclaimer():
    st.info(DISCLAIMER)


def safe_page_link(page: str, label: str, icon: str | None = None):
    try:
        if icon:
            st.page_link(page, label=label, icon=icon)
        else:
            st.page_link(page, label=label)
    except Exception:
        icon_str = f"{icon} " if icon else ""
        st.markdown(f"{icon_str}[{label}]({page})")

