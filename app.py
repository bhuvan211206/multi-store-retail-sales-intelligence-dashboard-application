"""
NEXUS — Retail Intelligence Platform
=====================================
Run both servers:
    python start.py

Run individually:
    API:       python server.py
    Dashboard: python -m streamlit run app.py
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import warnings
try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False
warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG  (must be first Streamlit call)
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NEXUS · Retail Intelligence",
    layout="wide",
    page_icon="assets/icon.png",
    initial_sidebar_state="expanded",
)

import base64
import os

def get_base64_of_bin_file(bin_file):
    if not os.path.exists(bin_file):
        return ""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

icon_b64 = get_base64_of_bin_file("assets/icon.png")

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE  ─  gate before any rendering
# ══════════════════════════════════════════════════════════════════════════════
if "app_started" not in st.session_state:
    st.session_state["app_started"] = False

# ─────────────────────────────────────────────────────────────────────────────
# LANDING PAGE
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state["app_started"]:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500&display=swap');
    [data-testid="stHeader"],[data-testid="stSidebar"],[data-testid="stToolbar"]{display:none!important;}
    .block-container{padding:0!important;max-width:100%!important;}
    html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"],.main{
        background:#06040E!important;background-color:#06040E!important;
        overflow:hidden;
    }
    #lp-orb-1,#lp-orb-2,#lp-orb-3,#lp-orb-4,#lp-orb-5{
        position:fixed;border-radius:50%;pointer-events:none;filter:blur(80px);z-index:0;
    }
    #lp-orb-1{width:55vw;height:55vw;background:radial-gradient(circle,rgba(168,85,247,0.55),transparent 70%);
              top:-15vh;left:-12vw;animation:orb1 14s ease-in-out infinite alternate;}
    #lp-orb-2{width:50vw;height:50vw;background:radial-gradient(circle,rgba(245,158,11,0.40),transparent 70%);
              top:5vh;right:-14vw;animation:orb2 17s ease-in-out infinite alternate;}
    #lp-orb-3{width:42vw;height:42vw;background:radial-gradient(circle,rgba(244,63,94,0.32),transparent 70%);
              bottom:-10vh;left:20vw;animation:orb3 11s ease-in-out infinite alternate;}
    #lp-orb-4{width:30vw;height:30vw;background:radial-gradient(circle,rgba(196,132,252,0.38),transparent 70%);
              bottom:8vh;right:5vw;animation:orb4 19s ease-in-out infinite alternate;}
    #lp-orb-5{width:22vw;height:22vw;background:radial-gradient(circle,rgba(251,146,60,0.28),transparent 70%);
              top:45vh;left:40vw;animation:orb5 13s ease-in-out infinite alternate;}
    @keyframes orb1{0%{transform:translate(0,0) scale(1);}100%{transform:translate(5vw,8vh) scale(1.15);}}
    @keyframes orb2{0%{transform:translate(0,0) scale(1);}100%{transform:translate(-6vw,5vh) scale(0.9);}}
    @keyframes orb3{0%{transform:translate(0,0) scale(1);}100%{transform:translate(4vw,-6vh) scale(1.1);}}
    @keyframes orb4{0%{transform:translate(0,0) scale(1);}100%{transform:translate(-4vw,-7vh) scale(1.2);}}
    @keyframes orb5{0%{transform:translate(0,0) scale(1);}100%{transform:translate(6vw,5vh) scale(0.85);}}
    .lp-grid{
        position:fixed;inset:0;pointer-events:none;z-index:0;
        background-image:linear-gradient(rgba(168,85,247,0.04) 1px,transparent 1px),
                         linear-gradient(90deg,rgba(168,85,247,0.04) 1px,transparent 1px);
        background-size:70px 70px;
    }
    #lp-card{
        position:relative;z-index:10;display:flex;flex-direction:column;
        align-items:center;justify-content:center;min-height:100vh;
        text-align:center;padding:0 24px;
    }
    .lp-logo-ring{
        width:96px;height:96px;border-radius:50%;
        border:1px solid rgba(168,85,247,0.35);
        background:rgba(168,85,247,0.08);
        display:flex;align-items:center;justify-content:center;
        margin:0 auto 28px;
        box-shadow:0 0 60px rgba(168,85,247,0.30),0 0 120px rgba(168,85,247,0.12);
        animation:ring-pulse 3s ease-in-out infinite;
    }
    @keyframes ring-pulse{
        0%,100%{box-shadow:0 0 40px rgba(168,85,247,0.30),0 0 80px rgba(168,85,247,0.10);}
        50%{box-shadow:0 0 80px rgba(245,158,11,0.45),0 0 140px rgba(245,158,11,0.15);}
    }
    .lp-tagline{
        font-family:'Inter',sans-serif;font-size:13px;font-weight:400;
        color:#9A8FBB;letter-spacing:2px;text-transform:uppercase;
        margin-bottom:20px;animation:fade-in 1s ease 0.3s both;
    }
    .lp-title{
        font-family:'Syne',sans-serif;font-size:clamp(48px,7vw,96px);
        font-weight:800;color:#F0EAFF;letter-spacing:-2px;line-height:1;
        margin-bottom:14px;animation:fade-in 1s ease 0.5s both;
    }
    .lp-title span{
        background:linear-gradient(135deg,#A855F7,#F59E0B,#F43F5E);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text;
        animation:title-hue 8s linear infinite;
    }
    @keyframes title-hue{0%{filter:hue-rotate(0deg);}100%{filter:hue-rotate(360deg);}}
    .lp-sub{
        font-family:'Inter',sans-serif;font-size:clamp(14px,1.6vw,18px);
        font-weight:300;color:#5A5080;max-width:520px;line-height:1.7;
        margin-bottom:48px;animation:fade-in 1s ease 0.7s both;
    }
    .lp-stats{
        display:flex;gap:40px;justify-content:center;margin-bottom:52px;
        animation:fade-in 1s ease 0.9s both;
    }
    .lp-stat-item{display:flex;flex-direction:column;align-items:center;gap:4px;}
    .lp-stat-val{
        font-family:'Syne',sans-serif;font-size:28px;font-weight:800;
        background:linear-gradient(135deg,#A855F7,#C084FC);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    }
    .lp-stat-label{font-size:11px;color:#5A5080;text-transform:uppercase;letter-spacing:1px;}
    .lp-badge-row{
        display:flex;gap:10px;justify-content:center;flex-wrap:wrap;
        margin-bottom:56px;animation:fade-in 1s ease 1.1s both;
    }
    .lp-badge{
        display:inline-flex;align-items:center;gap:7px;padding:6px 14px;
        border:1px solid rgba(168,85,247,0.22);border-radius:100px;
        background:rgba(168,85,247,0.07);font-size:11px;
        color:#9A8FBB;letter-spacing:0.5px;
    }
    .lp-badge-dot{width:5px;height:5px;border-radius:50%;}
    @keyframes fade-in{from{opacity:0;transform:translateY(12px);}to{opacity:1;transform:none;}}
    </style>
    <div id="lp-orb-1"></div>
    <div id="lp-orb-2"></div>
    <div id="lp-orb-3"></div>
    <div id="lp-orb-4"></div>
    <div id="lp-orb-5"></div>
    <div class="lp-grid"></div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1,2,1])
    with col_b:
        st.markdown(f"""
        <div id="lp-card">
          <div class="lp-logo-ring">
            <img src="data:image/png;base64,{icon_b64}" width="52"
                 style="border-radius:12px;filter:drop-shadow(0 0 16px rgba(168,85,247,0.7));">
          </div>
          <div class="lp-tagline">Retail Intelligence Platform</div>
          <div class="lp-title">NEXUS<span>.</span></div>
          <div class="lp-sub">
            Real-time analytics for modern store networks.<br>
            Unify your stores, products and performance — in one live dashboard.
          </div>
          <div class="lp-stats">
            <div class="lp-stat-item">
              <div class="lp-stat-val">5</div>
              <div class="lp-stat-label">Stores</div>
            </div>
            <div class="lp-stat-item">
              <div class="lp-stat-val" style="background:linear-gradient(135deg,#F59E0B,#FB923C);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">50+</div>
              <div class="lp-stat-label">Products</div>
            </div>
            <div class="lp-stat-item">
              <div class="lp-stat-val" style="background:linear-gradient(135deg,#F43F5E,#FB923C);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">3</div>
              <div class="lp-stat-label">Modules</div>
            </div>
            <div class="lp-stat-item">
              <div class="lp-stat-val" style="background:linear-gradient(135deg,#C084FC,#A855F7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">Live</div>
              <div class="lp-stat-label">Updates</div>
            </div>
          </div>
          <div class="lp-badge-row">
            <div class="lp-badge"><div class="lp-badge-dot" style="background:#A855F7;"></div>Store Performance</div>
            <div class="lp-badge"><div class="lp-badge-dot" style="background:#F59E0B;"></div>Stock & Inventory</div>
            <div class="lp-badge"><div class="lp-badge-dot" style="background:#F43F5E;"></div>Product Analytics</div>
            <div class="lp-badge"><div class="lp-badge-dot" style="background:#22D3A0;"></div>Profit & Loss</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀  Enter Dashboard  →", use_container_width=True, key="btn_enter"):
            st.session_state["app_started"] = True
            st.rerun()

    # Render a centered CTA button with custom styling
    st.markdown("""
    <style>
    div[data-testid="stButton"]>button{
        background:linear-gradient(135deg,rgba(168,85,247,0.25),rgba(245,158,11,0.15))!important;
        border:1px solid rgba(168,85,247,0.5)!important;
        color:#F0EAFF!important;
        font-family:'Syne',sans-serif!important;
        font-size:16px!important;font-weight:700!important;
        padding:18px 48px!important;border-radius:14px!important;
        letter-spacing:0.5px;
        box-shadow:0 0 40px rgba(168,85,247,0.25),0 0 80px rgba(168,85,247,0.08)!important;
        animation:btn-glow 3s ease-in-out infinite alternate;
        transition:all 0.25s!important;
    }
    div[data-testid="stButton"]>button:hover{
        background:linear-gradient(135deg,rgba(168,85,247,0.45),rgba(245,158,11,0.30))!important;
        box-shadow:0 0 60px rgba(168,85,247,0.50),0 0 100px rgba(168,85,247,0.15)!important;
        transform:translateY(-3px) scale(1.02)!important;
    }
    @keyframes btn-glow{
        from{box-shadow:0 0 30px rgba(168,85,247,0.20),0 0 60px rgba(168,85,247,0.06)!important;}
        to  {box-shadow:0 0 55px rgba(245,158,11,0.35),0 0 90px rgba(245,158,11,0.10)!important;}
    }
    </style>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* ── CSS Variables — Violet/Gold/Rose Premium Theme ── */
:root {
    --bg0: #06040E;
    --bg1: #0A0714;
    --bg2: #100D1E;
    --bg3: #161228;
    --bg4: #1C1730;
    --border0: rgba(255,255,255,0.04);
    --border1: rgba(255,255,255,0.08);
    --border2: rgba(255,255,255,0.14);
    --txt0: #F0EAFF;
    --txt1: #9A8FBB;
    --txt2: #5A5080;
    --blue:   #A855F7;
    --teal:   #F59E0B;
    --coral:  #F43F5E;
    --amber:  #FB923C;
    --violet: #C084FC;
    --mint:   #FCD34D;
    --shadow: 0 4px 24px rgba(0,0,0,0.6);
    --glass: rgba(16,13,30,0.80);
    --glass-border: rgba(168,85,247,0.10);
    --glow-blue: 0 0 40px rgba(168,85,247,0.22);
    --glow-teal: 0 0 40px rgba(245,158,11,0.18);
}

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body {
    background-color: #06040E !important;
    color: #F0EAFF !important;
}

.stApp,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background: #06040E !important;
    background-color: #06040E !important;
    color: #F0EAFF !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px;
}

/* ── Ambient Orbs — animated color-cycling ── */
@keyframes orb-shift {
    0%   { opacity: 1; }
    33%  { opacity: 0.6; filter: hue-rotate(60deg) brightness(1.15); }
    66%  { opacity: 0.8; filter: hue-rotate(140deg) brightness(0.9); }
    100% { opacity: 1; filter: hue-rotate(0deg) brightness(1); }
}
@keyframes orb-move-1 {
    0%,100% { transform: translate(0,0) scale(1); }
    33%     { transform: translate(6%,4%) scale(1.08); }
    66%     { transform: translate(-4%,8%) scale(0.95); }
}
@keyframes orb-move-2 {
    0%,100% { transform: translate(0,0) scale(1); }
    33%     { transform: translate(-5%,-6%) scale(1.12); }
    66%     { transform: translate(8%,3%) scale(0.92); }
}
@keyframes orb-move-3 {
    0%,100% { transform: translate(0,0) scale(1); }
    33%     { transform: translate(4%,-8%) scale(1.05); }
    66%     { transform: translate(-6%,5%) scale(1.10); }
}

/* Main ambient layer: three floating orbs */
[data-testid="stApp"]::before {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    animation: orb-shift 12s ease-in-out infinite, orb-move-1 18s ease-in-out infinite;
    background:
        radial-gradient(ellipse 58% 42% at 12% 18%,  rgba(168,85,247,0.18)  0%, transparent 68%),
        radial-gradient(ellipse 46% 34% at 82% 14%,  rgba(245,158,11,0.14)  0%, transparent 68%),
        radial-gradient(ellipse 62% 48% at 68% 78%,  rgba(196,132,252,0.13) 0%, transparent 68%),
        radial-gradient(ellipse 42% 32% at 28% 82%,  rgba(244,63,94,0.11)   0%, transparent 68%),
        radial-gradient(ellipse 38% 30% at 52% 48%,  rgba(251,146,60,0.09)  0%, transparent 68%);
}

/* Subtle grid overlay */
[data-testid="stApp"]::after {
    content: '';
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.018) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.018) 1px, transparent 1px);
    background-size: 80px 80px;
}

/* Show Streamlit header but make it transparent so we can see the sidebar toggle */
[data-testid="stHeader"] {
    background: transparent !important;
    border: none !important;
    z-index: 99 !important;
}
/* Ensure the sidebar toggle button is visible and colored correctly */
[data-testid="stHeader"] button {
    color: var(--violet) !important;
}

/* Remove default Streamlit padding */
.block-container {
    padding: 0 2rem 4rem 2rem !important;
    max-width: 100% !important;
    position: relative;
    z-index: 1;
}

/* ── Topbar ── */
#nexus-topbar {
    position: sticky;
    top: 0; left: 0; right: 0;
    z-index: 999;
    background: rgba(4,5,10,0.82);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 0 2rem;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 0 rgba(255,255,255,0.04), 0 8px 32px rgba(0,0,0,0.4);
}
#nexus-topbar .brand { display: flex; align-items: center; gap: 10px; }
#nexus-topbar .brand-icon { font-size: 18px; animation: pulse-icon 3s ease-in-out infinite; }
@keyframes pulse-icon {
    0%,100% { filter: drop-shadow(0 0 4px rgba(168,85,247,0.5)); }
    50%      { filter: drop-shadow(0 0 14px rgba(245,158,11,0.8)); }
}
@keyframes icon-hue {
    0%,100% { filter: hue-rotate(0deg) brightness(1.1); }
    50%      { filter: hue-rotate(80deg) brightness(1.25); }
}
#nexus-topbar .brand-icon { animation: pulse-icon 3s ease-in-out infinite, icon-hue 8s ease-in-out infinite; }
#nexus-topbar .brand-name { font-family: 'Syne', sans-serif; font-size: 17px; font-weight: 800; color: #F0EAFF; letter-spacing: -0.5px; }
#nexus-topbar .brand-sub  { font-size: 10px; color: #5A5080; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 1px; }
#nexus-topbar .nav-pills  { display: flex; gap: 6px; align-items: center; }
#nexus-topbar .pill {
    padding: 5px 14px; border-radius: 20px; font-size: 11px; font-weight: 600;
    letter-spacing: 0.4px; border: 1px solid rgba(255,255,255,0.08); color: #5A5080;
    background: transparent; transition: all 0.2s;
}
#nexus-topbar .pill.active {
    background: rgba(168,85,247,0.14); border-color: rgba(168,85,247,0.35);
    color: #C084FC; box-shadow: 0 0 16px rgba(168,85,247,0.20);
}
#nexus-topbar .live-dot {
    width: 6px; height: 6px; background: #F59E0B; border-radius: 50%;
    animation: blink 2s ease-in-out infinite; margin-right: 4px; display: inline-block;
}
@keyframes blink {
    0%,100% { opacity: 1; box-shadow: 0 0 6px #F59E0B; }
    50%      { opacity: 0.3; box-shadow: none; }
}
@keyframes blink-violet {
    0%,100% { opacity: 1; box-shadow: 0 0 6px #A855F7; }
    50%      { opacity: 0.3; box-shadow: none; }
}
#nexus-topbar .meta { display: flex; align-items: center; gap: 14px; }
#nexus-topbar .meta-item { font-size: 11px; color: #4A5270; display: flex; align-items: center; gap: 5px; }

/* ── Page module header card ── */
.nexus-page-header {
    background: linear-gradient(135deg, var(--glass) 0%, rgba(4,5,10,0.4) 100%);
    backdrop-filter: blur(16px);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 32px 36px;
    margin: 1.2rem 0 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    overflow: hidden;
}
.nexus-page-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(168,85,247,0.5), rgba(245,158,11,0.35), rgba(244,63,94,0.25), transparent);
    animation: topline-glow 6s ease-in-out infinite alternate;
}
@keyframes topline-glow {
    from { opacity: 0.7; }
    to   { opacity: 1; filter: blur(0.5px); }
}

/* ── Footer ── */
#nexus-footer {
    background: var(--glass);
    backdrop-filter: blur(20px);
    border-top: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px 20px 0 0;
    margin-top: 64px;
    padding: 40px 48px 28px;
    position: relative;
    overflow: hidden;
}
#nexus-footer::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(168,85,247,0.6) 25%, rgba(245,158,11,0.5) 55%, rgba(244,63,94,0.45) 80%, transparent 100%);
    animation: footer-line-shift 8s ease-in-out infinite alternate;
}
@keyframes footer-line-shift {
    from { background-position: 0% 50%; }
    to   { filter: hue-rotate(30deg); }
}
#nexus-footer .footer-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 32px; margin-bottom: 32px; }
#nexus-footer .footer-brand { display: flex; flex-direction: column; gap: 8px; }
#nexus-footer .footer-logo { font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 800; color: #EDF0FF; letter-spacing: -0.5px; display: flex; align-items: center; gap: 8px; }
#nexus-footer .footer-tagline { font-size: 12px; color: #4A5270; line-height: 1.6; max-width: 240px; }
#nexus-footer .footer-stat-group { display: flex; flex-direction: column; gap: 4px; }
#nexus-footer .footer-stat-label { font-size: 10px; color: #4A5270; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: 8px; }
#nexus-footer .footer-stat { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
#nexus-footer .footer-stat-val { font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700; color: #EDF0FF; }
#nexus-footer .footer-stat-key { font-size: 11px; color: #4A5270; }
#nexus-footer .footer-badges { display: flex; flex-direction: column; gap: 10px; }
#nexus-footer .footer-badge { display: inline-flex; align-items: center; gap: 8px; padding: 7px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.02); width: fit-content; }
#nexus-footer .footer-badge-dot { width: 5px; height: 5px; border-radius: 50%; }
#nexus-footer .footer-badge-text { font-size: 11px; color: #8892B0; }
#nexus-footer .footer-bottom { display: flex; justify-content: space-between; align-items: center; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.04); }
#nexus-footer .footer-copy { font-size: 11px; color: #4A5270; letter-spacing: 0.3px; }
#nexus-footer .footer-version { font-size: 10px; color: #4A5270; font-family: 'Syne', monospace; background: rgba(255,255,255,0.03); padding: 3px 10px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.06); }

/* ══════════════════════════════════════════════════════
   REDESIGNED SIDEBAR
   ══════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080510 0%, #0C0820 100%) !important;
    border-right: 1px solid rgba(168,85,247,0.15) !important;
    min-width: 290px !important;
    max-width: 290px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebarContent"] { padding: 0 !important; }

/* Sidebar section labels */
[data-testid="stSidebar"] label {
    color: var(--txt1) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] .stMarkdown p { color: var(--txt2) !important; font-size: 13px !important; }

/* Sidebar Selectors */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(16,13,30,0.9) !important;
    border: 1px solid rgba(168,85,247,0.15) !important;
    border-radius: 8px !important;
}

/* Multiselect tags */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: rgba(168,85,247,0.15) !important;
    border: 1px solid rgba(168,85,247,0.30) !important;
    border-radius: 4px !important;
    color: var(--txt0) !important;
    margin-right: 4px !important;
    padding: 2px !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span { font-size: 12px !important; font-weight: 500 !important; color: var(--txt0) !important; }

/* Sidebar radio buttons */
[data-testid="stSidebar"] [data-baseweb="radio"] label {
    padding: 8px 12px; border-radius: 6px; margin-bottom: 4px;
    transition: all 0.15s; cursor: pointer; background: transparent;
    display: flex; align-items: center; white-space: nowrap;
}
[data-testid="stSidebar"] [data-baseweb="radio"] label:hover { background: var(--bg3) !important; }
[data-testid="stSidebar"] [aria-checked="true"] + label,
[data-testid="stSidebar"] [data-baseweb="radio"] [aria-checked="true"] ~ div { color: var(--violet) !important; }

/* Sidebar nav cards */
.sb-nav-card {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; border-radius: 10px; margin: 3px 0;
    border: 1px solid transparent; cursor: pointer;
    transition: all 0.2s;
    background: transparent;
}
.sb-nav-card.active {
    background: rgba(168,85,247,0.10);
    border-color: rgba(168,85,247,0.28);
}
.sb-nav-card:hover { background: rgba(255,255,255,0.04); }
.sb-nav-icon { font-size: 18px; width: 32px; height: 32px; display:flex; align-items:center; justify-content:center; border-radius:8px; }
.sb-nav-label { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 600; color: #EDF0FF; }
.sb-nav-sub { font-size: 10px; color: #4A5270; margin-top: 1px; }
.sb-section-label {
    font-size: 9px; color: #2A3050; text-transform: uppercase;
    letter-spacing: 1.5px; font-weight: 700; padding: 0 16px;
    margin: 16px 0 6px;
}
.sb-divider { height: 1px; background: rgba(255,255,255,0.05); margin: 8px 0; }

/* ── KPI Metric Cards ── */
[data-testid="metric-container"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border1) !important;
    border-radius: 14px !important;
    padding: 20px 20px 18px !important;
    position: relative; overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="metric-container"]:hover { transform: translateY(-2px); border-color: var(--border2) !important; box-shadow: var(--shadow); }
[data-testid="metric-container"]::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--blue), var(--teal), var(--coral));
    border-radius: 14px 14px 0 0;
    animation: bar-pulse 4s ease-in-out infinite alternate, bar-hue 10s linear infinite;
}
@keyframes bar-pulse { from { opacity: 0.6; } to { opacity: 1; filter: blur(0.5px); } }
@keyframes bar-hue   { from { filter: hue-rotate(0deg); } to { filter: hue-rotate(360deg); } }
[data-testid="stMetricLabel"] { color: var(--txt1) !important; font-size: 10px !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 1px !important; }
[data-testid="stMetricValue"] { color: var(--txt0) !important; font-size: 26px !important; font-weight: 700 !important; font-family: 'Syne', sans-serif !important; line-height: 1.2 !important; }
[data-testid="stMetricDelta"] { font-size: 11px !important; font-weight: 500 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: var(--bg2) !important; border: 1px solid rgba(168,85,247,0.12) !important; border-radius: 12px !important; padding: 5px !important; gap: 3px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--txt1) !important; border-radius: 8px !important; padding: 9px 22px !important; font-size: 13px !important; font-weight: 500 !important; font-family: 'Inter', sans-serif !important; border: none !important; transition: all 0.15s !important; }
.stTabs [data-baseweb="tab"]:hover { background: var(--bg3) !important; color: var(--txt0) !important; }
.stTabs [aria-selected="true"] { background: rgba(168,85,247,0.14) !important; color: var(--violet) !important; border: 1px solid rgba(168,85,247,0.28) !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── Dividers ── */
hr { border: none !important; height: 1px !important; background: var(--border0) !important; margin: 2.2rem 0 !important; }

/* ── Dataframe / Tables ── */
[data-testid="stDataFrame"] { border-radius: 12px !important; border: 1px solid var(--border1) !important; overflow: hidden !important; }
[data-testid="stDataFrame"] table { background: var(--bg2) !important; }
[data-testid="stDataFrame"] thead tr th { background: var(--bg3) !important; color: var(--txt1) !important; font-size: 11px !important; text-transform: uppercase !important; letter-spacing: 0.8px !important; font-weight: 600 !important; border-bottom: 1px solid var(--border1) !important; }
[data-testid="stDataFrame"] tbody tr:hover td { background: var(--bg3) !important; }

/* ── Alerts ── */
.stAlert { border-radius: 12px !important; border: 1px solid var(--border1) !important; background: var(--bg2) !important; }

/* ── Selectbox ── */
[data-baseweb="select"] > div { background: var(--bg2) !important; border: 1px solid var(--border1) !important; border-radius: 8px !important; color: var(--txt0) !important; }
[data-baseweb="popover"] { background: var(--bg3) !important; border: 1px solid var(--border2) !important; border-radius: 10px !important; }
[data-baseweb="menu"] { background: var(--bg3) !important; }
[data-baseweb="option"] { background: var(--bg3) !important; color: var(--txt0) !important; }
[data-baseweb="option"]:hover { background: var(--bg4) !important; }

/* ── Multiselect tags ── */
[data-baseweb="tag"] { background: rgba(168,85,247,0.12) !important; border: 1px solid rgba(168,85,247,0.25) !important; border-radius: 5px !important; color: var(--violet) !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] { background: var(--bg2) !important; border: 1px dashed rgba(168,85,247,0.25) !important; border-radius: 12px !important; }
[data-testid="stFileUploader"]:hover { border-color: var(--blue) !important; }

/* ── Buttons ── */
.stButton > button { background: rgba(168,85,247,0.12) !important; border: 1px solid rgba(168,85,247,0.30) !important; color: var(--violet) !important; border-radius: 8px !important; font-family: 'Inter', sans-serif !important; font-weight: 500 !important; font-size: 13px !important; padding: 8px 20px !important; transition: all 0.15s !important; }
.stButton > button:hover { background: rgba(168,85,247,0.22) !important; border-color: var(--blue) !important; transform: translateY(-1px) !important; }

/* ── Radio buttons ── */
[data-baseweb="radio"] span { color: var(--txt1) !important; font-size: 13px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--txt2); }

/* ── Info / Warning / Success ── */
div[data-testid="stInfo"], div[data-testid="stWarning"], div[data-testid="stSuccess"] { border-radius: 10px !important; }

/* ── Expanders ── */
.streamlit-expanderHeader { background: var(--bg2) !important; border-radius: 10px !important; font-family: 'Inter', sans-serif !important; font-size: 13px !important; color: var(--txt0) !important; }
.streamlit-expanderContent { background: var(--bg2) !important; border: 1px solid var(--border1) !important; border-top: none !important; border-radius: 0 0 10px 10px !important; }

/* ── Number/text inputs ── */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input { background: var(--bg2) !important; border: 1px solid var(--border1) !important; border-radius: 8px !important; color: var(--txt0) !important; font-family: 'Inter', sans-serif !important; }

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] { background: var(--violet) !important; }

/* ── section-header accent bar animation ── */
.nexus-sh-bar { animation: sh-glow 3s ease-in-out infinite alternate; }
@keyframes sh-glow { from { box-shadow: none; } to { box-shadow: 0 0 8px currentColor; } }

/* Product card grid */
.prod-stat-card {
    background: rgba(13,18,32,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 16px;
    position: relative;
    overflow: hidden;
    transition: all 0.2s;
}
.prod-stat-card:hover { border-color: rgba(91,155,248,0.25); transform: translateY(-2px); }
.prod-stat-card .psc-top { font-size: 10px; color: #4A5270; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: 6px; }
.prod-stat-card .psc-val { font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 800; }
.prod-stat-card .psc-sub { font-size: 11px; color: #4A5270; margin-top: 4px; }

/* Category pill badges */
.cat-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 20px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.3px;
    border: 1px solid transparent;
}
</style>
<div id="nexus-cursor-glow"></div>
<script>
    (function() {
        // Clean up legacy global element if it exists
        try {
            const oldGlow = window.parent.document.getElementById('nexus-cursor-glow');
            if (oldGlow) oldGlow.remove();
        } catch(e) {}

        const glow = document.getElementById('nexus-cursor-glow');
        if (!glow) return;

        Object.assign(glow.style, {
            position: 'fixed',
            inset: '0',
            pointerEvents: 'none',
            zIndex: '999999',
            mixBlendMode: 'screen',
            transition: 'background 0.08s ease-out'
        });

        const handleMouseMove = (e) => {
            const h = (Date.now() / 70) % 360;
            // Enhanced Multi-Layer Ambient Light
            // 1. Large soft halo for overall mood
            // 2. Focused central glow for interactivity
            glow.style.background = `
                radial-gradient(circle 600px at ${e.clientX}px ${e.clientY}px, hsla(${h}, 70%, 60%, 0.08), transparent 80%),
                radial-gradient(circle 150px at ${e.clientX}px ${e.clientY}px, hsla(${h}, 85%, 75%, 0.12), transparent 70%)
            `;
        };

        window.removeEventListener('mousemove', handleMouseMove);
        window.addEventListener('mousemove', handleMouseMove);
        
        // Also handle the parent for when mouse enters/leaves the iframe area
        try {
            window.parent.document.addEventListener('mousemove', handleMouseMove);
        } catch(e) {}
    })();
</script>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS & PALETTE
# ══════════════════════════════════════════════════════════════════════════════
STORE_COLORS = {
    "North Mall":  "#A855F7",
    "South Plaza": "#F59E0B",
    "East Hub":    "#F43F5E",
    "City Centre": "#FB923C",
    "West Gate":   "#C084FC",
}
CAT_COLORS = {
    "Electronics":   "#A855F7",
    "Apparel":       "#F59E0B",
    "Home & Living": "#F43F5E",
    "Groceries":     "#FB923C",
    "Beauty":        "#C084FC",
}
STATUS_COLORS = {
    "Healthy":      "#22D3A0",
    "Low Stock":    "#F59E0B",
    "Out of Stock": "#F43F5E",
}
MO_ORDER = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

STAT_MAP = {
    "Revenue (₹ Lakhs)":   "Revenue_Lakhs",
    "Gross Margin %":       "Gross_Margin_Pct",
    "Daily Footfall":       "Daily_Footfall",
    "Conversion Rate %":    "Conversion_Rate_Pct",
    "Avg Basket Size (₹)": "Avg_Basket_Size_Rs",
    "Units Sold":           "Units_Sold",
}

# ── Product Catalog: Category → list of products ────────────────────────────
PRODUCT_CATALOG = {
    "Electronics": [
        "Laptops", "Smartphones", "Tablets", "Smart TVs", "Headphones",
        "Cameras", "Gaming Consoles", "Smartwatches", "Speakers", "Printers",
    ],
    "Apparel": [
        "T-Shirts", "Jeans", "Formal Shirts", "Dresses", "Jackets",
        "Sneakers", "Ethnic Wear", "Sportswear", "Accessories", "Kids Clothing",
    ],
    "Home & Living": [
        "Sofas", "Beds & Mattresses", "Kitchen Appliances", "Cookware",
        "Decor Items", "Lighting", "Storage & Shelves", "Curtains", "Rugs", "Air Purifiers",
    ],
    "Groceries": [
        "Fresh Produce", "Dairy & Eggs", "Beverages", "Snacks & Chips",
        "Rice & Grains", "Oils & Condiments", "Frozen Foods", "Bakery",
        "Personal Care", "Cleaning Supplies",
    ],
    "Beauty": [
        "Skincare", "Haircare", "Makeup", "Perfumes & Deodorants",
        "Nail Care", "Men's Grooming", "Sunscreen", "Face Masks",
        "Lip Care", "Eye Care",
    ],
}

PRODUCT_COLORS = {
    # Electronics
    "Laptops": "#5B9BF8", "Smartphones": "#4A8AE8", "Tablets": "#3979D8",
    "Smart TVs": "#2868C8", "Headphones": "#1757B8", "Cameras": "#6AABFF",
    "Gaming Consoles": "#79BAFF", "Smartwatches": "#88C9FF", "Speakers": "#97D8FF", "Printers": "#A6E7FF",
    # Apparel
    "T-Shirts": "#00E5B8", "Jeans": "#00CFA8", "Formal Shirts": "#00B998",
    "Dresses": "#00A388", "Jackets": "#008D78", "Sneakers": "#10F5C8",
    "Ethnic Wear": "#20DDB8", "Sportswear": "#30C5A8", "Accessories": "#40AD98", "Kids Clothing": "#50958A",
    # Home & Living
    "Sofas": "#FF5C7A", "Beds & Mattresses": "#FF4D6B", "Kitchen Appliances": "#FF3E5C",
    "Cookware": "#FF2F4D", "Decor Items": "#FF203E", "Lighting": "#FF6B8A",
    "Storage & Shelves": "#FF7A9A", "Curtains": "#FF89AA", "Rugs": "#FF98BA", "Air Purifiers": "#FFA7CA",
    # Groceries
    "Fresh Produce": "#FFAB2E", "Dairy & Eggs": "#FFA020", "Beverages": "#FF9512",
    "Snacks & Chips": "#FF8A04", "Rice & Grains": "#FFB540", "Oils & Condiments": "#FFC052",
    "Frozen Foods": "#FFCB64", "Bakery": "#FFD676", "Personal Care": "#FFE188", "Cleaning Supplies": "#FFEC9A",
    # Beauty
    "Skincare": "#A470FF", "Haircare": "#9862F0", "Makeup": "#8C54E1",
    "Perfumes & Deodorants": "#8046D2", "Nail Care": "#7438C3", "Men's Grooming": "#B07EFF",
    "Sunscreen": "#BE8CFF", "Face Masks": "#CC9AFF", "Lip Care": "#DAA8FF", "Eye Care": "#E8B6FF",
}


# ══════════════════════════════════════════════════════════════════════════════
# PLOTLY HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _ptheme():
    return dict(
        font=dict(color="#8892B0", family="Inter", size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(0,0,0,0)",
            tickfont=dict(color="#8892B0", size=11),
            title_font=dict(color="#8892B0"),
            linecolor="rgba(255,255,255,0.06)",
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(0,0,0,0)",
            tickfont=dict(color="#8892B0", size=11),
            title_font=dict(color="#8892B0"),
            linecolor="rgba(255,255,255,0.06)",
        ),
        legend=dict(
            bgcolor="rgba(13,18,32,0.8)",
            bordercolor="rgba(255,255,255,0.06)",
            borderwidth=1,
            font=dict(color="#8892B0", size=11),
        ),
        margin=dict(l=12, r=12, t=44, b=12),
        coloraxis_colorbar=dict(
            tickfont=dict(color="#8892B0"),
            title_font=dict(color="#8892B0"),
        ),
    )

def pt(fig, title=None, height=360):
    fig.update_layout(**_ptheme(), height=height)
    if title:
        fig.update_layout(title=dict(
            text=title,
            font=dict(color="#EDF0FF", size=13, family="Syne"),
            x=0, xanchor="left", pad=dict(l=4),
        ))
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def section_header(title: str, subtitle: str = "", accent: str = "#5B9BF8"):
    sub_html = f'<div style="font-size:12px;color:#4A5270;margin-top:6px;font-weight:400;padding-left:17px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="margin:2.8rem 0 1.4rem 0;padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,0.04);">
      <div style="display:flex;align-items:center;gap:12px;">
        <div class="nexus-sh-bar" style="width:3px;height:22px;
             background:linear-gradient(180deg,{accent},{accent}33);
             border-radius:2px;flex-shrink:0;color:{accent};"></div>
        <div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;
             color:#EDF0FF;letter-spacing:-0.3px;">{title}</div>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(255,255,255,0.04),transparent);"></div>
      </div>
      {sub_html}
    </div>""", unsafe_allow_html=True)


