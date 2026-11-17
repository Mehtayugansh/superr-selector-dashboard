import pandas as pd
import streamlit as st
from components import data as D
from components.style import page_header, section
from config import PDF_FILE

V = '<span class="badge b-val">VALIDATED</span>'
P = '<span class="badge b-prov">PROVISIONAL</span>'
L = '<span class="badge b-lim">LIMITATION</span>'


def _item(badge, text):
    st.markdown(f"{badge} {text}", unsafe_allow_html=True)


def render():
    page_header("Methodology", "How pressure was defined, how players were scored and what the data can and cannot support.")
    if PDF_FILE.exists():
        st.download_button("⬇ Download full methodology report (PDF)", PDF_FILE.read_bytes(), file_name=PDF_FILE.name, mime="application/pdf")
    else:
        st.warning("The methodology PDF is not in the data folder.")
    st.markdown("**Legend:** " + V + " checked against the data · " + P + " analyst judgement, tested for sensitivity but not fitted to outcomes · " + L + " known gap", unsafe_allow_html=True)

    with st.expander("1. Objective and data coverage", expanded=True):
        st.write("Identify the 10 most reliable batters and 10 most reliable bowlers under pressure, using IPL and T20I ball-by-ball data from 2022 onward, "
                 "for Rajasthan Royals' IPL 2027 auction planning. Reliability means strong performance in demanding match states, supported by an adequate sample and repeatability across matches.")
        _item(V, "837 matches (367 IPL, 470 T20I) and 194,014 deliveries after filtering the source's 883 matches. Two A-team tournaments (Emerging Teams Asia Cup 2024, Asia Cup Rising Stars 2025) were excluded; 16 abandoned matches have no ball data; 38 Super Over deliveries are excluded from scoring.")
    with st.expander("2. Data preparation"):
        _item(V, "Legal ball = not a wide, 'Overstep' or 'other' delivery. 99.99% of complete overs have exactly 6 legal balls under this rule.")
        _item(V, "Revised-overs columns are in balls (e.g. 66 = 11 overs); innings length uses them, and the revised target is used for shortened chases.")
        _item(V, "Bowler wickets = Bowled, Caught, LBW, Stump, Hit Wicket only. Run-outs, retire-outs and obstruction are not credited to bowlers. 12 records with a dismissed player but no wicket flag were not counted.")
        _item(L, "Bye and leg-bye runs are not recorded and wide-running runs are missing, so exact team totals, required run rate and bowler economy cannot be rebuilt.")
        cal = D.load("calibration")
        if cal is not None:
            c = cal.set_index("check").value
            _item(V, f"Team runs are <i>estimated</i> for the chase target only (bat runs + penalties + fitted bye/leg-bye averages). Against 'won by N runs' margins (n={int(c['n margin matches'])}): mean error {c['mean error (runs)']:+.1f}, SD {c['SD error']:.1f}, MAE {c['MAE']:.1f} runs.")
    with st.expander("3. Pressure identification framework"):
        st.write("Pressure is a ball-by-ball measure computed **before** each delivery from information available at that moment (no look-ahead). "
                 "Batting and bowling pressure are scored separately. A delivery counts as high pressure if its score is in the top 15% of all deliveries and the match is not already decided (runs required ≤ 0 or required rate ≥ 18).")
        _item(V, "The provisional v2 model was replaced because it behaved as a late-innings proxy (correlation with over number 0.93 batting / 0.96 bowling; at least 92% of high-pressure balls in overs 16–20). The final v3 model reduces this to 0.77 / 0.37.")
        _item(P, "Component weights and the 85th-percentile cut-off are analyst-set. Ranking overlap under 10% / 20% bands is only 5–7 of 10 names, so the pressure definition is the most influential assumption.")
    with st.expander("4. Batting pressure model"):
        st.markdown("`Innings 1: 0.40·W + 0.35·I + 0.25·K`  \n`Innings 2: 0.30·W + 0.20·I + 0.20·K + 0.30·C`")
        st.caption("W wickets lost ×10 · I legal balls used ÷ innings length ×100 · K wickets in previous 12 legal balls (capped at 3) · C chase demand from required rate (6→12 maps to 0→100).")
    with st.expander("5. Bowling pressure model"):
        st.markdown("`Innings 1: 0.40·I + 0.30·B + 0.30·T`  \n`Innings 2: 0.30·I + 0.25·B + 0.20·T + 0.25·L`")
        st.caption("B boundary share of previous 12 legal balls (50% = 100) · T wickets in hand ×10 · L chase closeness (tight chases score higher). Windows exclude the current delivery.")
    with st.expander("6. Performance metrics"):
        st.write("**Batters:** strike rate, dismissal frequency, boundary share, dot-ball share, match consistency (weights 0.30 / 0.25 / 0.15 / 0.10 / 0.20). "
                 "**Bowlers:** wicket-taking rate, boundary prevention, dot-ball control, match consistency (weights 0.30 / 0.25 / 0.20 / 0.25). "
                 "Each rate is an index versus the IPL or T20I high-pressure baseline for the balls actually faced or bowled, which keeps competitions comparable.")
        _item(P, "Weights are analyst-set. Equal weights, no-consistency and consistency-heavy variants change at most 3 of the 10 names in either list.")
        _item(L, "Economy is not a ranking metric. The approximate economy and runs conceded shown for bowlers use recorded runs only.")
    with st.expander("7. Reliability calculation and sample-size adjustment"):
        st.markdown("`Adjusted = n/(n+k) × PlayerIndex + k/(n+k) × 1`, where n is high-pressure balls and k the prior sample equivalent. "
                    "Adjusted components are standardised, weighted, re-standardised and mapped to 0–100 with the normal CDF (a percentile-style position among eligible players).")
        _item(V, "k is estimated per metric and per discipline with an empirical-Bayes method-of-moments, not assumed equal for batting and bowling.")
        par = D.load("params")
        if par is not None:
            k = par[par.parameter.str.startswith("shrinkage k")].copy()
            k["metric"] = k.parameter.str.extract(r"\((.*)\)")
            st.dataframe(k.pivot(index="metric", columns="group", values="value").reset_index(), hide_index=True, width="content")
        _item(P, "Eligibility is ≥50 high-pressure balls and ≥5 matches (132 batters, 167 bowlers). Chosen from the sample distribution; alternatives were tested.")
    with st.expander("8. Match-to-match consistency"):
        st.write("A qualifying match has ≥3 high-pressure balls faced (batters) or ≥4 legal balls bowled (bowlers). "
                 "A batter succeeds if he scores at or above the pool baseline for his balls and is not dismissed; a bowler succeeds if he takes a wicket or beats the pool baseline on both boundary and dot-ball share. "
                 "The success rate is shrunk toward the pool-wide rate.")
        _item(P, "These success definitions are judgement calls.")
    with st.expander("9. Ranking methodology and sensitivity"):
        st.write("Players are ranked by reliability score. 'Core' players stay in the Top 10 in at least 9 of 13 alternative scenarios; 'Moderate' in 6–8; 'Sensitive' in 5 or fewer.")
        sens = D.load("sensitivity")
        if sens is not None:
            s = sens.rename(columns={"group": "Group", "scenario": "Scenario", "eligible": "Eligible", "top10_overlap_with_baseline": "Top-10 names retained",
                                     "baseline_top10_still_in_top15": "Still in top 15"})
            st.dataframe(s[["Group", "Scenario", "Eligible", "Top-10 names retained", "Still in top 15"]], hide_index=True, width="stretch")
    with st.expander("10. Data limitations"):
        for t in ["Even eligible players have 50–358 high-pressure balls (batters) and 50–684 (bowlers); shrinkage reduces but cannot remove small-sample uncertainty.",
                  "Baselines are by competition, not by role, venue or opposition quality.",
                  "Role labels are derived from batting order and bowling style, not an official role field.",
                  "Competition, season and team filters in this dashboard recompute counts and rates, but rank and reliability score stay overall.",
                  "Players are represented only through high-pressure balls in IPL 2022–26 and T20Is since 2022.",
                  "No official logo or player photographs are bundled; initials avatars are used so no player is misidentified."]:
            _item(L, t)
    dq = D.load("dq")
    if dq is not None:
        section("Data-quality decisions log")
        st.dataframe(dq.rename(columns={"issue": "Issue", "decision": "Decision", "effect": "Effect"}), hide_index=True, width="stretch")
