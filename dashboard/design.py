"""Premium, accessible, offline-first V2 visual system (team tokens from blueprint).
Decorative insignias are ORIGINAL monogram illustrations—not official IPL/team logos.
"""
from pathlib import Path
import base64
import html
import json
import streamlit as st
from dashboard.official_brand import official_logo_url, local_logo_file
ROOT=Path(__file__).resolve().parents[1]
TOKENS=json.loads((ROOT/'assets/team_theme_tokens.json').read_text())
NEUTRAL=TOKENS['neutral']

def palette(code=None):
    return TOKENS.get('teams',{}).get(code,NEUTRAL)

def safe(s):return html.escape(str(s),quote=True)

def svg_uri(path:Path)->str:
    return 'data:image/svg+xml;base64,'+base64.b64encode(path.read_bytes()).decode('ascii')

def inject_theme(code=None):
    t=palette(code); accent=t['primary']; highlight=t['accent']; dark=t['hero_gradient'][0]
    st.markdown(f'''<style>
:root {{ --ipl-accent:{accent}; --ipl-highlight:{highlight}; --ipl-tint:{dark}; --ipl-ink:#F0F6FF; --ipl-sub:#9DAFC7; }}
html, body, [data-testid="stAppViewContainer"] {{background: #080F1D !important;color:#E9F2FF;}}
[data-testid="stAppViewContainer"] > .main {{background:radial-gradient(ellipse at 94% 5%, {accent}1B 0%, transparent 33%),radial-gradient(ellipse at 8% 15%, {highlight}0B 0%,transparent 43%),#080F1D;}}
[data-testid="stSidebar"] {{background: linear-gradient(165deg,#111E33 0%,#091322 100%);border-right:1px solid rgba(167,200,236,.13);}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{color:#B7C7DA;}}
.block-container {{padding-top:1.25rem;padding-bottom:3.5rem;max-width:1530px;}}
[data-testid="stVerticalBlock"] > div {{scroll-margin-top:1rem;}}
h1,h2,h3 {{letter-spacing:-.036em;font-weight:790;}}
h1 {{font-size:clamp(2rem,3vw,3rem)!important;}}
h2 {{font-size:1.36rem!important;}}
[data-testid="stMetric"] {{background:linear-gradient(136deg,rgba(35,58,85,.62),rgba(18,31,51,.62));border:1px solid rgba(183,216,248,.16);border-radius:18px;padding:17px 18px;box-shadow:0 14px 32px rgba(0,0,0,.15);backdrop-filter:blur(16px);}}
[data-testid="stMetric"]:hover {{border-color:{accent}66;transform:translateY(-2px);transition:all .2s ease;}}
[data-testid="stMetricLabel"] {{color:#AEC0D7;}}
[data-testid="stMetricValue"] {{font-weight:760;}}
[data-testid="stTabs"] button[aria-selected="true"] {{color:{accent};border-color:{accent};}}
[data-testid="stExpander"], [data-testid="stDataFrame"] {{border-radius:14px;}}
[data-testid="stSelectbox"], [data-testid="stMultiSelect"], [data-testid="stSlider"] {{color:#DDE8F8;}}
[data-testid="stPageLink-NavLink"]:hover {{background:{accent}20;}}
[data-testid="stBaseButton-primary"] {{background:{accent};border-radius:12px;color:#08101c;font-weight:760;border:none;}}
[data-testid="stPlotlyChart"] {{background:rgba(16,28,48,.35);border:1px solid rgba(167,200,236,.11);border-radius:16px;padding:6px;}}
.ipl-eyebrow {{text-transform:uppercase;font-weight:800;letter-spacing:.19em;font-size:.68rem;color:var(--ipl-accent);}}
.ipl-hero {{position:relative;overflow:hidden;border-radius:23px;padding:28px 30px;margin:0 0 19px;background:linear-gradient(116deg,{dark},#0D1A30 73%,{accent}21);border:1px solid {accent}45;box-shadow:0 25px 60px rgba(0,0,0,.24);}}
.ipl-hero::before {{content:'';position:absolute;width:340px;height:340px;right:-95px;top:-120px;border:1px solid {accent}3B;border-radius:50%;box-shadow:0 0 0 36px {accent}09,0 0 0 78px {accent}07;pointer-events:none;}}
.ipl-hero h1 {{font-size:clamp(2rem,3.1vw,3.2rem);margin:.2rem 0 .55rem;color:#FFFFFF;line-height:1.06;max-width:850px;}}
.ipl-hero p {{max-width:780px;color:#CAD8EB;line-height:1.6;font-size:.94rem;}}
.ipl-eyeline {{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:10px;}}
.ipl-pill {{display:inline-block;padding:6px 11px;border:1px solid {accent}55;background:{accent}16;border-radius:999px;color:{accent};font-weight:700;font-size:.72rem;letter-spacing:.03em;}}
.ipl-card {{position:relative;min-height:130px;padding:18px 19px;border:1px solid rgba(187,219,249,.15);border-radius:17px;box-shadow:inset 0 1px 0 rgba(255,255,255,.045),0 18px 30px rgba(0,0,0,.14);background:linear-gradient(132deg,rgba(41,68,102,.53),rgba(17,30,51,.55));backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);transition:transform .21s,border-color .21s;}}
.ipl-card:hover {{transform:translateY(-3px);border-color:{accent}91;}}
.ipl-card::after {{content:'';position:absolute;right:18px;top:15px;width:7px;height:7px;border-radius:50%;background:{accent};box-shadow:0 0 14px {accent}88;}}
.ipl-card-label {{font-size:.76rem;color:#D2DFEE;letter-spacing:.012em;line-height:1.35;margin-bottom:11px;font-weight:600;}}
.ipl-card-value {{font-size:clamp(1.35rem,2vw,2.05rem);font-weight:840;line-height:1.14;color:#F6FBFF;letter-spacing:-.04em;white-space:normal;overflow-wrap:anywhere;}}
.ipl-card-note {{font-size:.70rem;color:#9FB2C9;margin-top:8px;line-height:1.4;}}
.ipl-panel {{border:1px solid rgba(188,212,241,.14);border-radius:18px;background:linear-gradient(135deg,rgba(27,48,74,.62),rgba(15,27,47,.75));padding:19px 21px;margin:9px 0 18px;}}
.ipl-panel-title {{font-weight:780;margin-bottom:10px;font-size:.98rem;color:#F3F7FF;}}
.ipl-insight {{border-left:3px solid {accent};border-radius:0 13px 13px 0;background:rgba(24,42,64,.75);padding:12px 16px;margin:9px 0;color:#DEEAF9;line-height:1.62;}}
.ipl-section-head {{margin:19px 0 10px;color:#FAFCFF;font-size:1.16rem;font-weight:790;}}
.ipl-muted {{color:#9CAFCA;font-size:.77rem;}}
.ipl-divider {{height:1px;background:linear-gradient(90deg,{accent}A8,rgba(255,255,255,.04));margin:18px 0;}}
.ipl-logo {{height:64px;width:64px;filter:drop-shadow(0 6px 14px rgba(0,0,0,.3));}}
.ipl-team-crest {{width:92px;height:92px;min-width:92px;background-position:center;background-repeat:no-repeat;background-size:contain;border-radius:20px;filter:drop-shadow(0 7px 18px {accent}50);}}
.ipl-hero-crest {{display:flex;gap:20px;align-items:center;}}
@keyframes ipl-enter {{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes ipl-aurora {{0%,100%{{box-shadow:0 0 0 1px {accent}33,0 9px 30px rgba(0,0,0,.19),0 0 19px {accent}10}}50%{{box-shadow:0 0 0 1px {accent}66,0 12px 34px rgba(0,0,0,.19),0 0 27px {accent}30}}}}
.ipl-card {{animation:ipl-enter .42s ease-out both,ipl-aurora 5s ease-in-out infinite;}}
.ipl-card:nth-child(even) {{animation-delay:.07s,.7s;}}
.ipl-hero {{animation:ipl-enter .35s ease-out both;}}
.ipl-card:hover {{box-shadow:0 15px 35px rgba(0,0,0,.25),0 0 28px {accent}50,inset 0 1px 0 rgba(255,255,255,.12);}}
[data-testid="stPlotlyChart"] {{transition:border-color .26s ease,transform .26s ease;}}
[data-testid="stPlotlyChart"]:hover {{border-color:{accent}4D;}}
@media (prefers-reduced-motion:reduce) {{*,*::before,*::after{{animation:none!important;transition:none!important;scroll-behavior:auto!important;}}}}
.ipl-hero-brand {{display:flex;gap:19px;align-items:center;}}
.ipl-team-mono {{font-size:5.4rem;line-height:.85;letter-spacing:-.09em;font-weight:900;color:{accent};text-shadow:0 2px 18px {accent}38;white-space:nowrap;}}
@media (max-width:640px) {{.ipl-hero {{padding:20px 18px;}} .ipl-card {{padding:13px 12px;min-height:94px;}} .ipl-card-value{{font-size:1.4rem;}}.ipl-team-mono{{font-size:3.6rem;}}}}
@media (prefers-reduced-motion:reduce) {{.ipl-card,[data-testid="stMetric"]{{transition:none!important;}} .ipl-card:hover{{transform:none;}}}}
</style>''',unsafe_allow_html=True)