def kpi_delta_card(label, value, delta_label="", delta_val="", color="#5B9BF8"):
    st.markdown(f"""
    <div style="background:#0D1220;border:1px solid rgba(255,255,255,0.07);border-radius:14px;
    padding:20px 18px 16px;position:relative;overflow:hidden;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;background:{color};opacity:0.7;"></div>
      <div style="font-size:10px;color:#4A5270;text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:8px;">{label}</div>
      <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;color:#EDF0FF;">{value}</div>
      {'<div style="font-size:11px;color:'+color+';margin-top:5px;font-weight:500;">'+delta_val+' '+delta_label+'</div>' if delta_val else ''}
    </div>""", unsafe_allow_html=True)


def store_attainment_card(store, pct, color):
    pct_clamped = min(pct, 100)
    status      = "On Track" if pct_clamped >= 80 else "At Risk"
    s_color     = "#00E5B8" if pct_clamped >= 80 else "#FF5C7A"
    st.markdown(f"""
    <div style="background:#0D1220;border:1px solid rgba(255,255,255,0.06);border-top:3px solid {color};
    border-radius:12px;padding:18px 14px;text-align:center;height:100%;">
      <div style="font-size:10px;font-weight:700;color:#4A5270;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">{store}</div>
      <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:{color};line-height:1;">{pct_clamped:.1f}%</div>
      <div style="background:rgba(255,255,255,0.04);height:4px;margin:12px 0 10px;border-radius:4px;overflow:hidden;">
        <div style="background:{color};height:4px;width:{pct_clamped}%;border-radius:4px;"></div>
      </div>
      <div style="font-size:11px;color:{s_color};font-weight:600;">{status}</div>
    </div>""", unsafe_allow_html=True)


