import streamlit as st
from config import NAV


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown('<div class="brand"><div class="b1">Supe<span>RR</span> Selector</div>'
                    '<div class="b2">Season 2 · Round 1 · Pressure reliability</div></div>', unsafe_allow_html=True)
        page = st.radio("Navigate", NAV, key="nav", label_visibility="collapsed")
        st.markdown("---")
        st.caption("IPL + T20I ball-by-ball data, 2022–2026. 837 matches, 194,014 deliveries. "
                   "Rankings come from the project analysis files and are shown unchanged.")
        st.caption("Rajasthan Royals–inspired visual identity. No official logo or player photographs are bundled.")
    return page
