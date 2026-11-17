import streamlit as st
from components.player_grid import player_grid
from components.style import page_header


def render():
    page_header("Discover 25 Players", "The Top 25 under pressure. Open any tile for a detailed profile.")
    choice = st.radio("Show", ["Batters", "Bowlers"], horizontal=True, key="grid_group")
    group = "batters" if choice == "Batters" else "bowlers"
    st.caption("Tile footer shows primary team and reliability score. Pink-bordered tiles are ranks 1–3.")
    player_grid(group)
