"""Player profile dialog opened from the 5x5 grid."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from components import data as D
from components.charts import LAYOUT, empty_fig
from components.style import avatar_uri, stability_badge
from config import GROUP_COLOR, GROUP_TINT, MUTED, NAVY, PINK


def _kpi(col, label, value, sub=""):
    col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div><div class="s">{sub}</div></div>', unsafe_allow_html=True)


def _num(v, fmt="{:,.1f}", na="n/a"):
    return na if v is None or (isinstance(v, float) and np.isnan(v)) else fmt.format(v)


def _pool_baselines(group):
    p = D.load("params")
    out = {}
    if p is None:
        return out
    p = p[p.group == group]
    for r in p.itertuples():
        if r.parameter.startswith("baseline ") and "(" in r.parameter:
            name, pool = r.parameter[9:].rsplit(" (", 1)
            out[(name.replace(" per ball", "").strip(), pool.rstrip(")"))] = r.value
    return out


def _warnings(group, r):
    w = []
    if r.ranking_stability != "Core":
        w.append(f"Ranking stability is <b>{r.ranking_stability}</b>: top 10 in {int(r.scenarios_in_top10)} of {int(r.scenarios_tested)} alternative scenarios tested.")
    balls = r.pressure_balls_faced if group == "batters" else r.pressure_legal_balls
    if balls < 100:
        w.append(f"Smaller sample: {int(balls)} high-pressure balls. Scores are shrunk toward the baseline, but uncertainty is larger.")
    if group == "batters" and r.pressure_dismissals < 5:
        w.append(f"Only {int(r.pressure_dismissals)} dismissals, so the batting average is unstable.")
    if r.consistency_qualifying_matches < 15:
        w.append(f"Consistency rests on {int(r.consistency_qualifying_matches)} qualifying matches.")
    if r.pressure_balls_ipl == 0 or r.pressure_balls_t20i == 0:
        w.append("All pressure balls come from one competition type (IPL or T20I).")
    if group == "bowlers":
        w.append("Economy and runs conceded are approximate (bye, leg-bye and wide-running runs are not recorded) and are not part of the score.")
    return w


def _match_chart(group, pid):
    m = D.load("matches")
    m = m[(m.group == group) & (m.player_id == pid)].copy()
    if m.empty:
        return empty_fig("No match-level records available.")
    m["date"] = pd.to_datetime(m.match_date, format="%m/%d/%Y", errors="coerce")
    m = m.sort_values("date").reset_index(drop=True)
    m["label"] = m.date.dt.strftime("%d %b %y") + " · " + m.comp_name.str.replace(" ", "\u00a0")
    ycol = "runs" if group == "batters" else "wickets"
    colors = np.where(~m.qualifying, "#D5DAE6", np.where(m.success == 1, GROUP_COLOR[group], GROUP_TINT[group]))
    fig = go.Figure(go.Bar(x=np.arange(len(m)), y=m[ycol], marker_color=colors,
                           customdata=np.c_[m.label, m.balls, m.success, m.qualifying],
                           hovertemplate="%{customdata[0]}<br>" + ("Runs" if group == "batters" else "Wickets") + ": %{y}<br>Balls: %{customdata[1]}<br>"
                                         "Qualifying: %{customdata[3]} · Success: %{customdata[2]}<extra></extra>"))
    if group == "batters":
        fig.add_trace(go.Scatter(x=np.arange(len(m)), y=m.baseline_runs, mode="markers", name="Baseline runs for balls faced",
                                 marker=dict(symbol="line-ew-open", size=10, color=NAVY, line=dict(width=2)), hovertemplate="Baseline: %{y:.1f}<extra></extra>"))
    fig.update_xaxes(title="Matches in date order (strong = successful, pale = qualifying but not successful, grey = too few balls to qualify)", showticklabels=False)
    fig.update_yaxes(title="Runs under pressure" if group == "batters" else "Wickets under pressure", gridcolor="#E3E7F0")
    fig.update_layout(height=260, showlegend=group == "batters", legend=dict(orientation="h", y=1.15), bargap=.25, **LAYOUT)
    return fig


def _pool_table(group, pid, r):
    b = D.load("breakdown")
    b = b[(b.group == group) & (b.player_id == pid)]
    base = _pool_baselines(group)
    rows = []
    for comp, g in b.groupby("competition"):
        balls = g.pressure_balls.sum()
        if group == "batters":
            sr = g.runs.sum() / balls * 100
            rows.append({"Competition": comp, "High-pressure balls": int(balls), "Matches": int(g.matches.sum()), "Runs": int(g.runs.sum()),
                         "Strike rate": round(sr, 1), "Pool baseline SR": round(base.get(("runs", comp), np.nan) * 100, 1),
                         "Dismissals": int(g.dismissals.sum())})
        else:
            rows.append({"Competition": comp, "High-pressure balls": int(balls), "Matches": int(g.matches.sum()), "Wickets": int(g.wickets.sum()),
                         "Dot-ball %": round(g.dots.sum() / balls * 100, 1), "Pool baseline dot %": round(base.get(("dot", comp), np.nan) * 100, 1),
                         "Boundary %": round(g.boundaries.sum() / balls * 100, 1), "Pool baseline boundary %": round(base.get(("bnd", comp), np.nan) * 100, 1)})
    return pd.DataFrame(rows)


def _baseline_chart(group, r):
    if group == "batters":
        labels, mine, base = ["Strike rate"], [r.pressure_strike_rate], [r.baseline_strike_rate]
    else:
        labels = ["Wickets per over ×100", "Dot-ball %", "Boundary %"]
        mine = [r.wickets_per_over_pressure * 100, r.control_dot_ball_pct, r.pressure_boundary_pct]
        base = [r.baseline_wickets_per_over * 100, r.baseline_dot_pct, r.baseline_boundary_pct]
    fig = go.Figure()
    fig.add_bar(x=labels, y=base, name="Pool baseline (same balls, IPL/T20I mix)", marker_color="#C7CEDF", text=[f"{v:.1f}" for v in base], textposition="outside")
    fig.add_bar(x=labels, y=mine, name="Player", marker_color=GROUP_COLOR[group], text=[f"{v:.1f}" for v in mine], textposition="outside")
    fig.update_layout(barmode="group", height=260, legend=dict(orientation="h", y=1.18), **LAYOUT)
    fig.update_yaxes(gridcolor="#E3E7F0", rangemode="tozero")
    return fig


@st.dialog("Player profile", width="large")
def profile_dialog(group: str, player_id):
    df = D.players(group, "eligible")  # every ranked player (top 25 is a subset)
    sel = df[df.player_id == player_id]
    if sel.empty:
        st.error("This player could not be found in the ranking file.")
        return
    r = sel.iloc[0].copy()
    role = r.role_derived if pd.notna(r.get("role_derived")) else "n/a"
    extra = (f" · {r.batting_hand}" if group == "batters" and pd.notna(r.get("batting_hand")) else
             f" · {r.bowling_style}" if group == "bowlers" and pd.notna(r.get("bowling_style")) else "")
    h1, h2 = st.columns([1, 6])
    h1.markdown(f'<img src="{avatar_uri(r.player_name, group)}" style="width:84px;height:84px;border-radius:50%"/>', unsafe_allow_html=True)
    h2.markdown(f'<div style="font-size:1.5rem;font-weight:800;color:{NAVY}">{r.player_name}</div>'
                f'<div class="note">{r.teams}</div>'
                f'<div style="margin-top:.3rem"><span class="badge b-lim">Rank #{int(r["rank"])} · {"Batter" if group == "batters" else "Bowler"}</span> '
                f'<span class="badge b-lim">{role}{extra}</span> {stability_badge(r.ranking_stability)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="note" style="margin:.6rem 0">{r.why_qualifies}</div>', unsafe_allow_html=True)

    st.markdown("##### Reliability")
    c = st.columns(4)
    _kpi(c[0], "Reliability score", f"{r.reliability_score:.1f}", "0–100, among eligible players")
    _kpi(c[1], "Consistency (adjusted)", f"{r.consistency_success_rate_adjusted:.0%}", f"raw {r.consistency_success_rate_raw:.0%}")
    _kpi(c[2], "Qualifying matches", f"{int(r.consistency_successful_matches)} / {int(r.consistency_qualifying_matches)}", "successful / qualifying")
    balls = r.pressure_balls_faced if group == "batters" else r.pressure_legal_balls
    _kpi(c[3], "High-pressure balls", f"{int(balls):,}", f"{int(r.pressure_matches)} matches")

    st.markdown("##### Pressure performance")
    c = st.columns(4)
    if group == "batters":
        _kpi(c[0], "Runs under pressure", f"{int(r.pressure_runs):,}", f"{int(r.pressure_boundaries)} boundaries")
        _kpi(c[1], "Strike rate", _num(r.pressure_strike_rate), f"baseline {_num(r.baseline_strike_rate)}")
        _kpi(c[2], "Average", _num(r.pressure_average), f"{int(r.pressure_dismissals)} dismissals")
        _kpi(c[3], "Matches / opportunities", f"{int(r.pressure_matches)} / {int(r.pressure_balls_faced)}", "matches / balls faced")
    else:
        _kpi(c[0], "Wickets under pressure", f"{int(r.pressure_wickets)}", f"{_num(r.wickets_per_over_pressure, '{:.2f}')} per over")
        _kpi(c[1], "Runs conceded (approx.)", f"{int(r.approx_runs_conceded_recorded):,}", "recorded runs only")
        _kpi(c[2], "Economy (approx.)", _num(r.approx_economy_recorded_runs, "{:.2f}"), "informational")
        _kpi(c[3], "Control (dot-ball %)", f"{r.control_dot_ball_pct:.1f}%", f"boundary balls {r.pressure_boundary_pct:.1f}%")

    t1, t2, t3 = st.tabs(["Match-to-match", "Versus baseline", "IPL vs T20I"])
    with t1:
        st.plotly_chart(_match_chart(group, r.player_id), width="stretch", key=f"mm_{group}_{player_id}")
    with t2:
        st.plotly_chart(_baseline_chart(group, r), width="stretch", key=f"bl_{group}_{player_id}")
        st.caption("Baseline = pooled high-pressure rate in the same competition(s), weighted by this player's balls.")
    with t3:
        pt = _pool_table(group, r.player_id, r)
        if pt.empty:
            st.info("No competition breakdown available.")
        else:
            st.dataframe(pt, hide_index=True, width="stretch")
    warns = _warnings(group, r)
    if warns:
        st.markdown("##### Notes and limitations")
        for w in warns:
            st.markdown(f"- {w}", unsafe_allow_html=True)
