"""Leaderboard tables (separate batter / bowler tables, sortable, searchable, downloadable)."""
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.colors import LinearSegmentedColormap
from components.player_profile import profile_dialog
from config import PINK, NAVY, SOFT

PINK_CM = LinearSegmentedColormap.from_list("rrpink", ["#FFFFFF", "#F9D3E4"])
NAVY_CM = LinearSegmentedColormap.from_list("rrnavy", ["#FFFFFF", "#CBD4EC"])
GREY_CM = LinearSegmentedColormap.from_list("rrgrey", ["#FFFFFF", "#E3E7F0"])

BAT_TABLE = {  # source column -> display label, format, gradient direction
    "rank": ("Rank", "{:.0f}", None), "player_name": ("Player", "{}", None), "teams": ("Teams", "{}", None),
    "role_derived": ("Role (derived)", "{}", None), "reliability_score": ("Reliability", "{:.1f}", "hi"),
    "pressure_runs": ("Runs", "{:,.0f}", "hi"), "pressure_strike_rate": ("Strike rate", "{:.1f}", "hi"),
    "pressure_average": ("Average", "{:.1f}", "hi"), "pressure_balls_faced": ("Balls", "{:,.0f}", None),
    "pressure_dismissals": ("Dismissals", "{:.0f}", "lo"), "pressure_boundary_pct": ("Boundary %", "{:.1f}", "hi"),
    "pressure_matches": ("Matches", "{:.0f}", None), "consistency_success_rate_adjusted": ("Consistency", "{:.0%}", "hi"),
    "ranking_stability": ("Stability", "{}", None),
}
BOWL_TABLE = {
    "rank": ("Rank", "{:.0f}", None), "player_name": ("Player", "{}", None), "teams": ("Teams", "{}", None),
    "role_derived": ("Type", "{}", None), "reliability_score": ("Reliability", "{:.1f}", "hi"),
    "pressure_wickets": ("Wickets", "{:.0f}", "hi"), "approx_runs_conceded_recorded": ("Runs conceded*", "{:,.0f}", None),
    "approx_economy_recorded_runs": ("Economy*", "{:.2f}", "lo"), "control_dot_ball_pct": ("Control (dot %)", "{:.1f}", "hi"),
    "pressure_boundary_pct": ("Boundary %", "{:.1f}", "lo"), "wickets_per_over_pressure": ("Wkts / over", "{:.2f}", "hi"),
    "pressure_legal_balls": ("Balls", "{:,.0f}", None), "pressure_matches": ("Matches", "{:.0f}", None),
    "consistency_success_rate_adjusted": ("Consistency", "{:.0%}", "hi"), "ranking_stability": ("Stability", "{}", None),
}


def search_filter(df: pd.DataFrame, query: str) -> pd.DataFrame:
    q = (query or "").strip().lower()
    if not q or df.empty:
        return df
    mask = df.player_name.str.lower().str.contains(q, regex=False) | df.teams.fillna("").str.lower().str.contains(q, regex=False)
    return df[mask]


def _styler(df: pd.DataFrame, spec: dict, accent: str):
    cols = [c for c in spec if c in df.columns]
    show = df[cols].rename(columns={c: spec[c][0] for c in cols}).reset_index(drop=True)
    sty = show.style.format({spec[c][0]: spec[c][1] for c in cols if spec[c][1] != "{}"}, na_rep="n/a")
    cm = PINK_CM if accent == PINK else NAVY_CM
    for c in cols:
        label, _, d = spec[c]
        if d and show[label].notna().sum() > 1:
            sty = sty.background_gradient(subset=[label], cmap=cm if d == "hi" else GREY_CM, vmin=None, vmax=None)

    def top3(col):
        out = []
        for v in show["Rank"]:
            out.append(f"background-color:{accent};color:white;font-weight:800" if v <= 3 else "")
        return out
    sty = sty.apply(top3, subset=["Rank"]).apply(
        lambda col: [f"background-color:{SOFT if accent == PINK else '#D6DCEE'};font-weight:700;color:{NAVY}" if r <= 3 else "font-weight:600" for r in show["Rank"]],
        subset=["Player"])
    return show, sty


def leaderboard(group: str, df: pd.DataFrame, key: str, pool: pd.DataFrame = None):
    """Render the sortable table for one group. With no search text it shows `df` (the Top 10); a search looks across `pool`
    (all ranked, eligible players) so players outside the Top 10 can be found. Offers a CSV download of what is shown."""
    spec, accent = (BAT_TABLE, PINK) if group == "batters" else (BOWL_TABLE, NAVY)
    c1, c2 = st.columns([3, 1.2])
    query = c1.text_input("Search player or team", key=f"q_{key}", placeholder="Search any ranked player or team…", label_visibility="collapsed")
    searching = bool((query or "").strip()) and pool is not None and not pool.empty
    shown = search_filter(pool if searching else df, query)
    if shown.empty:
        st.info("No ranked player matches your search. Only eligible players (at least 50 high-pressure balls in at least 5 matches) are ranked.")
        return
    if searching:
        st.caption(f"Search results from all {len(pool)} ranked {group} (not just the Top 10). Rank shows overall position.")
    disp, sty = _styler(shown, spec, accent)
    height = 38 + 35 * len(disp)
    st.dataframe(sty, hide_index=True, width="stretch", height=min(height, 460),
                 column_config={"Teams": st.column_config.TextColumn(width="large"),
                                "Player": st.column_config.TextColumn(width="medium")})
    c2.download_button("⬇ Download CSV", shown.to_csv(index=False).encode(), file_name=f"{group}_search.csv" if searching else f"top10_{group}.csv",
                       mime="text/csv", key=f"dl_{key}", width="stretch")
    # open the full profile for any player currently shown (Top 10 or search results)
    p1, p2 = st.columns([3, 1.2])
    pick = p1.selectbox("Open full profile for", shown.player_id.tolist(), key=f"pick_{key}", label_visibility="collapsed",
                        format_func=lambda pid: f"#{int(shown.loc[shown.player_id == pid, 'rank'].iloc[0])}  {shown.loc[shown.player_id == pid, 'player_name'].iloc[0]}")
    if p2.button("Open profile", key=f"open_{key}", width="stretch"):
        profile_dialog(group, pick)
    if group == "bowlers":
        st.caption("*Runs conceded and economy use recorded runs only (bye, leg-bye and wide-running runs are not in the data), "
                   "so they are approximate and not part of the ranking. Control = dot-ball share.")
