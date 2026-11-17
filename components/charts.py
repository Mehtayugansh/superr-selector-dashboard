"""Plotly charts: sortable horizontal bars and the performance-vs-reliability scatter."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import PINK, NAVY, SOFT, GROUP_COLOR, GROUP_TINT, MUTED

LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Helvetica, Arial, sans-serif", color=NAVY, size=12),
              margin=dict(l=10, r=20, t=40, b=10))


def empty_fig(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False, font=dict(size=14, color=MUTED))
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False)
    fig.update_layout(height=260, **LAYOUT)
    return fig


def _hover(group, df):
    if group == "batters":
        return ("<b>%{y}</b><br>Rank #%{customdata[0]} · %{customdata[1]}<br>Reliability: %{customdata[2]:.1f}<br>Runs: %{customdata[3]:,.0f} · SR: %{customdata[4]:.1f}<br>"
                "Matches: %{customdata[5]:.0f}<extra></extra>"), df[["rank", "teams", "reliability_score", "pressure_runs", "pressure_strike_rate", "pressure_matches"]]
    return ("<b>%{y}</b><br>Rank #%{customdata[0]} · %{customdata[1]}<br>Reliability: %{customdata[2]:.1f}<br>Wickets: %{customdata[3]:.0f} · Dot %: %{customdata[4]:.1f}<br>"
            "Matches: %{customdata[5]:.0f}<extra></extra>"), df[["rank", "teams", "reliability_score", "pressure_wickets", "control_dot_ball_pct", "pressure_matches"]]


def bar_chart(group: str, df: pd.DataFrame, metric: tuple, title: str) -> go.Figure:
    col, fmt, axis_title = metric
    if df.empty or col not in df.columns:
        return empty_fig("No players have data for the selected filters.")
    d = df.dropna(subset=[col]).copy()
    if d.empty:
        return empty_fig("This metric is not available for the selected players (e.g. no dismissals for an average).")
    d = d.sort_values(col, ascending=True)  # horizontal bars: largest ends up on top
    hover, cd = _hover(group, d)
    fig = go.Figure(go.Bar(x=d[col], y=d.player_name, orientation="h", marker=dict(color=GROUP_COLOR[group], line=dict(width=0)),
                           text=d[col], texttemplate="%{text:" + fmt + "}", textposition="outside", cliponaxis=False,
                           customdata=cd.values, hovertemplate=hover))
    rng = None
    if col == "reliability_score":
        lo = max(0, np.floor(d[col].min() - 4)); rng = [lo, 100.6]
    else:
        rng = [0, d[col].max() * 1.15 if d[col].max() > 0 else 1]
    fig.update_xaxes(title=axis_title, range=rng, gridcolor="#E3E7F0", zeroline=False)
    fig.update_yaxes(title=None, tickfont=dict(size=12), automargin=True)
    fig.update_layout(title=dict(text=title, font=dict(size=15)), height=max(300, 42 * len(d) + 110), bargap=.32, **LAYOUT)
    if col == "reliability_score":
        fig.add_annotation(text=f"Axis starts at {rng[0]:.0f} to show differences between close scores", xref="paper", yref="paper", x=1, y=-0.16,
                           showarrow=False, font=dict(size=10, color=MUTED), xanchor="right")
    return fig


def scatter_chart(group: str, df: pd.DataFrame, x_col: str, x_title: str, top_ids: set) -> go.Figure:
    if df.empty or x_col not in df.columns or df[x_col].notna().sum() < 2:
        return empty_fig("Not enough players with data for the selected filters.")
    d = df.dropna(subset=[x_col]).copy()
    d["tier"] = np.where(d.player_id.isin(top_ids), "Top 10", "Other eligible")
    color, tint = GROUP_COLOR[group], GROUP_TINT[group]
    fig = go.Figure()
    for tier, c, size, op in [("Other eligible", tint, 9, .75), ("Top 10", color, 13, 1)]:
        s = d[d.tier == tier]
        if s.empty:
            continue
        fig.add_trace(go.Scatter(x=s[x_col], y=s.reliability_score, mode="markers", name=tier,
                                 marker=dict(color=c, size=size, opacity=op, line=dict(color="white", width=1.2)),
                                 customdata=np.c_[s.player_name, s["rank"], s.teams.fillna("—").map(lambda t: str(t).split(" / ")[0]), s.pressure_matches, s[x_col], s.reliability_score],
                                 hovertemplate="<b>%{customdata[0]}</b><br>Rank #%{customdata[1]} · %{customdata[2]}<br>Matches under pressure: %{customdata[3]:.0f}<br>"
                                               + x_title + ": %{customdata[4]:.2f}<br>Reliability: %{customdata[5]:.1f}<extra></extra>"))
    top = d[d.tier == "Top 10"]
    fig.add_trace(go.Scatter(x=top[x_col], y=top.reliability_score, mode="text", text=top.player_name.map(lambda n: n.split()[-1]),
                             textposition="top center", textfont=dict(size=10, color=color), showlegend=False, hoverinfo="skip"))
    fig.add_vline(x=float(d[x_col].median()), line=dict(color=MUTED, dash="dot", width=1))
    fig.add_hline(y=float(d.reliability_score.median()), line=dict(color=MUTED, dash="dot", width=1))
    fig.update_xaxes(title=x_title, gridcolor="#E3E7F0", zeroline=False)
    fig.update_yaxes(title="Reliability score", gridcolor="#E3E7F0", zeroline=False)
    fig.update_layout(height=520, legend=dict(orientation="h", y=1.08, x=0), **LAYOUT)
    return fig