def page_header(title: str, subtitle: str, icon: str, color: str, rgb: str, record_count):
    st.markdown(f"""
    <div class="nexus-page-header">
      <div style="position:absolute;top:-80px;right:-80px;width:260px;height:260px;
           border-radius:50%;background:rgb({rgb});opacity:0.06;filter:blur(50px);pointer-events:none;"></div>
      <div style="position:relative;z-index:1;">
        <div style="display:flex;align-items:center;gap:14px;">
          <div style="width:48px;height:48px;background:rgba({rgb},0.1);border:1px solid rgba({rgb},0.2);
               border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:22px;
               box-shadow:0 0 20px rgba({rgb},0.15);">{icon}</div>
          <div>
            <div style="font-family:'Syne',sans-serif;font-size:24px;font-weight:800;
                 color:#EDF0FF;letter-spacing:-0.8px;line-height:1.1;">{title}</div>
            <div style="font-size:11px;color:#4A5270;margin-top:4px;letter-spacing:0.3px;">{subtitle}</div>
          </div>
        </div>
      </div>
      <div style="position:relative;z-index:1;text-align:right;">
        <div style="font-family:'Syne',sans-serif;font-size:36px;font-weight:800;
             color:{color};line-height:1;text-shadow:0 0 30px rgba({rgb},0.4);">{record_count:,}</div>
        <div style="font-size:10px;color:#4A5270;text-transform:uppercase;letter-spacing:1.2px;margin-top:6px;">Records Active</div>
        <div style="margin-top:8px;display:inline-block;background:rgba({rgb},0.08);
             border:1px solid rgba({rgb},0.2);border-radius:12px;padding:3px 12px;">
          <span style="font-size:10px;color:{color};font-weight:600;">● LIVE</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA ENGINE
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    np.random.seed(42)
    n = len(out)

    if "Current_Stock" not in out.columns:
        out["Current_Stock"] = (out["Units_Sold"] * np.random.uniform(0.5, 3.0, size=n)).astype(int)
    if "Reorder_Point" not in out.columns:
        out["Reorder_Point"] = (out["Units_Sold"] * 0.4).astype(int).clip(lower=5)
    if "Unit_Cost_Rs" not in out.columns:
        out["Unit_Cost_Rs"] = (out["Avg_Basket_Size_Rs"] * np.random.uniform(0.4, 0.7, size=n)).round(0)

    # ── Assign Sub-Products from catalog ─────────────────────────────────────
    # Each row gets a random product from its category's catalog
    rng = np.random.default_rng(99)
    prod_list = []
    for _, row in out.iterrows():
        cat = row["Category"]
        products = PRODUCT_CATALOG.get(cat, ["General Product"])
        prod_list.append(rng.choice(products))
    out["SubProduct"] = prod_list

    # Legacy Product column (category + SKU suffix) — kept for stock module
    if "Product" not in out.columns:
        suffix = np.random.randint(100, 999, size=n).astype(str)
        out["Product"] = out["Category"] + " — SKU" + suffix

    out["Stock_Value_Lakhs"] = (out["Current_Stock"] * out["Unit_Cost_Rs"] / 100_000).round(2)
    out["Stock_Status"] = np.where(
        out["Current_Stock"] <= 0, "Out of Stock",
        np.where(out["Current_Stock"] <= out["Reorder_Point"], "Low Stock", "Healthy"),
    )
    # Derived performance columns
    out["Revenue_Per_Footfall"] = (out["Revenue_Lakhs"] / out["Daily_Footfall"].replace(0, np.nan)).round(4)
    out["Margin_Value_Lakhs"]   = (out["Revenue_Lakhs"] * out["Gross_Margin_Pct"] / 100).round(2)

    # ── Profit / Loss columns ─────────────────────────────────────────────────
    # Cost = Revenue * COGS_Pct / 100 (COGS_Pct already in CSV; fallback to 55%)
    if "COGS_Pct" not in out.columns:
        out["COGS_Pct"] = 55.0
    out["COGS_Lakhs"]   = (out["Revenue_Lakhs"] * out["COGS_Pct"] / 100).round(2)
    out["Gross_Profit_Lakhs"] = (out["Revenue_Lakhs"] - out["COGS_Lakhs"]).round(2)
    # Operating expenses estimate (15–20% of revenue)
    np.random.seed(7)
    opex_pct = np.random.uniform(15, 20, size=len(out))
    out["Opex_Lakhs"]   = (out["Revenue_Lakhs"] * opex_pct / 100).round(2)
    out["Net_Profit_Lakhs"] = (out["Gross_Profit_Lakhs"] - out["Opex_Lakhs"]).round(2)
    out["Is_Loss"]      = out["Net_Profit_Lakhs"] < 0
    return out


@st.cache_data
def load_csv(content: bytes) -> pd.DataFrame:
    return pd.read_csv(StringIO(content.decode("utf-8")))


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════
uploaded = st.sidebar.file_uploader("", type=["csv"], help="Upload your retail sales CSV file", label_visibility="collapsed")

try:
    if uploaded is not None:
        df_raw = load_csv(uploaded.read())
    else:
        df_raw = pd.read_csv("store_sales_data.csv")
    df_raw.columns = df_raw.columns.str.strip()
    df_raw = enrich_dataframe(df_raw)
except FileNotFoundError:
    st.markdown("""
    <div style="background:rgba(255,92,122,0.08);border:1px solid rgba(255,92,122,0.2);border-radius:12px;padding:24px;margin-top:2rem;text-align:center;">
      <div style="font-size:32px;margin-bottom:12px;">⚠️</div>
      <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:#FF5C7A;margin-bottom:8px;">Data File Not Found</div>
      <div style="font-size:13px;color:#8892B0;">Please upload a CSV file using the sidebar uploader,<br>or place <code>store_sales_data.csv</code> in the same directory.</div>
    </div>""", unsafe_allow_html=True)
    st.stop()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# Derived filter options
ALL_CATS   = sorted(set(df_raw["Category"].dropna()))
ALL_STORES = sorted(set(df_raw["Store"].dropna()))
ALL_MONTHS = [m for m in MO_ORDER if m in set(df_raw["Month"].dropna())]


# ══════════════════════════════════════════════════════════════════════════════
# REDESIGNED SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
# ── Brand logo ───────────────────────────────────────────────────────────────
# Inject real ambient orb divs — visible across the whole dashboard
st.markdown("""
<div id="amb-orb-1"></div>
<div id="amb-orb-2"></div>
<div id="amb-orb-3"></div>
<div id="amb-orb-4"></div>
<div id="amb-orb-5"></div>
<style>
#amb-orb-1,#amb-orb-2,#amb-orb-3,#amb-orb-4,#amb-orb-5{
    position:fixed;border-radius:50%;pointer-events:none;z-index:0;
    mix-blend-mode:screen;
}
#amb-orb-1{
    width:70vw;height:70vw;
    background:radial-gradient(circle at center,rgba(168,85,247,0.25) 0%,transparent 70%);
    filter:blur(80px);
    top:-25vh;left:-25vw;
    animation:ambOrb1 18s ease-in-out infinite alternate;
}
#amb-orb-2{
    width:65vw;height:65vw;
    background:radial-gradient(circle at center,rgba(245,158,11,0.20) 0%,transparent 70%);
    filter:blur(90px);
    top:15vh;right:-28vw;
    animation:ambOrb2 22s ease-in-out infinite alternate;
}
#amb-orb-3{
    width:55vw;height:55vw;
    background:radial-gradient(circle at center,rgba(244,63,94,0.18) 0%,transparent 70%);
    filter:blur(100px);
    bottom:-18vh;left:20vw;
    animation:ambOrb3 15s ease-in-out infinite alternate;
}
#amb-orb-4{
    width:45vw;height:45vw;
    background:radial-gradient(circle at center,rgba(196,132,252,0.20) 0%,transparent 70%);
    filter:blur(85px);
    bottom:12vh;right:12vw;
    animation:ambOrb4 25s ease-in-out infinite alternate;
}
#amb-orb-5{
    width:30vw;height:30vw;
    background:radial-gradient(circle at center,rgba(251,146,60,0.15) 0%,transparent 70%);
    filter:blur(60px);
    top:40vh;left:35vw;
    animation:ambOrb5 30s ease-in-out infinite alternate;
}
@keyframes ambOrb1{
    0%  {transform:translate(0,0) scale(1);    opacity:0.8;}
    33% {transform:translate(10vw,12vh) scale(1.15);opacity:1;  filter:blur(80px) hue-rotate(50deg);}
    66% {transform:translate(-6vw,7vh) scale(0.95);opacity:0.7;filter:blur(100px) hue-rotate(90deg);}
    100%{transform:translate(8vw,-10vh) scale(1.08);opacity:0.9;filter:blur(80px) hue-rotate(0deg);}
}
@keyframes ambOrb2{
    0%  {transform:translate(0,0) scale(1);    opacity:0.7;}
    50% {transform:translate(-12vw,8vh) scale(1.18);opacity:1;  filter:blur(90px) hue-rotate(70deg);}
    100%{transform:translate(7vw,-12vh) scale(0.92);opacity:0.8;filter:blur(90px) hue-rotate(0deg);}
}
@keyframes ambOrb3{
    0%  {transform:translate(0,0) scale(1);    opacity:0.6;}
    50% {transform:translate(7vw,-10vh) scale(1.25);opacity:0.9; filter:blur(100px) hue-rotate(110deg);}
    100%{transform:translate(-5vw,8vh) scale(0.9); opacity:0.7;filter:blur(100px) hue-rotate(0deg);}
}
@keyframes ambOrb4{
    0%  {transform:translate(0,0) scale(1);    opacity:0.7;}
    50% {transform:translate(-10vw,-12vh) scale(1.15);opacity:1;  filter:blur(85px) hue-rotate(60deg);}
    100%{transform:translate(10vw,7vh) scale(0.98);opacity:0.8; filter:blur(85px) hue-rotate(0deg);}
}
@keyframes ambOrb5{
    0%,100% {transform:translate(0,0); opacity:0.5;}
    50% {transform:translate(5vw,5vh); opacity:0.8; filter:hue-rotate(30deg);}
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style="padding:22px 20px 16px;border-bottom:1px solid rgba(168,85,247,0.15);
     background:linear-gradient(180deg,rgba(168,85,247,0.09) 0%,transparent 100%);">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="display:flex;align-items:center;justify-content:center;animation:pulse-icon 3s ease-in-out infinite;"><img src="data:image/png;base64,{icon_b64}" width="28" style="border-radius:6px; box-shadow: 0 0 16px rgba(168,85,247,0.6);"></div>
    <div>
      <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:#F0EAFF;
           letter-spacing:-0.5px;line-height:1.1;">NEXUS</div>
      <div style="font-size:9px;color:#5A5080;text-transform:uppercase;letter-spacing:2px;margin-top:2px;">Retail Intelligence</div>
    </div>
  </div>
  <div style="margin-top:14px;display:flex;align-items:center;gap:8px;
       background:rgba(168,85,247,0.07);border:1px solid rgba(168,85,247,0.18);
       border-radius:8px;padding:6px 10px;width:fit-content;">
    <div style="width:6px;height:6px;border-radius:50%;background:#A855F7;animation:blink 2s ease-in-out infinite;"></div>
    <span style="font-size:10px;color:#C084FC;font-weight:600;">Live Dashboard Active</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Navigation section ────────────────────────────────────────────────────────
st.sidebar.markdown('<div class="sb-section-label">Navigation</div>', unsafe_allow_html=True)

NAV_OPTIONS = {
    "📊  Store Performance":  ("Store Performance",   "#A855F7", "Revenue · Margins · Traffic"),
    "📦  Stock & Inventory":  ("Stock & Inventory",   "#C084FC", "Health · Alerts · Velocity"),
    "🏷️  Product Analytics":  ("Product Analytics",   "#F59E0B", "Units · Profit · Loss · Stock"),
}

app_mode = st.sidebar.radio(
    "nav",
    list(NAV_OPTIONS.keys()),
    label_visibility="collapsed",
)

# Render nav card descriptions
_nav_label, _nav_color, _nav_desc = NAV_OPTIONS[app_mode]
st.sidebar.markdown(f"""
<div style="margin:4px 0 8px;padding:8px 12px;background:rgba(255,255,255,0.02);
     border-radius:8px;border-left:2px solid {_nav_color};">
  <span style="font-size:11px;color:{_nav_color};font-weight:600;">{_nav_desc}</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

# ── Filters section ───────────────────────────────────────────────────────────
st.sidebar.markdown('<div class="sb-section-label">Filters</div>', unsafe_allow_html=True)

# Category filter with colored indicators
st.sidebar.markdown("""
<div style="font-size:10px;color:#8892B0;font-weight:600;text-transform:uppercase;
     letter-spacing:0.8px;margin-bottom:4px;">Category</div>""", unsafe_allow_html=True)
sel_cats = st.sidebar.multiselect(
    "cat_filter", ALL_CATS, default=ALL_CATS, key="f_cat", label_visibility="collapsed"
)

st.sidebar.markdown("""
<div style="font-size:10px;color:#8892B0;font-weight:600;text-transform:uppercase;
     letter-spacing:0.8px;margin:10px 0 4px;">Store</div>""", unsafe_allow_html=True)
sel_stores = st.sidebar.multiselect(
    "store_filter", ALL_STORES, default=ALL_STORES, key="f_store", label_visibility="collapsed"
)

st.sidebar.markdown("""
<div style="font-size:10px;color:#8892B0;font-weight:600;text-transform:uppercase;
     letter-spacing:0.8px;margin:10px 0 4px;">Month</div>""", unsafe_allow_html=True)
sel_months = st.sidebar.multiselect(
    "month_filter", ALL_MONTHS, default=ALL_MONTHS, key="f_month", label_visibility="collapsed"
)

if not sel_cats or not sel_stores or not sel_months:
    st.warning("⚠️  Select at least one option in every filter to continue.")
    st.stop()

# Apply filters
df = df_raw[
    df_raw["Category"].isin(sel_cats)  &
    df_raw["Store"].isin(sel_stores)   &
    df_raw["Month"].isin(sel_months)
].copy()

if df.empty:
    st.warning("No data matches the selected filters. Please adjust your selections.")
    st.stop()

STORES = sorted(df["Store"].unique())
CATS   = sorted(df["Category"].unique())

st.sidebar.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

# ── Dataset summary card ──────────────────────────────────────────────────────
_total_rev_sb  = df["Revenue_Lakhs"].sum()
_total_prof_sb = df["Net_Profit_Lakhs"].sum()
_prof_color    = "#00E5B8" if _total_prof_sb >= 0 else "#FF5C7A"

st.sidebar.markdown(f"""
<div style="margin:0 0 10px;padding:14px 16px;background:rgba(91,155,248,0.06);
     border:1px solid rgba(91,155,248,0.12);border-radius:12px;">
  <div style="font-size:9px;color:#4A5270;text-transform:uppercase;letter-spacing:1.2px;
       font-weight:700;margin-bottom:10px;">Active Dataset</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
    <div>
      <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:#5B9BF8;">{len(df):,}</div>
      <div style="font-size:10px;color:#4A5270;">records</div>
    </div>
    <div>
      <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:#00E5B8;">₹{_total_rev_sb:.0f}L</div>
      <div style="font-size:10px;color:#4A5270;">revenue</div>
    </div>
    <div>
      <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:#FFAB2E;">{len(STORES)}</div>
      <div style="font-size:10px;color:#4A5270;">stores</div>
    </div>
    <div>
      <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:{_prof_color};">₹{_total_prof_sb:.0f}L</div>
      <div style="font-size:10px;color:#4A5270;">net profit</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── API Server Status ─────────────────────────────────────────────────────────
_API_URL = "http://localhost:8000"
_api_ok  = False
_api_data = {}
if _HAS_REQUESTS:
    try:
        _r = _requests.get(f"{_API_URL}/api/health", timeout=1.5)
        if _r.status_code == 200:
            _api_ok   = True
            _api_data = _r.json()
    except Exception:
        pass

if _api_ok:
    _uptime   = _api_data.get("uptime", "--")
    _srv_time = _api_data.get("server_time", "")[:19].replace("T", " ")
    _rec      = _api_data.get("records_loaded", 0)
    st.sidebar.markdown(f"""
    <div style="background:rgba(0,229,184,0.05);border:1px solid rgba(0,229,184,0.18);
         border-radius:10px;padding:12px 14px;">
      <div style="display:flex;align-items:center;gap:7px;margin-bottom:8px;">
        <div style="width:7px;height:7px;border-radius:50%;background:#00E5B8;
             box-shadow:0 0 6px #00E5B8;animation:blink 2s ease-in-out infinite;"></div>
        <div style="font-size:10px;color:#00E5B8;font-weight:700;text-transform:uppercase;
             letter-spacing:1px;">API Server Online</div>
      </div>
      <div style="font-size:11px;color:#4A5270;line-height:1.8;">
        <span style="color:#8892B0;">Uptime:</span> {_uptime}<br/>
        <span style="color:#8892B0;">Records:</span> {_rec:,}<br/>
        <span style="color:#8892B0;">Time:</span> {_srv_time}
      </div>
      <div style="margin-top:8px;font-size:10px;color:#4A5270;">
        <a href="http://localhost:8000/docs" target="_blank"
           style="color:#5B9BF8;text-decoration:none;">Open API Docs /docs</a>
      </div>
    </div>""", unsafe_allow_html=True)
else:
    _reason = "requests not installed" if not _HAS_REQUESTS else "server not reachable"
    st.sidebar.markdown(f"""
    <div style="background:rgba(255,92,122,0.05);border:1px solid rgba(255,92,122,0.18);
         border-radius:10px;padding:10px 14px;">
      <div style="display:flex;align-items:center;gap:7px;">
        <div style="width:7px;height:7px;border-radius:50%;background:#FF5C7A;opacity:0.7;"></div>
        <div style="font-size:10px;color:#FF5C7A;font-weight:700;text-transform:uppercase;
             letter-spacing:1px;">API Offline</div>
      </div>
      <div style="font-size:10px;color:#4A5270;margin-top:6px;">
        Run: <code style="color:#8892B0;">python server.py</code>
      </div>
    </div>""", unsafe_allow_html=True)


# ── Sticky Topbar ─────────────────────────────────────────────────────────────
import datetime as _dtnow
_ts = _dtnow.datetime.now().strftime("%H:%M")
_pill_sp  = "active" if "Store Performance" in app_mode else ""
_pill_si  = "active" if "Stock" in app_mode else ""
_pill_pa  = "active" if "Product" in app_mode else ""

st.markdown(f"""
<div id="nexus-topbar">
  <div class="brand">
    <img src="data:image/png;base64,{icon_b64}" width="22" class="brand-icon" style="border-radius:4px;">
    <div>
      <div class="brand-name">NEXUS</div>
      <div class="brand-sub">Retail Intelligence</div>
    </div>
  </div>

  <div class="nav-pills">
    <div class="pill {_pill_sp}">📊 Store Performance</div>
    <div class="pill {_pill_si}">📦 Stock &amp; Inventory</div>
    <div class="pill {_pill_pa}">🏷️ Product Analytics</div>
  </div>

  <div class="meta">
    <div class="meta-item">
      <span class="live-dot"></span>
      <span style="color:#00E5B8;font-weight:600;">Live</span>
    </div>
    <div class="meta-item">
      <span>🗃</span>
      <span style="color:#EDF0FF;font-weight:600;">{len(df):,}</span>
      <span>records</span>
    </div>
    <div class="meta-item">
      <span>🏬</span>
      <span>{len(STORES)} stores</span>
    </div>
    <div class="meta-item" style="font-size:10px;opacity:0.5;">{_ts} IST</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE A — STORE PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
def render_store_performance():

    # Sidebar metric picker
    st.sidebar.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sb-section-label">Chart Options</div>', unsafe_allow_html=True)
    st.sidebar.markdown("""<div style="font-size:10px;color:#8892B0;font-weight:600;text-transform:uppercase;
         letter-spacing:0.8px;margin-bottom:4px;">Primary Metric</div>""", unsafe_allow_html=True)
    sel_label = st.sidebar.selectbox("metric_pick", list(STAT_MAP.keys()), label_visibility="collapsed")
    sel_stat  = STAT_MAP[sel_label]

    # Page header
    page_header(
        "Store Performance",
        "Revenue · Gross Margins · Traffic · Conversion · Basket Size",
        "📊", "#5B9BF8", "91,155,248", len(df)
    )

    # ── Aggregate by store
    agg = df.groupby("Store").agg(
        Total_Revenue   = ("Revenue_Lakhs",     "sum"),
        Target          = ("Annual_Target_Lakhs","first"),
        Avg_Margin      = ("Gross_Margin_Pct",   "mean"),
        Avg_Conv        = ("Conversion_Rate_Pct","mean"),
        Avg_Basket      = ("Avg_Basket_Size_Rs", "mean"),
        Total_Units     = ("Units_Sold",         "sum"),
        Total_Footfall  = ("Daily_Footfall",     "sum"),
        Margin_Value    = ("Margin_Value_Lakhs", "sum"),
    ).reset_index()
    agg["Attainment_Pct"] = (agg["Total_Revenue"] / agg["Target"].replace(0, np.nan) * 100).round(1).fillna(0)
    total_rev    = agg["Total_Revenue"].sum()
    total_target = agg["Target"].sum()
    total_margin = df["Margin_Value_Lakhs"].sum()

    # ━━━ KPI ROW ━━━
    section_header("Key Performance Indicators")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Revenue",      f"₹{total_rev:.1f}L")
    k2.metric("Target Attainment",  f"{total_rev / total_target * 100 if total_target else 0:.1f}%")
    k3.metric("Gross Margin Value", f"₹{total_margin:.1f}L")
    k4.metric("Avg Conversion",     f"{df['Conversion_Rate_Pct'].mean():.1f}%")
    k5.metric("Avg Basket Size",    f"₹{df['Avg_Basket_Size_Rs'].mean():.0f}")
    k6.metric("Total Units Sold",   f"{df['Units_Sold'].sum():,}")

    # ━━━ ATTAINMENT CARDS ━━━
    section_header("Target Attainment per Store", "Revenue vs Annual Target")
    cols = st.columns(len(agg))
    for col, (_, row) in zip(cols, agg.iterrows()):
        with col:
            store_attainment_card(
                row["Store"],
                row["Attainment_Pct"],
                STORE_COLORS.get(row["Store"], "#5B9BF8"),
            )

    st.divider()

    # ━━━ REVENUE ANALYSIS ━━━
    section_header("Revenue Analysis", f"Currently viewing: {sel_label}")
    c1, c2 = st.columns([3, 2])

    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=agg["Store"], y=agg["Total_Revenue"],
            name="Actual Revenue",
            marker_color=[STORE_COLORS.get(s, "#5B9BF8") for s in agg["Store"]],
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:.1f}L<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=agg["Store"], y=agg["Target"],
            name="Annual Target",
            mode="markers",
            marker=dict(symbol="line-ew", size=22, color="#EDF0FF",
                        line=dict(width=2.5, color="#EDF0FF")),
            hovertemplate="<b>%{x}</b><br>Target: ₹%{y:.1f}L<extra></extra>",
        ))
        st.plotly_chart(pt(fig, "Revenue vs Annual Target"), width='stretch')

    with c2:
        cat_sum = df.groupby("Category")["Revenue_Lakhs"].sum().reset_index()
        fig = px.pie(
            cat_sum, names="Category", values="Revenue_Lakhs",
            hole=0.58, color="Category", color_discrete_map=CAT_COLORS,
        )
        fig.update_traces(
            textfont_color="#EDF0FF", textfont_size=11,
            hovertemplate="<b>%{label}</b><br>₹%{value:.1f}L (%{percent})<extra></extra>",
        )
        st.plotly_chart(pt(fig, "Category Revenue Share"), width='stretch')

    # ━━━ TREND + HEATMAP ━━━
    c3, c4 = st.columns(2)
    with c3:
        months_active = [m for m in ALL_MONTHS if m in sel_months]
        trend_df = df.groupby(["Month","Category"])[sel_stat].mean().unstack()
        trend_df = trend_df.reindex(months_active)
        fig = px.line(trend_df, markers=True, color_discrete_map=CAT_COLORS)
        fig.update_traces(line_width=2.2, marker_size=7)
        st.plotly_chart(pt(fig, f"{sel_label} — Monthly Trend by Category"), width='stretch')

    with c4:
        pivot = df.pivot_table(index="Store", columns="Category", values=sel_stat, aggfunc="mean").fillna(0)
        fig = px.imshow(
            pivot, aspect="auto", text_auto=".1f",
            color_continuous_scale=[[0,"#0D1220"],[0.45,"#5B9BF8"],[1,"#00E5B8"]],
        )
        fig.update_coloraxes(showscale=False)
        fig.update_traces(textfont=dict(color="#EDF0FF", size=11))
        st.plotly_chart(pt(fig, f"{sel_label} — Store × Category Heatmap"), width='stretch')

    st.divider()

    # ━━━ SCATTER + MARGIN BAR ━━━
    section_header("Distribution & Performance Drivers")
    c5, c6 = st.columns(2)

    with c5:
        fig = px.scatter(
            df, x="Daily_Footfall", y=sel_stat,
            color="Store", color_discrete_map=STORE_COLORS,
            size="Avg_Basket_Size_Rs",
            hover_data=["Category", "Month"],
            hover_name="Store",
        )
        fig.update_traces(marker_line_width=0, marker_opacity=0.8)
        st.plotly_chart(pt(fig, f"Daily Footfall vs {sel_label}"), width='stretch')

    with c6:
        margin_by_store = df.groupby("Store")["Margin_Value_Lakhs"].sum().reset_index().sort_values("Margin_Value_Lakhs")
        fig = px.bar(
            margin_by_store, x="Margin_Value_Lakhs", y="Store",
            orientation="h", color="Store", color_discrete_map=STORE_COLORS,
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(pt(fig, "Gross Margin Value by Store (₹ Lakhs)"), width='stretch')

    st.divider()

    # ━━━ DEEP DIVE TABS ━━━
    section_header("Deep Dive Analysis")
    tab1, tab2, tab3, tab4 = st.tabs(["📈  Monthly Store Trends", "📦  Category Breakdown", "🔢  Ranked Comparison", "🌡️  Correlation Matrix"])

    with tab1:
        store_trend = df.groupby(["Month","Store"])[sel_stat].mean().unstack()
        store_trend = store_trend.reindex([m for m in ALL_MONTHS if m in sel_months])
        fig = px.line(store_trend, markers=True, color_discrete_map=STORE_COLORS)
        fig.update_traces(line_width=2.2, marker_size=7)
        st.plotly_chart(pt(fig, f"{sel_label} — Monthly Trend by Store", height=380), width='stretch')

    with tab2:
        cc1, cc2 = st.columns(2)
        with cc1:
            fig = px.box(
                df, x="Category", y=sel_stat,
                color="Category", color_discrete_map=CAT_COLORS,
                points="outliers",
            )
            fig.update_traces(marker_size=5, line_width=1.5)
            st.plotly_chart(pt(fig, f"{sel_label} Distribution by Category", height=360), width='stretch')
        with cc2:
            cat_agg = df.groupby(["Store","Category"])["Revenue_Lakhs"].sum().reset_index()
            fig = px.bar(
                cat_agg, x="Store", y="Revenue_Lakhs",
                color="Category", color_discrete_map=CAT_COLORS,
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(pt(fig, "Revenue Stacks — Store × Category", height=360), width='stretch')

    with tab3:
        rank_by = st.radio("Rank by entity:", ["Store", "Category", "Month"], horizontal=True, key="rank_radio")
        rc1, rc2 = st.columns(2)
        ranked = df.groupby(rank_by)[sel_stat].mean().sort_values().reset_index()
        cmap_r = CAT_COLORS if rank_by == "Category" else STORE_COLORS
        with rc1:
            fig = px.bar(
                ranked, x=sel_stat, y=rank_by,
                orientation="h", color=rank_by,
                color_discrete_map=cmap_r,
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(pt(fig, f"Mean {sel_label} Ranking", height=340), width='stretch')
        with rc2:
            fig = px.pie(
                df, names=rank_by, values=sel_stat,
                hole=0.45, color=rank_by,
                color_discrete_map=cmap_r,
            )
            fig.update_traces(textfont_color="#EDF0FF", textfont_size=11)
            st.plotly_chart(pt(fig, f"{sel_label} Share Composition", height=340), width='stretch')

    with tab4:
        num_cols = ["Revenue_Lakhs","Gross_Margin_Pct","Daily_Footfall","Conversion_Rate_Pct","Avg_Basket_Size_Rs","Units_Sold"]
        corr = df[num_cols].corr().round(2)
        fig = px.imshow(
            corr, text_auto=True, aspect="auto",
            color_continuous_scale=[[0,"#FF5C7A"],[0.5,"#0D1220"],[1,"#5B9BF8"]],
            zmin=-1, zmax=1,
        )
        fig.update_coloraxes(showscale=False)
        fig.update_traces(textfont=dict(color="#EDF0FF", size=12))
        st.plotly_chart(pt(fig, "Pearson Correlation Matrix — All Metrics", height=420), width='stretch')

    st.divider()

    # ━━━ CONVERSION FUNNEL PROXY ━━━
    section_header("Conversion & Basket Intelligence")
    cf1, cf2, cf3 = st.columns(3)
    with cf1:
        fig = px.scatter(
            df, x="Conversion_Rate_Pct", y="Avg_Basket_Size_Rs",
            color="Category", color_discrete_map=CAT_COLORS,
            size="Revenue_Lakhs",
            hover_name="Store", hover_data=["Month"],
        )
        fig.update_traces(marker_line_width=0, marker_opacity=0.85)
        st.plotly_chart(pt(fig, "Conversion Rate vs Basket Size", height=320), width='stretch')

    with cf2:
        basket_cat = df.groupby("Category")["Avg_Basket_Size_Rs"].mean().reset_index().sort_values("Avg_Basket_Size_Rs")
        fig = px.bar(
            basket_cat, x="Avg_Basket_Size_Rs", y="Category",
            orientation="h", color="Category", color_discrete_map=CAT_COLORS,
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(pt(fig, "Avg Basket Size by Category (₹)", height=320), width='stretch')

    with cf3:
        conv_store = df.groupby("Store")["Conversion_Rate_Pct"].mean().reset_index().sort_values("Conversion_Rate_Pct")
        fig = px.bar(
            conv_store, x="Conversion_Rate_Pct", y="Store",
            orientation="h", color="Store", color_discrete_map=STORE_COLORS,
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(pt(fig, "Avg Conversion Rate by Store (%)", height=320), width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# MODULE B — STOCK & INVENTORY
# ══════════════════════════════════════════════════════════════════════════════
def render_stock_analysis():

    page_header(
        "Stock & Inventory",
        "Health Index · Reorder Alerts · Capital Exposure · Velocity Analysis",
        "📦", "#A470FF", "164,112,255", len(df)
    )

    # Aggregates
    total_val   = df["Stock_Value_Lakhs"].sum()
    total_units = df["Current_Stock"].sum()
    n_oos       = len(df[df["Stock_Status"] == "Out of Stock"])
    n_low       = len(df[df["Stock_Status"] == "Low Stock"])
    n_healthy   = len(df[df["Stock_Status"] == "Healthy"])
    total_skus  = len(df)
    health_pct  = n_healthy / total_skus * 100 if total_skus else 0

    # ━━━ KPI ROW ━━━
    section_header("Inventory Health Snapshot")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Vault Value",        f"₹{total_val:.1f}L")
    k2.metric("Units On Hand",      f"{total_units:,}")
    k3.metric("Health Rate",        f"{health_pct:.0f}%",   delta=f"{n_healthy} SKUs healthy")
    k4.metric("Low Stock Alerts",   f"{n_low}",             delta=f"−{n_low} near threshold", delta_color="inverse")
    k5.metric("Out of Stock",       f"{n_oos}",             delta=f"−{n_oos} critical",       delta_color="inverse")
    k6.metric("Total SKU Lines",    f"{total_skus}")

    st.divider()

    # ━━━ PRODUCT COMPARISON ━━━
    section_header(
        "Product Stock Comparison",
        "Select SKUs to compare current stock vs sales velocity vs reorder threshold",
        "#A470FF",
    )
    all_prods = sorted(df["Product"].unique().tolist())
    sel_prods = st.multiselect(
        "Select products to compare:",
        all_prods,
        default=all_prods[:min(5, len(all_prods))],
        key="prod_compare",
    )

    if sel_prods:
        comp = (
            df[df["Product"].isin(sel_prods)]
            .groupby("Product")
            .agg(
                Current_Stock    = ("Current_Stock",     "sum"),
                Reorder_Point    = ("Reorder_Point",     "sum"),
                Units_Sold       = ("Units_Sold",        "sum"),
                Stock_Value_Lakhs= ("Stock_Value_Lakhs", "sum"),
                Category         = ("Category",          "first"),
            )
            .reset_index()
        )
        comp["Status"] = np.where(
            comp["Current_Stock"] <= 0, "Out of Stock",
            np.where(comp["Current_Stock"] <= comp["Reorder_Point"], "Low Stock", "Healthy"),
        )

        pc1, pc2 = st.columns([1, 2])
        with pc1:
            def _row_style(row):
                if row["Current_Stock"] <= 0:
                    return ["color:#FF5C7A; font-weight:600"] * len(row)
                elif row["Current_Stock"] <= row["Reorder_Point"]:
                    return ["color:#FFAB2E; font-weight:500"] * len(row)
                return [""] * len(row)

            display_cols = ["Product","Category","Current_Stock","Reorder_Point","Units_Sold","Status"]
            st.dataframe(
                comp[display_cols].style.apply(_row_style, axis=1),
                width='stretch', hide_index=True,
            )

        with pc2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=comp["Product"], y=comp["Current_Stock"],
                name="Current Stock",
                marker_color="#5B9BF8", marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>Stock: %{y:,}<extra></extra>",
            ))
            fig.add_trace(go.Bar(
                x=comp["Product"], y=comp["Units_Sold"],
                name="Units Sold",
                marker_color="#00E5B8", opacity=0.65, marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>Sold: %{y:,}<extra></extra>",
            ))
            fig.add_trace(go.Scatter(
                x=comp["Product"], y=comp["Reorder_Point"],
                name="Reorder Point",
                mode="markers+lines",
                marker=dict(size=11, color="#FFAB2E", symbol="triangle-down"),
                line=dict(dash="dash", color="#FFAB2E", width=1.5),
                hovertemplate="<b>%{x}</b><br>Reorder at: %{y:,}<extra></extra>",
            ))
            fig.update_layout(barmode="group")
            st.plotly_chart(pt(fig, "Stock · Sales · Reorder Point Comparison", height=360), width='stretch')
    else:
        st.info("Select at least one product to see the comparison.")

    st.divider()

    # ━━━ VELOCITY QUADRANT ━━━
    section_header(
        "Inventory Velocity Quadrant",
        "Lower-right = high sales / low stock (restock risk)  ·  Upper-left = low sales / high stock (dead capital)",
        "#A470FF",
    )
    fig = px.scatter(
        df, x="Units_Sold", y="Current_Stock",
        color="Category", size="Stock_Value_Lakhs",
        color_discrete_map=CAT_COLORS,
        hover_name="Product",
        hover_data=["Stock_Status", "Store", "Stock_Value_Lakhs"],
    )
    med_stock = df["Current_Stock"].median()
    med_sales = df["Units_Sold"].median()
    fig.add_hline(y=med_stock, line_dash="dot", line_color="rgba(255,255,255,0.12)",
                  annotation_text="Median Stock", annotation_font_color="#4A5270", annotation_font_size=10)
    fig.add_vline(x=med_sales, line_dash="dot", line_color="rgba(255,255,255,0.12)",
                  annotation_text="Median Sales", annotation_font_color="#4A5270", annotation_font_size=10)
    fig.update_traces(marker_line_width=0, marker_opacity=0.85)
    st.plotly_chart(pt(fig, "Sales Velocity vs Current Stock Level", height=420), width='stretch')

    st.divider()

    # ━━━ DISTRIBUTION ━━━
    section_header("Stock Distribution & Capital Exposure")
    d1, d2 = st.columns(2)

    with d1:
        store_st = df.groupby(["Store","Stock_Status"]).size().reset_index(name="Count")
        fig = px.bar(
            store_st, x="Store", y="Count",
            color="Stock_Status", barmode="stack",
            color_discrete_map=STATUS_COLORS,
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(pt(fig, "Stock Status Profile per Store", height=340), width='stretch')

    with d2:
        cat_val = df.groupby("Category")["Stock_Value_Lakhs"].sum().reset_index()
        fig = px.pie(
            cat_val, names="Category", values="Stock_Value_Lakhs",
            hole=0.52, color="Category", color_discrete_map=CAT_COLORS,
        )
        fig.update_traces(
            textfont_color="#EDF0FF", textfont_size=11,
            hovertemplate="<b>%{label}</b><br>₹%{value:.2f}L (%{percent})<extra></extra>",
        )
        st.plotly_chart(pt(fig, "Capital Frozen by Category (₹ Lakhs)", height=340), width='stretch')

    # ━━━ STORE × CATEGORY STOCK HEATMAP ━━━
    d3, d4 = st.columns(2)
    with d3:
        pivot_stock = df.pivot_table(index="Store", columns="Category", values="Current_Stock", aggfunc="sum").fillna(0)
        fig = px.imshow(
            pivot_stock, aspect="auto", text_auto=".0f",
            color_continuous_scale=[[0,"#0D1220"],[0.5,"#A470FF"],[1,"#00E5B8"]],
        )
        fig.update_coloraxes(showscale=False)
        fig.update_traces(textfont=dict(color="#EDF0FF", size=11))
        st.plotly_chart(pt(fig, "Total Units On Hand — Store × Category", height=300), width='stretch')

    with d4:
        pivot_val = df.pivot_table(index="Store", columns="Category", values="Stock_Value_Lakhs", aggfunc="sum").fillna(0).round(2)
        fig = px.imshow(
            pivot_val, aspect="auto", text_auto=".1f",
            color_continuous_scale=[[0,"#0D1220"],[0.5,"#FFAB2E"],[1,"#FF5C7A"]],
        )
        fig.update_coloraxes(showscale=False)
        fig.update_traces(textfont=dict(color="#EDF0FF", size=11))
        st.plotly_chart(pt(fig, "Stock Value (₹L) — Store × Category", height=300), width='stretch')

    st.divider()

    # ━━━ CRITICAL RESTOCK QUEUE ━━━
    section_header(
        "Critical Restock Queue",
        "Items at or below reorder threshold — sorted by urgency (ascending stock level)",
        "#FF5C7A",
    )
    crit = (
        df[df["Stock_Status"].isin(["Out of Stock","Low Stock"])]
        .sort_values("Current_Stock")
        [["Store","Category","Product","Current_Stock","Reorder_Point","Units_Sold","Stock_Value_Lakhs","Stock_Status"]]
        .head(25)
    )

    if not crit.empty:
        def _crit_style(val):
            if val == "Out of Stock": return "color:#FF5C7A; font-weight:700"
            if val == "Low Stock":    return "color:#FFAB2E; font-weight:600"
            return ""

        st.dataframe(
            crit.style.map(_crit_style, subset=["Stock_Status"]),
            width='stretch',
            hide_index=True,
        )

        oos_val = crit[crit["Stock_Status"]=="Out of Stock"]["Stock_Value_Lakhs"].sum()
        low_val = crit[crit["Stock_Status"]=="Low Stock"]["Stock_Value_Lakhs"].sum()
        st.markdown(f"""
        <div style="display:flex;gap:12px;margin-top:12px;flex-wrap:wrap;">
          <div style="background:rgba(255,92,122,0.07);border:1px solid rgba(255,92,122,0.15);border-radius:8px;padding:10px 16px;">
            <span style="font-size:10px;color:#FF5C7A;text-transform:uppercase;letter-spacing:0.8px;font-weight:600;">Out of Stock</span>
            <span style="font-family:'Syne',sans-serif;font-size:16px;font-weight:800;color:#FF5C7A;margin-left:12px;">{n_oos} SKUs</span>
          </div>
          <div style="background:rgba(255,171,46,0.07);border:1px solid rgba(255,171,46,0.15);border-radius:8px;padding:10px 16px;">
            <span style="font-size:10px;color:#FFAB2E;text-transform:uppercase;letter-spacing:0.8px;font-weight:600;">Low Stock</span>
            <span style="font-family:'Syne',sans-serif;font-size:16px;font-weight:800;color:#FFAB2E;margin-left:12px;">{n_low} SKUs</span>
          </div>
          <div style="background:rgba(91,155,248,0.07);border:1px solid rgba(91,155,248,0.15);border-radius:8px;padding:10px 16px;">
            <span style="font-size:10px;color:#5B9BF8;text-transform:uppercase;letter-spacing:0.8px;font-weight:600;">Capital at Risk</span>
            <span style="font-family:'Syne',sans-serif;font-size:16px;font-weight:800;color:#5B9BF8;margin-left:12px;">₹{oos_val+low_val:.1f}L</span>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.success("✅  All SKU lines are currently above their respective reorder thresholds.")

    st.divider()

    # ━━━ REORDER ANALYSIS ━━━
    section_header("Reorder Gap Analysis", "Difference between current stock and reorder point")
    df_gap = df.copy()
    df_gap["Stock_Gap"] = df_gap["Current_Stock"] - df_gap["Reorder_Point"]
    df_gap_top = df_gap.nsmallest(20, "Stock_Gap")[["Store","Category","Product","Current_Stock","Reorder_Point","Stock_Gap","Stock_Status"]]

    ga1, ga2 = st.columns([2, 1])
    with ga1:
        fig = px.bar(
            df_gap_top.sort_values("Stock_Gap"),
            x="Stock_Gap", y="Product",
            color="Stock_Status",
            color_discrete_map=STATUS_COLORS,
            orientation="h",
        )
        fig.add_vline(x=0, line_color="rgba(255,255,255,0.2)", line_width=1)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(pt(fig, "Stock Gap (Current − Reorder Point) — Bottom 20", height=420), width='stretch')

    with ga2:
        cat_gap = df_gap.groupby("Category")["Stock_Gap"].mean().reset_index().sort_values("Stock_Gap")
        fig = px.bar(
            cat_gap, x="Stock_Gap", y="Category",
            orientation="h", color="Category", color_discrete_map=CAT_COLORS,
        )
        fig.add_vline(x=0, line_color="rgba(255,255,255,0.2)", line_width=1)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(pt(fig, "Avg Stock Gap by Category", height=300), width='stretch')


# ══════════════════════════════════════════════════════════════════════════════
# MODULE C — PRODUCT ANALYTICS  (NEW)
# ══════════════════════════════════════════════════════════════════════════════
def render_product_analytics():

    page_header(
        "Product Analytics",
        "Units Sold · Profit & Loss · Stock Status · Category Deep Dive",
        "🏷️", "#00E5B8", "0,229,184", len(df)
    )

    # ── Category + Product selector in sidebar ───────────────────────────────
    st.sidebar.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sb-section-label">Product Filters</div>', unsafe_allow_html=True)

    # Focus Category
    st.sidebar.markdown("""
<div style="font-size:10px;color:#9A8FBB;font-weight:600;text-transform:uppercase;
     letter-spacing:0.8px;margin-bottom:4px;">Focus Category</div>""", unsafe_allow_html=True)

    focus_cat = st.sidebar.selectbox(
        "focus_cat",
        ["All Categories"] + list(CATS),
        label_visibility="collapsed",
        key="pa_focus_cat",
    )

    # ── Sub-Product filter (dynamic based on category selection) ──────────────
    icon_map = {"Electronics":"💻","Apparel":"👕","Home & Living":"🏠","Groceries":"🛒","Beauty":"💄"}
    if focus_cat == "All Categories":
        _available_products = [p for prods in PRODUCT_CATALOG.values() for p in prods]
    else:
        _available_products = PRODUCT_CATALOG.get(focus_cat, [])

    st.sidebar.markdown("""
<div style="font-size:10px;color:#9A8FBB;font-weight:600;text-transform:uppercase;
     letter-spacing:0.8px;margin:10px 0 4px;">Products</div>""", unsafe_allow_html=True)

    sel_products = st.sidebar.multiselect(
        "product_filter",
        options=_available_products,
        default=_available_products,
        key="pa_products",
        label_visibility="collapsed",
    )

    if not sel_products:
        st.warning("⚠️  Select at least one product to continue.")
        return

    # Category color pills in sidebar
    st.sidebar.markdown('<div style="margin-top:10px;">', unsafe_allow_html=True)
    for cat in CATS:
        c = CAT_COLORS.get(cat, "#A855F7")
        icon = icon_map.get(cat, "📦")
        active_style = f"border-color:{c};background:rgba(168,85,247,0.06);" if focus_cat == cat else ""
        st.sidebar.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;padding:5px 8px;border-radius:8px;
             border:1px solid transparent;{active_style}margin-bottom:4px;">
          <div style="width:8px;height:8px;border-radius:50%;background:{c};flex-shrink:0;"></div>
          <span style="font-size:11px;color:#9A8FBB;">{icon} {cat}</span>
        </div>""", unsafe_allow_html=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Filter data to focused category and selected sub-products
    df_focus = df if focus_cat == "All Categories" else df[df["Category"] == focus_cat].copy()
    df_focus = df_focus[df_focus["SubProduct"].isin(sel_products)].copy()

    if df_focus.empty:
        st.warning("No data for the selected category/products. Please adjust filters.")
        return

    # ── Aggregate by SubProduct ───────────────────────────────────────────────
    prod_agg = df_focus.groupby(["Category","SubProduct"]).agg(
        Units_Sold       = ("Units_Sold",           "sum"),
        Revenue          = ("Revenue_Lakhs",         "sum"),
        Gross_Profit     = ("Gross_Profit_Lakhs",    "sum"),
        Net_Profit       = ("Net_Profit_Lakhs",      "sum"),
        COGS             = ("COGS_Lakhs",            "sum"),
        Opex             = ("Opex_Lakhs",            "sum"),
        Current_Stock    = ("Current_Stock",         "sum"),
        Stock_Value      = ("Stock_Value_Lakhs",     "sum"),
        Loss_Count       = ("Is_Loss",               "sum"),
        Total_Rows       = ("Units_Sold",            "count"),
    ).reset_index()
    prod_agg["Profit_Margin_Pct"] = (prod_agg["Net_Profit"] / prod_agg["Revenue"].replace(0, np.nan) * 100).round(1).fillna(0)
    prod_agg["Is_Net_Loss"]       = prod_agg["Net_Profit"] < 0
    prod_agg["Stock_Status_Grp"]  = np.where(prod_agg["Current_Stock"] <= 0, "Out of Stock",
                                    np.where(prod_agg["Current_Stock"] < prod_agg["Units_Sold"] * 0.3, "Low Stock", "Healthy"))

    total_units_sold  = prod_agg["Units_Sold"].sum()
    total_revenue     = prod_agg["Revenue"].sum()
    total_net_profit  = prod_agg["Net_Profit"].sum()
    total_gross_prof  = prod_agg["Gross_Profit"].sum()
    n_products        = len(prod_agg)
    n_loss_prods      = prod_agg["Is_Net_Loss"].sum()
    n_oos_prods       = (prod_agg["Stock_Status_Grp"] == "Out of Stock").sum()
    n_low_prods       = (prod_agg["Stock_Status_Grp"] == "Low Stock").sum()

    # ━━━ KPI SUMMARY BANNER ━━━
    section_header("Product Performance Overview", f"{'All Categories' if focus_cat == 'All Categories' else focus_cat} · {n_products} products tracked")

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Units Sold",   f"{total_units_sold:,}")
    k2.metric("Total Revenue",      f"₹{total_revenue:.1f}L")
    k3.metric("Gross Profit",       f"₹{total_gross_prof:.1f}L")
    _p_color_delta = "normal" if total_net_profit >= 0 else "inverse"
    k4.metric("Net Profit",         f"₹{total_net_profit:.1f}L", delta=f"{'▲' if total_net_profit >= 0 else '▼'} {'Profitable' if total_net_profit >= 0 else 'Loss'}", delta_color=_p_color_delta)
    k5.metric("Loss-Making Products", f"{n_loss_prods}", delta=f"out of {n_products}", delta_color="inverse" if n_loss_prods > 0 else "normal")
    k6.metric("Out of Stock",       f"{n_oos_prods}", delta=f"{n_low_prods} low stock", delta_color="inverse" if n_oos_prods > 0 else "normal")

    st.divider()

    # ━━━ CATEGORY OVERVIEW CARDS ━━━
    section_header("Category Breakdown", "Products organized by category")
    categories_to_show = CATS if focus_cat == "All Categories" else [focus_cat]

    for cat in categories_to_show:
        cat_color = CAT_COLORS.get(cat, "#5B9BF8")
        cat_rgb   = {"Electronics":"91,155,248","Apparel":"0,229,184","Home & Living":"255,92,122","Groceries":"255,171,46","Beauty":"164,112,255"}.get(cat,"91,155,248")
        cat_icon  = {"Electronics":"💻","Apparel":"👕","Home & Living":"🏠","Groceries":"🛒","Beauty":"💄"}.get(cat,"📦")
        cat_df    = prod_agg[prod_agg["Category"] == cat]
        if cat_df.empty:
            continue

        cat_total_units  = cat_df["Units_Sold"].sum()
        cat_total_rev    = cat_df["Revenue"].sum()
        cat_total_profit = cat_df["Net_Profit"].sum()
        cat_n_loss       = cat_df["Is_Net_Loss"].sum()

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba({cat_rgb},0.06) 0%,rgba(13,18,32,0.8) 100%);
             border:1px solid rgba({cat_rgb},0.18);border-radius:16px;padding:20px 24px;margin:12px 0;">
          <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;">
            <div style="width:44px;height:44px;background:rgba({cat_rgb},0.12);border:1px solid rgba({cat_rgb},0.25);
                 border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;">{cat_icon}</div>
            <div>
              <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:#EDF0FF;">{cat}</div>
              <div style="font-size:11px;color:#4A5270;margin-top:2px;">{len(cat_df)} products tracked</div>
            </div>
            <div style="margin-left:auto;display:flex;gap:16px;text-align:right;">
              <div>
                <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:{cat_color};">{cat_total_units:,}</div>
                <div style="font-size:10px;color:#4A5270;text-transform:uppercase;letter-spacing:0.8px;">Units Sold</div>
              </div>
              <div>
                <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:#EDF0FF;">₹{cat_total_rev:.1f}L</div>
                <div style="font-size:10px;color:#4A5270;text-transform:uppercase;letter-spacing:0.8px;">Revenue</div>
              </div>
              <div>
                <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;
                     color:{'#00E5B8' if cat_total_profit>=0 else '#FF5C7A'};">₹{cat_total_profit:.1f}L</div>
                <div style="font-size:10px;color:#4A5270;text-transform:uppercase;letter-spacing:0.8px;">Net {'Profit' if cat_total_profit>=0 else 'Loss'}</div>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Product grid inside category
        products = cat_df.sort_values("Units_Sold", ascending=False)
        cols_per_row = 5
        prod_list = products.to_dict("records")

        for row_start in range(0, len(prod_list), cols_per_row):
            cols = st.columns(cols_per_row)
            for ci, prod in enumerate(prod_list[row_start : row_start + cols_per_row]):
                with cols[ci]:
                    pname       = prod["SubProduct"]
                    pcolor      = PRODUCT_COLORS.get(pname, cat_color)
                    units       = prod["Units_Sold"]
                    net_p       = prod["Net_Profit"]
                    stock       = prod["Current_Stock"]
                    stock_st    = prod["Stock_Status_Grp"]
                    margin_pct  = prod["Profit_Margin_Pct"]
                    st_color    = {"Healthy":"#00E5B8","Low Stock":"#FFAB2E","Out of Stock":"#FF5C7A"}.get(stock_st, "#4A5270")
                    pf_color    = "#00E5B8" if net_p >= 0 else "#FF5C7A"
                    pf_label    = f"▲ ₹{net_p:.1f}L" if net_p >= 0 else f"▼ ₹{abs(net_p):.1f}L"

                    st.markdown(f"""
                    <div style="background:rgba(13,18,32,0.9);border:1px solid rgba(255,255,255,0.07);
                         border-top:2px solid {pcolor};border-radius:12px;padding:14px 12px;
                         transition:all 0.2s;text-align:center;">
                      <div style="font-size:9px;color:#4A5270;text-transform:uppercase;letter-spacing:0.8px;
                           font-weight:600;margin-bottom:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{pname}</div>
                      <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:{pcolor};line-height:1.1;">{units:,}</div>
                      <div style="font-size:10px;color:#4A5270;margin-bottom:8px;">units sold</div>
                      <div style="height:1px;background:rgba(255,255,255,0.05);margin:6px 0;"></div>
                      <div style="font-size:12px;font-weight:700;color:{pf_color};">{pf_label}</div>
                      <div style="font-size:10px;color:#4A5270;">net p&l · {margin_pct:.1f}%</div>
                      <div style="height:1px;background:rgba(255,255,255,0.05);margin:6px 0;"></div>
                      <div style="display:flex;align-items:center;justify-content:center;gap:4px;">
                        <div style="width:5px;height:5px;border-radius:50%;background:{st_color};"></div>
                        <span style="font-size:10px;color:{st_color};font-weight:600;">{stock_st}</span>
                      </div>
                      <div style="font-size:10px;color:#4A5270;">{stock:,} units</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    st.divider()

    # ━━━ STATISTICAL GRAPHS SECTION ━━━
    section_header("Statistical Analysis", "Deep-dive charts: units sold, profit, loss, stock status", "#00E5B8")

    tab_units, tab_profit, tab_loss, tab_stock = st.tabs([
        "📈  Units Sold", "💰  Profit Analysis", "📉  Loss Analysis", "📦  Stock Status"
    ])

    # ── TAB 1: Units Sold ─────────────────────────────────────────────────────
    with tab_units:
        su1, su2 = st.columns(2)

        with su1:
            top_prods = prod_agg.sort_values("Units_Sold", ascending=True).tail(15)
            colors_bar = [PRODUCT_COLORS.get(p, "#5B9BF8") for p in top_prods["SubProduct"]]
            fig = go.Figure(go.Bar(
                x=top_prods["Units_Sold"],
                y=top_prods["SubProduct"],
                orientation="h",
                marker_color=colors_bar,
                marker_line_width=0,
                hovertemplate="<b>%{y}</b><br>Units Sold: %{x:,}<extra></extra>",
            ))
            st.plotly_chart(pt(fig, "Top Products by Units Sold", height=420), width='stretch')

        with su2:
            # Sunburst: Category → Product → Units
            fig = px.sunburst(
                prod_agg,
                path=["Category", "SubProduct"],
                values="Units_Sold",
                color="Units_Sold",
                color_continuous_scale=[[0,"#0D1220"],[0.5,"#5B9BF8"],[1,"#00E5B8"]],
                hover_data={"Units_Sold": True},
            )
            fig.update_traces(
                textfont_color="#EDF0FF",
                hovertemplate="<b>%{label}</b><br>Units: %{value:,}<extra></extra>",
            )
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(pt(fig, "Units Sold — Category › Product Sunburst", height=420), width='stretch')

        # Monthly trend of units sold by subproduct (top 6)
        su3, su4 = st.columns(2)
        with su3:
            top6 = prod_agg.nlargest(6, "Units_Sold")["SubProduct"].tolist()
            mdf = df_focus[df_focus["SubProduct"].isin(top6)].groupby(["Month","SubProduct"])["Units_Sold"].sum().unstack().fillna(0)
            mdf = mdf.reindex([m for m in ALL_MONTHS if m in sel_months])
            fig = px.line(mdf, markers=True, color_discrete_map=PRODUCT_COLORS)
            fig.update_traces(line_width=2, marker_size=6)
            st.plotly_chart(pt(fig, "Units Sold — Monthly Trend (Top 6 Products)", height=360), width='stretch')

        with su4:
            # Category comparison: stacked bar of units per store
            cat_store = df_focus.groupby(["Store","Category"])["Units_Sold"].sum().reset_index()
            fig = px.bar(cat_store, x="Store", y="Units_Sold", color="Category",
                         color_discrete_map=CAT_COLORS, barmode="stack")
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(pt(fig, "Units Sold by Store & Category", height=360), width='stretch')

    # ── TAB 2: Profit Analysis ───────────────────────────────────────────────
    with tab_profit:
        sp1, sp2 = st.columns(2)

        with sp1:
            prof_prods = prod_agg[prod_agg["Net_Profit"] >= 0].sort_values("Net_Profit", ascending=True).tail(15)
            if not prof_prods.empty:
                fig = go.Figure(go.Bar(
                    x=prof_prods["Net_Profit"],
                    y=prof_prods["SubProduct"],
                    orientation="h",
                    marker_color=[PRODUCT_COLORS.get(p, "#00E5B8") for p in prof_prods["SubProduct"]],
                    marker_line_width=0,
                    hovertemplate="<b>%{y}</b><br>Net Profit: ₹%{x:.2f}L<extra></extra>",
                ))
                st.plotly_chart(pt(fig, "Most Profitable Products (₹ Lakhs)", height=420), width='stretch')
            else:
                st.info("No profit-making products in the current selection.")

        with sp2:
            # Profit margin treemap
            fig = px.treemap(
                prod_agg[prod_agg["Net_Profit"] >= 0],
                path=["Category", "SubProduct"],
                values="Net_Profit",
                color="Profit_Margin_Pct",
                color_continuous_scale=[[0,"#0D1220"],[0.5,"#00E5B8"],[1,"#5B9BF8"]],
                hover_data={"Net_Profit": ":.2f", "Profit_Margin_Pct": ":.1f"},
            )
            fig.update_traces(textfont_color="#EDF0FF", marker_line_width=1, marker_line_color="rgba(255,255,255,0.08)")
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(pt(fig, "Profit Treemap — Net Profit (₹L) & Margin %", height=420), width='stretch')

        sp3, sp4 = st.columns(2)
        with sp3:
            # Gross vs Net Profit comparison
            top_profit = prod_agg.nlargest(10, "Gross_Profit")[["SubProduct","Gross_Profit","Net_Profit","Opex"]].sort_values("Gross_Profit")
            fig = go.Figure()
            fig.add_trace(go.Bar(y=top_profit["SubProduct"], x=top_profit["Gross_Profit"],
                                 name="Gross Profit", orientation="h", marker_color="#5B9BF8", marker_line_width=0))
            fig.add_trace(go.Bar(y=top_profit["SubProduct"], x=top_profit["Net_Profit"],
                                 name="Net Profit", orientation="h", marker_color="#00E5B8", opacity=0.7, marker_line_width=0))
            fig.update_layout(barmode="overlay")
            st.plotly_chart(pt(fig, "Gross vs Net Profit by Product (Top 10)", height=360), width='stretch')

        with sp4:
            # Revenue vs Profit scatter
            fig = px.scatter(
                prod_agg[prod_agg["Net_Profit"] >= 0],
                x="Revenue", y="Net_Profit",
                size="Units_Sold", color="Category",
                color_discrete_map=CAT_COLORS,
                text="SubProduct",
                hover_data={"Profit_Margin_Pct": True},
            )
            fig.update_traces(marker_line_width=0, marker_opacity=0.8, textfont_color="#EDF0FF", textfont_size=9)
            st.plotly_chart(pt(fig, "Revenue vs Net Profit (bubble = units sold)", height=360), width='stretch')

    # ── TAB 3: Loss Analysis ─────────────────────────────────────────────────
    with tab_loss:
        loss_df = prod_agg[prod_agg["Net_Profit"] < 0].sort_values("Net_Profit")

        if loss_df.empty:
            st.success("🎉 No loss-making products in the current selection! All products are profitable.")
        else:
            sl1, sl2 = st.columns(2)

            with sl1:
                fig = go.Figure(go.Bar(
                    x=loss_df["Net_Profit"],
                    y=loss_df["SubProduct"],
                    orientation="h",
                    marker_color="#FF5C7A",
                    marker_line_width=0,
                    hovertemplate="<b>%{y}</b><br>Net Loss: ₹%{x:.2f}L<extra></extra>",
                ))
                fig.add_vline(x=0, line_color="rgba(255,255,255,0.2)", line_width=1)
                st.plotly_chart(pt(fig, "Loss-Making Products — Net Loss (₹ Lakhs)", height=400), width='stretch')

            with sl2:
                # Revenue vs Loss: compare what we earn vs what we lose
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=loss_df["SubProduct"], y=loss_df["Revenue"],
                    name="Revenue", marker_color="#5B9BF8", marker_line_width=0,
                ))
                fig.add_trace(go.Bar(
                    x=loss_df["SubProduct"], y=loss_df["COGS"] + loss_df["Opex"],
                    name="Total Costs", marker_color="#FF5C7A", opacity=0.75, marker_line_width=0,
                ))
                fig.update_layout(barmode="group")
                st.plotly_chart(pt(fig, "Revenue vs Total Costs — Loss Products", height=400), width='stretch')

            sl3, sl4 = st.columns(2)
            with sl3:
                # Cost breakdown for loss products
                cost_melt = loss_df[["SubProduct","COGS","Opex"]].melt(id_vars="SubProduct", var_name="Cost Type", value_name="Amount")
                fig = px.bar(cost_melt, x="SubProduct", y="Amount", color="Cost Type",
                             color_discrete_map={"COGS":"#FFAB2E","Opex":"#A470FF"},
                             barmode="stack")
                fig.add_scatter(x=loss_df["SubProduct"], y=loss_df["Revenue"],
                                mode="markers", name="Revenue",
                                marker=dict(size=10, color="#00E5B8", symbol="diamond"))
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(pt(fig, "Cost Structure of Loss Products", height=340), width='stretch')

            with sl4:
                # Loss by category
                loss_by_cat = prod_agg.groupby("Category")["Net_Profit"].sum().reset_index()
                loss_by_cat["Type"] = np.where(loss_by_cat["Net_Profit"] >= 0, "Profit", "Loss")
                loss_by_cat["Abs"] = loss_by_cat["Net_Profit"].abs()
                fig = px.bar(
                    loss_by_cat.sort_values("Net_Profit"),
                    x="Net_Profit", y="Category", orientation="h",
                    color="Type", color_discrete_map={"Profit":"#00E5B8","Loss":"#FF5C7A"},
                )
                fig.add_vline(x=0, line_color="rgba(255,255,255,0.2)", line_width=1)
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(pt(fig, "Net Profit / Loss by Category", height=340), width='stretch')

            # ── Loss summary banner ──────────────────────────────────────────
            total_loss_val = loss_df["Net_Profit"].sum()
            worst_prod     = loss_df.iloc[0]["SubProduct"]
            worst_loss     = loss_df.iloc[0]["Net_Profit"]
            st.markdown(f"""
            <div style="display:flex;gap:12px;margin-top:16px;flex-wrap:wrap;">
              <div style="background:rgba(255,92,122,0.07);border:1px solid rgba(255,92,122,0.2);border-radius:12px;padding:16px 20px;flex:1;">
                <div style="font-size:10px;color:#FF5C7A;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:6px;">Total Net Loss</div>
                <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#FF5C7A;">₹{abs(total_loss_val):.2f}L</div>
              </div>
              <div style="background:rgba(255,92,122,0.07);border:1px solid rgba(255,92,122,0.2);border-radius:12px;padding:16px 20px;flex:1;">
                <div style="font-size:10px;color:#FF5C7A;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:6px;">Loss Products</div>
                <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#FF5C7A;">{len(loss_df)}</div>
                <div style="font-size:11px;color:#4A5270;">out of {n_products} total</div>
              </div>
              <div style="background:rgba(255,171,46,0.07);border:1px solid rgba(255,171,46,0.2);border-radius:12px;padding:16px 20px;flex:2;">
                <div style="font-size:10px;color:#FFAB2E;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:6px;">Worst Performer</div>
                <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#EDF0FF;">{worst_prod}</div>
                <div style="font-size:13px;color:#FF5C7A;font-weight:600;">₹{abs(worst_loss):.2f}L net loss</div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 4: Stock Status ──────────────────────────────────────────────────
    with tab_stock:
        ss1, ss2 = st.columns([1, 1])

        with ss1:
            # Stock status distribution donut
            stock_summary = prod_agg["Stock_Status_Grp"].value_counts().reset_index()
            stock_summary.columns = ["Status", "Count"]
            fig = px.pie(
                stock_summary, names="Status", values="Count",
                hole=0.6, color="Status", color_discrete_map=STATUS_COLORS,
            )
            fig.update_traces(
                textfont_color="#EDF0FF", textfont_size=12,
                hovertemplate="<b>%{label}</b><br>Products: %{value} (%{percent})<extra></extra>",
            )
            st.plotly_chart(pt(fig, "Product Stock Status Distribution", height=360), width='stretch')

        with ss2:
            # Stock units per product (horizontal bar, color by status)
            stock_bars = prod_agg.sort_values("Current_Stock", ascending=True).tail(20)
            bar_colors = [STATUS_COLORS.get(s, "#4A5270") for s in stock_bars["Stock_Status_Grp"]]
            fig = go.Figure(go.Bar(
                x=stock_bars["Current_Stock"],
                y=stock_bars["SubProduct"],
                orientation="h",
                marker_color=bar_colors,
                marker_line_width=0,
                hovertemplate="<b>%{y}</b><br>Stock: %{x:,} units<extra></extra>",
            ))
            st.plotly_chart(pt(fig, "Current Stock by Product (color = status)", height=360), width='stretch')

        ss3, ss4 = st.columns(2)
        with ss3:
            # Heatmap: Category × Product for stock
            stock_pivot = prod_agg.pivot_table(index="Category", columns="SubProduct", values="Current_Stock", aggfunc="sum").fillna(0)
            if not stock_pivot.empty:
                fig = px.imshow(
                    stock_pivot, aspect="auto", text_auto=".0f",
                    color_continuous_scale=[[0,"#FF5C7A"],[0.4,"#FFAB2E"],[1,"#00E5B8"]],
                )
                fig.update_coloraxes(showscale=False)
                fig.update_traces(textfont=dict(color="#EDF0FF", size=10))
                st.plotly_chart(pt(fig, "Stock Units — Category × Product Heatmap", height=360), width='stretch')

        with ss4:
            # Out of Stock & Low Stock product list
            oos_prods = prod_agg[prod_agg["Stock_Status_Grp"] != "Healthy"][["Category","SubProduct","Current_Stock","Units_Sold","Stock_Value","Stock_Status_Grp"]].sort_values("Current_Stock")
            if not oos_prods.empty:
                def _ss_style(val):
                    if val == "Out of Stock": return "color:#FF5C7A;font-weight:700"
                    if val == "Low Stock":    return "color:#FFAB2E;font-weight:600"
                    return ""
                st.markdown("""<div style="font-size:11px;color:#8892B0;margin-bottom:8px;font-weight:600;">⚠️ Products requiring attention</div>""", unsafe_allow_html=True)
                st.dataframe(
                    oos_prods.rename(columns={"Stock_Status_Grp":"Status","Stock_Value":"Value (₹L)"})
                             .style.map(_ss_style, subset=["Status"]),
                    width='stretch', hide_index=True,
                )
            else:
                st.success("✅ All products have healthy stock levels!")

        # ── Per-category stock overview ──────────────────────────────────────
        st.divider()
        section_header("Per-Category Stock Summary", accent="#00E5B8")
        cat_cols = st.columns(len(categories_to_show))
        for ci, cat in enumerate(categories_to_show):
            cat_prod_data = prod_agg[prod_agg["Category"] == cat]
            if cat_prod_data.empty:
                continue
            n_h   = (cat_prod_data["Stock_Status_Grp"] == "Healthy").sum()
            n_l   = (cat_prod_data["Stock_Status_Grp"] == "Low Stock").sum()
            n_o   = (cat_prod_data["Stock_Status_Grp"] == "Out of Stock").sum()
            total = len(cat_prod_data)
            c_col = CAT_COLORS.get(cat, "#5B9BF8")
            cat_icon2 = {"Electronics":"💻","Apparel":"👕","Home & Living":"🏠","Groceries":"🛒","Beauty":"💄"}.get(cat,"📦")
            with cat_cols[ci]:
                st.markdown(f"""
                <div style="background:rgba(13,18,32,0.9);border:1px solid rgba(255,255,255,0.07);
                     border-top:2px solid {c_col};border-radius:12px;padding:16px 14px;text-align:center;">
                  <div style="font-size:18px;margin-bottom:6px;">{cat_icon2}</div>
                  <div style="font-size:11px;font-weight:700;color:{c_col};margin-bottom:10px;">{cat}</div>
                  <div style="display:flex;flex-direction:column;gap:6px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;
                         background:rgba(0,229,184,0.06);border-radius:6px;padding:5px 8px;">
                      <span style="font-size:10px;color:#00E5B8;">✓ Healthy</span>
                      <span style="font-family:'Syne',sans-serif;font-size:14px;font-weight:800;color:#00E5B8;">{n_h}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;
                         background:rgba(255,171,46,0.06);border-radius:6px;padding:5px 8px;">
                      <span style="font-size:10px;color:#FFAB2E;">⚠ Low</span>
                      <span style="font-family:'Syne',sans-serif;font-size:14px;font-weight:800;color:#FFAB2E;">{n_l}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;
                         background:rgba(255,92,122,0.06);border-radius:6px;padding:5px 8px;">
                      <span style="font-size:10px;color:#FF5C7A;">✕ Out</span>
                      <span style="font-family:'Syne',sans-serif;font-size:14px;font-weight:800;color:#FF5C7A;">{n_o}</span>
                    </div>
                  </div>
                  <div style="height:4px;background:rgba(255,255,255,0.04);border-radius:4px;margin-top:10px;overflow:hidden;">
                    <div style="height:4px;background:{c_col};width:{n_h/total*100 if total else 0:.0f}%;border-radius:4px;"></div>
                  </div>
                  <div style="font-size:10px;color:#4A5270;margin-top:4px;">{n_h/total*100 if total else 0:.0f}% healthy</div>
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if "Store Performance" in app_mode:
    render_store_performance()
elif "Stock" in app_mode:
    render_stock_analysis()
else:
    render_product_analytics()


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
import datetime as _dt
_now = _dt.datetime.now().strftime("%d %b %Y · %H:%M")

st.markdown(f"""
<div id="nexus-footer">
  <div class="footer-grid">
    <div class="footer-brand">
      <div class="footer-logo"><img src="data:image/png;base64,{icon_b64}" width="24" style="border-radius:4px; filter: drop-shadow(0 0 8px rgba(91,155,248,0.3));"> <span>NEXUS</span></div>
      <div class="footer-tagline">
        Retail Intelligence Platform — real-time analytics for modern store networks.
        Powered by Streamlit &amp; Plotly.
      </div>
      <div style="display:flex;gap:8px;margin-top:10px;">
        <div style="width:28px;height:2px;border-radius:2px;background:#5B9BF8;opacity:0.7;"></div>
        <div style="width:18px;height:2px;border-radius:2px;background:#00E5B8;opacity:0.5;"></div>
        <div style="width:10px;height:2px;border-radius:2px;background:#A470FF;opacity:0.4;"></div>
      </div>
    </div>
    <div class="footer-stat-group">
      <div class="footer-stat-label">Dataset Summary</div>
      <div class="footer-stat">
        <span class="footer-stat-val" style="color:#5B9BF8;">{len(df):,}</span>
        <span class="footer-stat-key">Active Records</span>
      </div>
      <div class="footer-stat">
        <span class="footer-stat-val" style="color:#00E5B8;">{len(STORES)}</span>
        <span class="footer-stat-key">Stores Analysed</span>
      </div>
      <div class="footer-stat">
        <span class="footer-stat-val" style="color:#A470FF;">{len(CATS)}</span>
        <span class="footer-stat-key">Product Categories</span>
      </div>
      <div class="footer-stat" style="border:none;">
        <span class="footer-stat-val" style="color:#FFAB2E;">{len(ALL_MONTHS)}</span>
        <span class="footer-stat-key">Months Loaded</span>
      </div>
    </div>
    <div class="footer-badges">
      <div class="footer-stat-label">System Status</div>
      <div class="footer-badge">
        <div class="footer-badge-dot" style="background:#00E5B8;"></div>
        <span class="footer-badge-text">All systems operational</span>
      </div>
      <div class="footer-badge">
        <div class="footer-badge-dot" style="background:#5B9BF8;"></div>
        <span class="footer-badge-text">Real-time ambient rendering</span>
      </div>
      <div class="footer-badge">
        <div class="footer-badge-dot" style="background:#A470FF;"></div>
        <span class="footer-badge-text">Interactive Plotly charts</span>
      </div>
      <div class="footer-badge">
        <div class="footer-badge-dot" style="background:#FFAB2E;"></div>
        <span class="footer-badge-text">Pandas 3.x compatible</span>
      </div>
    </div>

  </div>
  <div class="footer-bottom">
    <div class="footer-copy">
      &copy; 2026 NEXUS Retail Intelligence &nbsp;·&nbsp; Last refreshed: {_now}
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div style="display:flex;align-items:center;gap:6px;">
        <div style="width:5px;height:5px;border-radius:50%;background:#00E5B8;
             animation:blink 2s ease-in-out infinite;"></div>
        <span style="font-size:10px;color:#4A5270;">Live</span>
      </div>
      <div class="footer-version">v3.0 · NEXUS</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)