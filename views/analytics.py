import streamlit as st
from components import data as D
from components.charts import bar_chart, scatter_chart
from components.style import page_header, section
from config import BAT_METRICS, BOWL_METRICS

COMPS = [D.ALL_COMP, "IPL", "T20I"]
SCATTER_X = {
    "batters": {"Pressure Strike Rate": ("pressure_strike_rate", "Strike rate under pressure"), "Pressure Runs": ("pressure_runs", "Runs under pressure"),
                "Pressure Average": ("pressure_average", "Average under pressure"), "Boundary %": ("pressure_boundary_pct", "Boundary share (%)")},
    "bowlers": {"Wickets Under Pressure": ("pressure_wickets", "Wickets under pressure"), "Wickets per Over": ("wickets_per_over_pressure", "Wickets per over"),
                "Control (dot-ball %)": ("control_dot_ball_pct", "Dot-ball share (%)"), "Boundary % conceded": ("pressure_boundary_pct", "Boundary share conceded (%)"),
                "Economy (approx.)": ("approx_economy_recorded_runs", "Approx. economy (recorded runs)")},
}


def _filters(group, ids, key):
    seasons, teams = D.filter_options(group, ids)
    c = st.columns(3)
    comp = c[0].selectbox("Competition", COMPS, key=f"comp_{key}")
    season = c[1].selectbox("Season", seasons, key=f"season_{key}")
    team = c[2].selectbox("Team", teams, key=f"team_{key}")
    return comp, season, team


def _section_bar(group, title, metrics, navy):
    section(title, navy=navy)
    base = D.players(group, "top10")
    comp, season, team = _filters(group, base.player_id.tolist(), f"bar_{group}")
    label = st.selectbox("Metric", list(metrics), key=f"metric_{group}")
    view = D.view_frame(group, base, comp, season, team)
    if not D.is_unfiltered(comp, season, team):
        st.caption("Filtered view: counts and rates are recomputed for the selection; rank and reliability score always stay overall.")
    st.plotly_chart(bar_chart(group, view, metrics[label], f"Top 10 {group} — {label}"), width="stretch", key=f"barchart_{group}")
    if group == "bowlers" and "Approx" in label:
        st.caption("Runs conceded use recorded runs only and are approximate.")


def render():
    page_header("Performance Analytics", "Compare the Top 10 across pressure metrics, then see how pressure performance relates to reliability.")
    _section_bar("batters", "Batting — Top 10", BAT_METRICS, False)
    _section_bar("bowlers", "Bowling — Top 10", BOWL_METRICS, True)

    section("Performance vs reliability")
    st.caption("One dot per eligible player. Large circles are the Top 10; the dotted lines mark the median of the plotted players. "
               "Top-right = strong pressure performance with high reliability.")
    grp_label = st.radio("Player category", ["Batters", "Bowlers"], horizontal=True, key="sc_group")
    group = "batters" if grp_label == "Batters" else "bowlers"
    elig = D.players(group, "eligible")
    top_ids = set(D.players(group, "top10").player_id)
    c = st.columns(4)
    x_label = c[0].selectbox("Performance metric (X)", list(SCATTER_X[group]), key=f"sc_x_{group}")
    seasons, teams = D.filter_options(group, elig.player_id.tolist())
    comp = c[1].selectbox("Competition", COMPS, key=f"sc_comp_{group}")
    season = c[2].selectbox("Season", seasons, key=f"sc_season_{group}")
    team = c[3].selectbox("Team", teams, key=f"sc_team_{group}")
    view = D.view_frame(group, elig, comp, season, team)
    x_col, x_title = SCATTER_X[group][x_label]
    st.plotly_chart(scatter_chart(group, view, x_col, x_title, top_ids), width="stretch", key=f"scatter_{group}")
    if not D.is_unfiltered(comp, season, team):
        st.caption("Y-axis reliability score is the overall score; only the X metric responds to the filters.")
    if group == "bowlers" and "approx" in x_col:
        st.caption("Economy uses recorded runs only and is approximate.")