def hero(title,subtitle,eyebrow='IPL / DATA INTELLIGENCE',chip='2008–2026',team=None):
    logo=''
    if team:
        fallback=ROOT/'assets/brand'/f'{team}.svg'
        fallback_uri=svg_uri(fallback) if fallback.exists() else ''
        local=local_logo_file(ROOT,team)
        if local:
            from urllib.parse import quote
            if local.suffix=='.svg':src=svg_uri(local)
            else:
                media='image/webp' if local.suffix=='.webp' else ('image/jpeg' if local.suffix in ('.jpg','.jpeg') else 'image/png')
                src='data:'+media+';base64,'+base64.b64encode(local.read_bytes()).decode('ascii')
            image_desc=f'Locally provided franchise logo for {team}'
            style=f'background-image:url({src}),url({fallback_uri})'
        else:
            image_desc=f'{team} logo (IPL-hosted where accessible; decorative monogram offline)'
            style=f'background-image:url({official_logo_url(team)}),url({fallback_uri})'
        logo=f'<div class="ipl-team-crest" role="img" aria-label="{safe(image_desc)}" style="{style}"></div>'
    else:
        path=ROOT/'assets/brand'/'IPL360.svg'
        if path.exists():logo=f'<img class="ipl-logo" alt="IPL Intelligence 360 decorative project emblem" src="{svg_uri(path)}"/>'
    st.markdown(f'''<section class="ipl-hero"><div class="ipl-eyeline">{logo}<span class="ipl-eyebrow">{safe(eyebrow)}</span><span class="ipl-pill">{safe(chip)}</span></div><h1>{safe(title)}</h1><p>{safe(subtitle)}</p></section>''',unsafe_allow_html=True)

def kpi(label,value,note=''):
    st.markdown(f'<div class="ipl-card"><div class="ipl-card-label">{safe(label)}</div><div class="ipl-card-value">{safe(value)}</div><div class="ipl-card-note">{safe(note) if note else "&nbsp;"}</div></div>',unsafe_allow_html=True)

def section(title,detail=None):
    st.markdown(f'<div class="ipl-section-head">{safe(title)}</div>',unsafe_allow_html=True)
    if detail:st.caption(detail)

def analyst(notes):
    section('THE ANALYST’S DESK', 'Evidence-based reading of the currently selected match universe.')
    for note in notes:
        # evidence_notes returns a limited trusted Markdown set; display as Streamlit Markdown outside HTML.
        st.markdown(note)
    st.caption('Descriptive comparisons ≠ causal claims or future match predictions.')
