"""Data access layer. Ranking sheets are the source of truth; nothing here re-ranks players."""
import numpy as np
import pandas as pd
import streamlit as st
from config import DATA_DIR, FILES, REQUIRED

ALL_COMP, ALL_SEASON, ALL_TEAM = "Overall", "All seasons", "All teams"


@st.cache_data(show_spinner=False)
def load(key: str):
    path = DATA_DIR / FILES[key]
    if not path.exists():
        return None
    return pd.read_csv(path)


def validate_data():
    """Return a list of human-readable problems (empty list = all good)."""
    problems = []
    for key, cols in REQUIRED.items():
        fname = FILES.get(key)
        df = load(key) if key in FILES else None
        if df is None:
            problems.append(f"Missing file: data/{fname}")
            continue
        missing = [c for c in cols if c not in df.columns]
        if missing:
            problems.append(f"data/{fname} is missing columns: {', '.join(missing)}")
        if "player_id" in df.columns and key.startswith("top") and df.player_id.duplicated().any():
            problems.append(f"data/{fname} contains duplicate player_id values")
    return problems


def players(group: str, level: str) -> pd.DataFrame:
    """level: 'top10' | 'top25' | 'eligible'. Returns a copy ordered by rank."""
    df = load(f"{level}_{group}")
    if df is None:
        return pd.DataFrame()
    return df.sort_values("rank").reset_index(drop=True).copy()


def primary_team(teams: str) -> str:
    return str(teams).split(" / ")[0] if isinstance(teams, str) and teams else "—"


def filter_options(group: str, ids):
    b = load("breakdown")
    if b is None:
        return [ALL_SEASON], [ALL_TEAM]
    b = b[(b.group == group) & b.player_id.isin(ids)]
    seasons = [ALL_SEASON] + sorted(int(s) for s in b.season.unique())
    teams = [ALL_TEAM] + sorted(b.team.dropna().unique())
    return seasons, teams


def is_unfiltered(comp, season, team):
    return comp == ALL_COMP and season == ALL_SEASON and team == ALL_TEAM


def _recompute(group: str, ids, comp, season, team) -> pd.DataFrame:
    b = load("breakdown")
    b = b[(b.group == group) & b.player_id.isin(ids)]
    if comp != ALL_COMP:
        b = b[b.competition == comp]
    if season != ALL_SEASON:
        b = b[b.season == season]
    if team != ALL_TEAM:
        b = b[b.team == team]
    if b.empty:
        return pd.DataFrame()
    if group == "batters":
        g = b.groupby("player_id").agg(pressure_balls_faced=("pressure_balls", "sum"), pressure_runs=("runs", "sum"),
                                       pressure_dismissals=("dismissals", "sum"), pressure_boundaries=("boundaries", "sum"),
                                       dots=("dots", "sum"), pressure_matches=("matches", "sum"))
        g["pressure_strike_rate"] = g.pressure_runs / g.pressure_balls_faced * 100
        g["pressure_average"] = g.pressure_runs / g.pressure_dismissals.replace(0, np.nan)
        g["pressure_boundary_pct"] = g.pressure_boundaries / g.pressure_balls_faced * 100
        g["pressure_dot_pct"] = g.dots / g.pressure_balls_faced * 100
    else:
        g = b.groupby("player_id").agg(pressure_legal_balls=("pressure_balls", "sum"), pressure_wickets=("wickets", "sum"),
                                       pressure_boundaries_conceded=("boundaries", "sum"), dots=("dots", "sum"),
                                       approx_runs_conceded_recorded=("runs_recorded", "sum"), pressure_matches=("matches", "sum"))
        g["wickets_per_over_pressure"] = g.pressure_wickets / g.pressure_legal_balls * 6
        g["control_dot_ball_pct"] = g.dots / g.pressure_legal_balls * 100
        g["pressure_boundary_pct"] = g.pressure_boundaries_conceded / g.pressure_legal_balls * 100
        g["approx_economy_recorded_runs"] = g.approx_runs_conceded_recorded / g.pressure_legal_balls * 6
    return g.drop(columns=["dots"]).reset_index()


def view_frame(group: str, base: pd.DataFrame, comp=ALL_COMP, season=ALL_SEASON, team=ALL_TEAM) -> pd.DataFrame:
    """Players with metrics for the chosen filters. With no filter the ranking-sheet values are used unchanged.
    With a filter, count-based metrics are recomputed from the breakdown file; rank and reliability score stay overall."""
    if base.empty or is_unfiltered(comp, season, team):
        return base.copy()
    rc = _recompute(group, base.player_id.tolist(), comp, season, team)
    if rc.empty:
        return pd.DataFrame(columns=base.columns)
    keep = [c for c in base.columns if c not in rc.columns or c == "player_id"]
    return base[keep].merge(rc, on="player_id", how="inner")
