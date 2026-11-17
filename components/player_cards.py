"""Spotlight cards for good performers ranked outside the Top 10."""
import pandas as pd
import streamlit as st
from components import data as D
from components.style import avatar_uri, section

FMT = {"reliability_score": "{:.1f}", "consistency_success_rate_adjusted": "{:.0%}", "pressure_strike_rate": "{:.1f}",
       "pressure_average": "{:.1f}", "control_dot_ball_pct": "{:.1f}%", "wickets_per_over_pressure": "{:.2f} /over"}
LABEL = {"reliability_score": "Reliability score", "consistency_success_rate_adjusted": "Adjusted consistency", "pressure_strike_rate": "Pressure strike rate",
         "pressure_average": "Pressure average", "control_dot_ball_pct": "Dot-ball control", "wickets_per_over_pressure": "Wickets per over"}


def spotlight(group: str):
    sp = D.load("spotlight")
    top10 = D.players(group, "top10")
    elig = D.players(group, "eligible")
    if sp is None or elig.empty:
        st.info("Spotlight data is not available.")
        return
    sp = sp[(sp.group == group)]
    sp = sp[~sp.player_id.isin(top10.player_id)].drop_duplicates("player_id")  # never repeat a Top 10 player
    if sp.empty:
        st.info("No eligible players outside the Top 10 were found for spotlight cards.")
        return
    cls = "" if group == "batters" else "navy"
    cols = st.columns(len(sp))
    info = elig.set_index("player_id")
    for col, r in zip(cols, sp.itertuples()):
        team = D.primary_team(info.loc[r.player_id, "teams"]) if r.player_id in info.index else "—"
        val = FMT.get(r.metric, "{:.2f}").format(r.metric_value)
        col.markdown(
            f'<div class="spot {cls}"><div class="cat">{r.category}</div>'
            f'<div style="display:flex;gap:.6rem;align-items:center;margin:.5rem 0"><img src="{avatar_uri(r.player_name, group)}"/>'
            f'<div><div class="nm">{r.player_name}</div><div class="note">{team} · ranked #{int(r.rank)} overall</div></div></div>'
            f'<div class="mv">{val}</div><div class="note">{LABEL.get(r.metric, r.metric)}</div>'
            f'<div class="tx">{r.note}</div><div class="note" style="margin-top:.3rem">Reliability score: <b>{r.reliability_score:.1f}</b></div></div>',
            unsafe_allow_html=True)
