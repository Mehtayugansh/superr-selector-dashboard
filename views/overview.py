import streamlit as st
from components import data as D
from components.player_cards import spotlight
from components.style import page_header, section
from components.tables import leaderboard


def render():
    page_header("Overview", "The 10 most reliable batters and 10 most reliable bowlers under pressure — IPL and T20I, 2022 onward.")
    bat, bowl = D.players("batters", "top10"), D.players("bowlers", "top10")
    c = st.columns(4)
    for col, (l, v, s) in zip(c, [("Top-10 batters", f"{len(bat)}", "ranked by reliability score"), ("Top-10 bowlers", f"{len(bowl)}", "ranked by reliability score"),
                                  ("Eligible batters", f"{len(D.players('batters', 'eligible'))}", "≥50 pressure balls, ≥5 matches"),
                                  ("Eligible bowlers", f"{len(D.players('bowlers', 'eligible'))}", "≥50 pressure balls, ≥5 matches")]):
        col.markdown(f'<div class="kpi"><div class="l">{l}</div><div class="v">{v}</div><div class="s">{s}</div></div>', unsafe_allow_html=True)

    section("Top 10 batters under pressure")
    st.caption("Reliability score blends pressure strike rate, dismissal frequency, boundary share, dot-ball share and match-to-match consistency, adjusted for sample size. Click a column header to sort.")
    leaderboard("batters", bat, "bat", pool=D.players("batters", "eligible"))
    section("Top 10 bowlers under pressure", navy=True)
    st.caption("Reliability score blends wicket-taking rate, boundary prevention, dot-ball control and match-to-match consistency, adjusted for sample size.")
    leaderboard("bowlers", bowl, "bowl", pool=D.players("bowlers", "eligible"))

    section("Reliability spotlight — batters outside the Top 10")
    st.caption("Good pressure performers ranked 11–30. No Top 10 player is repeated here.")
    spotlight("batters")
    section("Reliability spotlight — bowlers outside the Top 10", navy=True)
    spotlight("bowlers")
