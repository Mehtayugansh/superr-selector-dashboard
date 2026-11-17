"""SupeRR Selector Season 2 – Round 1 dashboard. Run with:  streamlit run app.py"""
import streamlit as st

st.set_page_config(page_title="SupeRR Selector · Pressure Reliability", page_icon="🏏", layout="wide", initial_sidebar_state="expanded")

from components import data as D
from components.sidebar import render_sidebar
from components.style import inject_css
from views import analytics, discover_players, methodology, overview

inject_css()
problems = D.validate_data()
if problems:
    st.error("The dashboard cannot start because of data problems:")
    for p in problems:
        st.markdown(f"- {p}")
    st.stop()

PAGES = {"Overview": overview.render, "Performance Analytics": analytics.render,
         "Discover 25 Players": discover_players.render, "Methodology": methodology.render}
PAGES[render_sidebar()]()
