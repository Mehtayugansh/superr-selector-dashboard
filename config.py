"""Central configuration: paths, colours and the mapping of dataset columns to dashboard fields."""
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

PINK, NAVY, SOFT, BG = "#C72C73", "#172B55", "#F4B8D0", "#F4F6FA"
MUTED = "#8A93A8"

FILES = {
    "top10_batters": "top10_batters.csv",
    "top10_bowlers": "top10_bowlers.csv",
    "top25_batters": "top25_batters.csv",
    "top25_bowlers": "top25_bowlers.csv",
    "eligible_batters": "eligible_batters_ranked.csv",
    "eligible_bowlers": "eligible_bowlers_ranked.csv",
    "spotlight": "spotlight_candidates_outside_top10.csv",
    "breakdown": "player_breakdown_competition_season_team.csv",
    "matches": "player_match_level_pressure.csv",
    "params": "model_parameters.csv",
    "sensitivity": "ranking_sensitivity_scenarios.csv",
    "stability": "ranking_player_stability.csv",
    "thresholds": "reliability_threshold_scenarios.csv",
    "calibration": "run_estimate_calibration.csv",
    "dq": "data_quality_decisions.csv",
}
PDF_FILE = DATA_DIR / "SupeRR_Selector_Round1_Methodology.pdf"

# Columns each ranking file must contain for the dashboard to render
REQUIRED = {
    "top10_batters": ["rank", "player_id", "player_name", "teams", "reliability_score", "pressure_runs",
                      "pressure_strike_rate", "pressure_average", "pressure_matches"],
    "top10_bowlers": ["rank", "player_id", "player_name", "teams", "reliability_score", "pressure_wickets",
                      "approx_runs_conceded_recorded", "control_dot_ball_pct", "pressure_matches"],
    "breakdown": ["group", "player_id", "competition", "season", "team", "pressure_balls", "matches"],
    "matches": ["group", "player_id", "match_id", "match_date", "balls", "success", "qualifying"],
}

# metric selectors: label -> (column, number format, axis title)
BAT_METRICS = {
    "Reliability Score": ("reliability_score", ".1f", "Reliability score (0–100)"),
    "Pressure Runs": ("pressure_runs", ",.0f", "Runs off the bat under pressure"),
    "Pressure Strike Rate": ("pressure_strike_rate", ".1f", "Strike rate under pressure"),
    "Pressure Average": ("pressure_average", ".1f", "Runs per dismissal under pressure"),
    "Pressure Matches": ("pressure_matches", ",.0f", "Matches with pressure balls"),
}
BOWL_METRICS = {
    "Reliability Score": ("reliability_score", ".1f", "Reliability score (0–100)"),
    "Wickets Under Pressure": ("pressure_wickets", ",.0f", "Bowler-credited wickets under pressure"),
    "Runs Conceded Under Pressure (approx.)": ("approx_runs_conceded_recorded", ",.0f", "Recorded runs conceded (approx.)"),
    "Control Under Pressure (dot-ball %)": ("control_dot_ball_pct", ".1f", "Dot-ball share under pressure (%)"),
    "Matches Under Pressure": ("pressure_matches", ",.0f", "Matches with pressure balls"),
}
GROUPS = {"Batters": "batters", "Bowlers": "bowlers"}
GROUP_COLOR = {"batters": PINK, "bowlers": NAVY}
GROUP_TINT = {"batters": SOFT, "bowlers": "#AEB9D6"}
NAV = ["Overview", "Performance Analytics", "Discover 25 Players", "Methodology"]
