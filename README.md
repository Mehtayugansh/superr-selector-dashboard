# SupeRR Selector · Season 2 · Round 1 — Pressure Reliability Dashboard

Rajasthan Royals–inspired Streamlit dashboard for the Top 10 / Top 25 most reliable batters and bowlers under pressure
(IPL + T20I, 2022 onward). All numbers come from the project analysis files in `data/`; the app never re-ranks players.

## Run
```bash
cd supeRR_selector_dashboard
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Requires Python 3.9+ and Streamlit 1.37+ (needed for `st.dialog`). Tested with Streamlit 1.67, Plotly 7.1, pandas 2.x.

## Pages
1. **Overview** – separate Top 10 batter and bowler tables (sortable, searchable, CSV download), plus spotlight cards for players ranked 11–30 (never repeats a Top 10 player).
2. **Performance Analytics** – horizontal bar charts with metric selectors and competition / season / team filters; performance-vs-reliability scatter.
3. **Discover 25 Players** – 5×5 grid of tiles; "Open profile" opens a modal with reliability, pressure metrics, match-to-match chart, baseline comparison, IPL vs T20I split and limitations.
4. **Methodology** – validated vs provisional decisions, parameters, sensitivity results, data-quality log, PDF download.

## Data files (`data/`, copied unchanged from the analysis outputs)
| File | Used for |
|---|---|
| `top10_*.csv`, `top25_*.csv`, `eligible_*_ranked.csv` | Tables, grid, scatter (source of truth for ranks and scores) |
| `spotlight_candidates_outside_top10.csv` | Spotlight cards |
| `player_breakdown_competition_season_team.csv` | Competition / season / team filters, IPL vs T20I table |
| `player_match_level_pressure.csv` | Match-to-match chart in the profile |
| `model_parameters.csv`, `ranking_sensitivity_scenarios.csv`, `run_estimate_calibration.csv`, `data_quality_decisions.csv` | Methodology page |
| `SupeRR_Selector_Round1_Methodology.pdf` | Download button |

To refresh the dashboard, replace these files with new outputs that keep the same column names (`config.py` lists the required ones; the app reports missing files or columns on start-up).

## Things to know
- **Filters:** competition / season / team recompute counts and rates from the breakdown file. Rank and reliability score always stay overall.
- **Economy / runs conceded** are approximate (bye, leg-bye and wide-running runs are not recorded) and are not part of any score. "Control" = dot-ball share.
- **Role** is derived from batting order (batters) and bowling style (bowlers); it is not an official role field.
- **Images:** no official logo or player photographs are bundled. Initials avatars are used so that no player can be misidentified. Drop images into `assets/` and extend `components/style.py::avatar_uri` if you have licensed photos.
- The page modules are in `views/` (not `pages/`) so Streamlit does not add its own automatic navigation.

## Structure
```
app.py  config.py  requirements.txt
components/  data.py style.py sidebar.py tables.py charts.py player_cards.py player_grid.py player_profile.py
views/       overview.py analytics.py discover_players.py methodology.py
data/        analysis outputs      assets/  (empty; for logos/photos)
.streamlit/config.toml  (theme)
```
