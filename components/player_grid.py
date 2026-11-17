"""Responsive 5x5 grid of player tiles. Each tile has an 'Open profile' button that opens a modal."""
import streamlit as st
from components import data as D
from components.style import avatar_uri
from components.player_profile import profile_dialog


def player_grid(group: str, ncols: int = 5):
    df = D.players(group, "top25").head(25)
    if df.empty:
        st.error("Top 25 data is unavailable.")
        return
    rows = [df.iloc[i:i + ncols] for i in range(0, len(df), ncols)]
    for ri, chunk in enumerate(rows):
        cols = st.columns(ncols, gap="small")
        for ci in range(ncols):
            if ci >= len(chunk):
                continue
            r = chunk.iloc[ci]
            variant = "pk" if (ri + ci) % 2 == 0 else "nv"
            top = " top" if int(r["rank"]) <= 3 else ""
            with cols[ci]:
                st.markdown(
                    f'<div class="tile {variant}{top}"><span class="rk">#{int(r["rank"])}</span>'
                    f'<img src="{avatar_uri(r.player_name, group)}"/><div class="nm">{r.player_name}</div>'
                    f'<div class="sb">{D.primary_team(r.teams)} · {r.reliability_score:.1f}</div></div>', unsafe_allow_html=True)
                if st.button("Open profile", key=f"tile_{group}_{r.player_id}", width="stretch"):
                    profile_dialog(group, r.player_id)
