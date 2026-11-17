"""Global CSS and small HTML/SVG helpers (avatars, badges)."""
import base64
from urllib.parse import quote
import streamlit as st
from config import PINK, NAVY, SOFT, BG

CSS = f"""
<style>
:root {{ --pink:{PINK}; --navy:{NAVY}; --soft:{SOFT}; --bg:{BG}; }}
.stApp {{ background:{BG}; }}
.block-container {{ padding-top:1.4rem; padding-bottom:3rem; max-width:1280px; }}
h1,h2,h3,h4 {{ color:{NAVY}; letter-spacing:-0.01em; }}
section[data-testid="stSidebar"] {{ background:{NAVY}; }}
section[data-testid="stSidebar"] * {{ color:#F4F6FA; }}
section[data-testid="stSidebar"] [role="radiogroup"] label {{ padding:.45rem .6rem; border-radius:10px; margin-bottom:2px; }}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{ background:{PINK}; }}
section[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {{ display:none; }}
.brand {{ padding:.2rem 0 1rem 0; border-bottom:1px solid rgba(255,255,255,.15); margin-bottom:1rem; }}
.brand .b1 {{ font-weight:800; font-size:1.35rem; letter-spacing:.02em; }}
.brand .b1 span {{ color:{SOFT}; }}
.brand .b2 {{ font-size:.72rem; opacity:.75; text-transform:uppercase; letter-spacing:.12em; }}
.page-title {{ font-size:1.9rem; font-weight:800; color:{NAVY}; margin:0; }}
.page-sub {{ color:#5B6784; margin:.1rem 0 1.1rem 0; font-size:.95rem; }}
.card {{ background:#fff; border:1px solid #E3E7F0; border-radius:16px; padding:1rem 1.1rem; box-shadow:0 2px 8px rgba(23,43,85,.06); }}
.kpi {{ background:#fff; border:1px solid #E3E7F0; border-radius:14px; padding:.8rem 1rem; box-shadow:0 2px 8px rgba(23,43,85,.05); }}
.kpi .l {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; color:#6A7690; }}
.kpi .v {{ font-size:1.55rem; font-weight:800; color:{NAVY}; line-height:1.2; }}
.kpi .s {{ font-size:.75rem; color:#6A7690; }}
.sec {{ font-size:1.2rem; font-weight:800; color:{NAVY}; margin:1.2rem 0 .2rem 0; display:flex; align-items:center; gap:.5rem; }}
.sec:before {{ content:""; width:6px; height:1.1rem; border-radius:3px; background:{PINK}; display:inline-block; }}
.sec.navy:before {{ background:{NAVY}; }}
.note {{ color:#5B6784; font-size:.82rem; }}
.badge {{ display:inline-block; font-size:.68rem; font-weight:700; padding:.12rem .5rem; border-radius:999px; letter-spacing:.04em; }}
.b-core {{ background:#DDF3E6; color:#1B6B3A; }} .b-mod {{ background:#FFF1CF; color:#8A6100; }} .b-sens {{ background:#FBE0E0; color:#9B2C2C; }}
.b-val {{ background:#DDF3E6; color:#1B6B3A; }} .b-prov {{ background:#FFF1CF; color:#8A6100; }} .b-lim {{ background:#E7EAF3; color:{NAVY}; }}
.spot {{ background:#fff; border:1px solid #E3E7F0; border-radius:16px; padding:.9rem 1rem; box-shadow:0 2px 8px rgba(23,43,85,.06); height:100%; border-top:4px solid {PINK}; }}
.spot.navy {{ border-top-color:{NAVY}; }}
.spot .cat {{ font-size:.68rem; text-transform:uppercase; letter-spacing:.09em; color:#6A7690; font-weight:700; }}
.spot .nm {{ font-weight:800; color:{NAVY}; font-size:1.02rem; }}
.spot .mv {{ font-size:1.5rem; font-weight:800; color:{PINK}; line-height:1.1; }}
.spot.navy .mv {{ color:{NAVY}; }}
.spot .tx {{ font-size:.78rem; color:#4C5878; margin-top:.35rem; }}
.spot img {{ width:46px; height:46px; border-radius:50%; }}
.tile {{ aspect-ratio:1/1; min-height:150px; border-radius:18px; padding:.7rem .6rem; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; position:relative; box-shadow:0 2px 8px rgba(23,43,85,.10); border:1px solid rgba(23,43,85,.08); }}
.tile.pk {{ background:linear-gradient(160deg,#FFFFFF 0%,#FBE3EE 100%); }}
.tile.nv {{ background:linear-gradient(160deg,#FFFFFF 0%,#E3E8F5 100%); }}
.tile.top {{ border:2px solid {PINK}; }}
.tile .rk {{ position:absolute; top:8px; left:10px; background:{NAVY}; color:#fff; font-weight:800; font-size:.78rem; border-radius:999px; padding:.05rem .55rem; }}
.tile.top .rk {{ background:{PINK}; }}
.tile img {{ width:58px; height:58px; border-radius:50%; margin:.9rem 0 .45rem 0; }}
.tile .nm {{ font-weight:800; color:{NAVY}; font-size:.92rem; line-height:1.15; padding:.1rem 0 .25rem 0; }}
.tile .sb {{ font-size:.72rem; color:#5B6784; padding-bottom:.15rem; }}
div[data-testid="stButton"] > button {{ border-radius:10px; }}
.legend-dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:5px; }}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def initials(name: str) -> str:
    parts = [p for p in str(name).replace(".", " ").split() if p]
    if not parts:
        return "?"
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


def avatar_uri(name: str, group: str = "batters") -> str:
    """Neutral initials avatar (no real photographs are used, so no player can be misidentified)."""
    bg, fg = (PINK, "#FFFFFF") if group == "batters" else (NAVY, "#FFFFFF")
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='50' fill='{bg}'/>"
           f"<circle cx='50' cy='50' r='46' fill='none' stroke='rgba(255,255,255,.35)' stroke-width='2'/>"
           f"<text x='50' y='62' font-family='Helvetica,Arial,sans-serif' font-size='34' font-weight='700' fill='{fg}' text-anchor='middle'>{initials(name)}</text></svg>")
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def stability_badge(label: str) -> str:
    cls = {"Core": "b-core", "Moderate": "b-mod"}.get(label, "b-sens")
    return f'<span class="badge {cls}">{label}</span>'


def page_header(title: str, sub: str):
    st.markdown(f'<p class="page-title">{title}</p><p class="page-sub">{sub}</p>', unsafe_allow_html=True)


def section(title: str, navy: bool = False):
    st.markdown(f'<div class="sec{" navy" if navy else ""}">{title}</div>', unsafe_allow_html=True)
