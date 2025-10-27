# =============================
# 🎵 Stay or Skip — Main Streamlit App (CSV-ready, minimal patch)
# =============================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path
import base64
import os
import re
import altair as alt  # ★ 인터랙티브 차트용

# ---------- App config ----------
st.set_page_config(page_title="Stay or Skip 🎧", page_icon="🎧", layout="wide")

# ---------- 경로/상수 ----------
BASE = Path(__file__).parent  # spotify.py가 있는 폴더(StayOrSkip)
RAW_BASE = "https://raw.githubusercontent.com/twinklefins/modu_project/main/StayOrSkip"  # 본인 레포 경로

# ---------- 이미지/플롯 하위호환 래퍼 ----------
def _st_image_compat(data: bytes):
    """Streamlit 신/구버전 호환 이미지 렌더"""
    try:
        st.image(data, use_container_width=True)
    except TypeError:
        st.image(data, use_column_width=True)

def sp(fig):
    """Streamlit 신/구버전 호환 pyplot 렌더"""
    try:
        st.pyplot(fig, use_container_width=True)
    except TypeError:
        st.pyplot(fig)

def _try_open_bytes(path: Path):
    try:
        with path.open("rb") as f:
            return f.read()
    except Exception:
        return None

def render_image(filename: str):
    """같은 폴더/자주 쓰는 하위폴더 우선, 실패 시 GitHub Raw 폴백(조용히 패스)"""
    candidates = [
        BASE / filename,
        BASE / "assets" / filename,            # ★ 추가
        BASE / "StayOrSkip" / filename,        # ★ 추가
    ]
    for p in candidates:
        b = _try_open_bytes(p)
        if b:
            _st_image_compat(b); return
    # GitHub Raw
    try:
        import urllib.request
        url = f"{RAW_BASE}/{filename}"
        with urllib.request.urlopen(url, timeout=6) as resp:
            _st_image_compat(resp.read())
        return
    except Exception:
        pass  # 패스

def img_to_datauri(filename: str) -> str:
    """이미지를 data URI로 변환(로컬→실패 시 GitHub Raw 폴백)"""
    candidates = [
        BASE / filename,
        BASE / "assets" / filename,            # ★ 추가
        BASE / "StayOrSkip" / filename,        # ★ 추가
    ]
    for p in candidates:
        try:
            with p.open("rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            return f"data:image/png;base64,{b64}"
        except Exception:
            pass
    # Raw
    try:
        import urllib.request
        url = f"{RAW_BASE}/{filename}"
        with urllib.request.urlopen(url, timeout=6) as resp:
            b64 = base64.b64encode(resp.read()).decode("ascii")
        return f"data:image/png;base64,{b64}"
    except Exception:
        # 마지막: 빈 투명 픽셀(1x1)
        return "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="

# ---------- 간격 유틸 ----------
def vgap(px: int):
    st.markdown(f"<div style='height:{px}px;'></div>", unsafe_allow_html=True)

def tight_top(px: int):
    st.markdown(f"<div style='margin-top:{px}px;'></div>", unsafe_allow_html=True)

# ---------- 소제목/간격 유틸 ----------
def section_title(text: str, caption: str = "", top_gap: int = 18, bottom_gap: int = 8):
    """제목 + 작은 설명 + 위아래 여백을 한 번에 출력"""
    vgap(top_gap)
    st.markdown(f"<div class='cup-h2'>{text}</div>", unsafe_allow_html=True)
    if caption:
        st.markdown(f"<span style='color:#A7B9AF;font-size:0.92rem;'>{caption}</span>", unsafe_allow_html=True)
    vgap(bottom_gap)

# ---------- 데이터 로드 (★ CSV 우선, 없으면 기존 XLSX) ----------
@st.cache_data(show_spinner=False)
def load_data():
    """
    Dataset Overview용: 머지된 엑셀(spotify_merged.xlsx) 우선.
    없으면 동일 스키마의 CSV를 백업으로 사용.
    """
    xlsx = BASE / "spotify_merged.xlsx"
    if xlsx.exists():
        df = pd.read_excel(xlsx)
        source = "xlsx"
    else:
        # 백업: 같은 파일명이거나 data/raw 경로의 csv
        csv_cands = [BASE / "spotify_merged.csv", BASE / "data" / "raw" / "spotify_merged.csv"]
        hit = next((p for p in csv_cands if p.exists()), None)
        if hit is None:
            raise FileNotFoundError("spotify_merged.xlsx(우선) 또는 spotify_merged.csv 를 찾지 못했습니다.")
        df = pd.read_csv(hit)
        source = "csv"

    # 최소 정리: revenue → 숫자, month → str  (차트/지표 안정화)
    if "revenue" in df.columns and "revenue_num" not in df.columns:
        def to_num(x):
            s = re.sub(r"[^0-9.\-]", "", str(x)) if pd.notna(x) else ""
            return float(s) if s else np.nan
        df["revenue_num"] = df["revenue"].map(to_num)

    if "month" in df.columns:
        df["month"] = df["month"].astype(str)

    return df, source

try:
    tidy, _src = load_data()
except FileNotFoundError:
    st.error("`spotify_merged.xlsx` 파일을 우선 찾고, 없으면 `spotify_merged.csv`를 찾습니다. 폴더(또는 data/raw)에 업로드해주세요.")
    st.stop()

# ================= CSS =================
st.markdown("""
<style>
:root{
  --bg:#121212; --panel:#191414; --text:#F9FCF9; --muted:#D7E4DC; --line:rgba(255,255,255,.08);
  --brand:#1DB954; --brand-2:#1ED760; --soft-ivory:#E8F5E9; --tab-underline:rgba(29,185,84,.5); --navShift:18px;
}
html, body, .stApp,[data-testid="stAppViewContainer"], [data-testid="stMain"]{ background:var(--bg)!important; color:var(--text)!important; }
[data-testid="stHeader"]{ background:var(--bg)!important; box-shadow:none!important; }
[data-testid="stAppViewContainer"] .main .block-container{ padding-top:.15rem!important; padding-bottom:2rem!important; }

section[data-testid="stSidebar"]{ background:var(--panel)!important; color:var(--text)!important; }
section[data-testid="stSidebar"] .block-container{ padding-top:.25rem!important; padding-bottom:.8rem!important; }
hr.cup-divider{ border:none; height:1px; background:var(--line); margin:.6rem 0 .5rem 0; }
section[data-testid="stSidebar"] [role="radiogroup"]{ display:flex; flex-direction:column; gap:.30rem; margin-left:var(--navShift)!important; }
section[data-testid="stSidebar"] label[data-baseweb="radio"]{ position:relative; display:block; background:transparent; border:none; border-radius:6px;
  padding:.35rem .45rem .35rem .90rem; line-height:1.08; cursor:pointer; transition:color .12s ease, background .12s ease; }
section[data-testid="stSidebar"] label[data-baseweb="radio"] p{ margin:0; color:#CFE3D8; font-weight:600; letter-spacing:.15px; font-size:.94rem; transition:color .12s ease; }
section[data-testid="stSidebar"] label[data-baseweb="radio"]:hover p{ color:var(--brand-2)!important; }
section[data-testid="stSidebar"] label[data-baseweb="radio"][aria-checked="true"]::before,
section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked)::before{
  content:""; position:absolute; left:.42rem; top:50%; width:9px; height:9px; border-radius:50%; background:var(--brand); transform:translateY(-50%);
}
section[data-testid="stSidebar"] label[data-baseweb="radio"][aria-checked="true"] p,
section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p{ color:#FFF!important; font-weight:700!important; }
section[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child, section[data-testid="stSidebar"] label[data-baseweb="radio"] svg{ display:none!important; }
section[data-testid="stSidebar"] label[data-baseweb="radio"] input[type="radio"]{ position:absolute; left:-9999px; opacity:0; }

hr.cup-footer-line{ border:none; height:1px; background:var(--line); margin:.8rem 0 .75rem 0; }
.cup-sidebar-footer{ margin-left:var(--navShift); color:var(--muted); font-size:.84rem; letter-spacing:.1px; text-align:left; }
.cup-link-btn{ display:inline-block; margin-bottom:.45rem; padding:6px 10px; font-size:.85rem; font-weight:600;
  color:var(--brand); text-decoration:none; border:1px solid rgba(29,185,84,.45); border-radius:6px; transition:all .2s ease; }
.cup-link-btn:hover{ background:var(--brand); color:#0.1; border-color:var(--brand); }

h1{ font-weight:800; letter-spacing:-0.2px; margin:0 0 -0.2rem 0!important; }
.cup-subtitle{ color:var(--muted); font-size:1.08rem; font-weight:500; margin:0 0 1rem 0; letter-spacing:.1px; }
.cup-h2{ display:flex; align-items:center; gap:.8rem; margin:1.6rem 0 .9rem 0; font-weight:700; font-size:1.25rem; letter-spacing:.1px; }
.cup-h2::before{ content:""; display:inline-block; width:4px; height:22px; background:var(--brand); border-radius:2px; }
.cup-card{ background:transparent; border:1px solid var(--line); border-radius:10px; padding:1rem 1.2rem; margin:1.1rem 0; }

.stTabs [aria-selected="true"], .stTabs [data-baseweb="tab"]:focus, .stTabs [data-baseweb="tab"]:active { background:transparent; box-shadow:none; filter:none; }
.stTabs [aria-selected="true"] p{ color:var(--brand-2); }
.stTabs [role="tablist"]{ border-color: rgba(255,255,255,.08); }
.stTabs [data-baseweb="tab"]{ border-bottom:2px solid transparent; }
.stTabs [data-baseweb="tab"][aria-selected="true"]{ border-bottom-color:var(--brand); }
.stTabs [data-baseweb="tab"]:hover{ border-bottom-color:var(--brand-2); }
.stTabs [data-baseweb="tab-highlight"]{ background:var(--brand)!important; }
.stTabs [data-baseweb="tab"] p{ color:rgba(255,255,255,0.72)!important; transition:color .15s ease; }
.stTabs [data-baseweb="tab"]:hover p{ color:var(--brand-2)!important; }

div[data-testid="stMetric"] div[data-testid="stMetricValue"]{ color:var(--brand)!important; font-weight:800!important; font-size:2.2rem!important; line-height:1.1!important; white-space:nowrap!important; }
div[data-testid="stMetric"] div[data-testid="stMetricLabel"] p{ font-size:1.05rem!important; color:var(--muted)!important; letter-spacing:.2px; }
.cup-kpi-plus small{ font-size:60%; opacity:.85; vertical-align:super; }
.kpi-tight [data-testid="stHorizontalBlock"]{ gap:.2rem!important; }
.kpi-tight [data-testid="column"]{ padding-left:.05rem!important; padding-right:.05rem!important; }
.kpi-tight [data-testid="stMetric"]{ margin-bottom:0!important; }

.cup-info-box{ background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.10); border-radius:12px; padding:1.6rem 1.8rem; }
.cup-team-line{ color:rgba(255,255,255,.9); font-size:1.05rem; line-height:2.0; margin:.2rem 0; display:flex; align-items:center; }
.cup-team-name{ display:inline-block; width:70px; font-weight:600; color:#fff; }
.cup-team-role{ margin-left:.4rem; }
.cup-spotify-box{ background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.10); border-radius:12px; padding:1.2rem 1.4rem; }

div[data-testid="stMarkdownContainer"] > p{ margin-bottom:.15rem!important; }
div[data-testid="stMarkdownContainer"] ul{ margin-top:.05rem!important; margin-bottom:.4rem!important; margin-left:1.1rem!important; padding-left:0!important; }
.cup-gap-top{ margin-top:1.2rem!important; }
.cup-gap-y{ height:1.2rem; }
            
/* 섹션 제목의 기본 여백을 없애고(=0), 아래쪽만 section_title()로 제어 */
.cup-h2{ margin:0 0 .9rem 0 !important; }

/* 카드 안 code가 초록색으로 보이지 않게 – 일반 텍스트처럼 */
.cup-card code{ color:var(--text)!important; background:transparent!important; padding:0!important; }
</style>
""", unsafe_allow_html=True)

# ================= Sidebar =================
with st.sidebar:
    st.caption("build: v2025-10-24-spotify-compat-CSV")  # ← 새 코드 적용 확인용
    # 로고 탐색 강화 (assets/ 포함)
    render_image("Cup_3_copy_4.png")
    st.markdown('<hr class="cup-divider">', unsafe_allow_html=True)
    section = st.radio("", ["PROJECT OVERVIEW","DATA EXPLORATION","AARRR DASHBOARD","INSIGHTS & STRATEGY"])
    st.markdown('<hr class="cup-footer-line">', unsafe_allow_html=True)
    st.markdown(
        '<div class="cup-sidebar-footer">'
        '<a href="https://colab.research.google.com/drive/1kmdOCUneO2tjT8NqOd5MvYaxJqiiqb9y?usp=sharing" '
        'target="_blank" class="cup-link-btn">🔗 Open in Google Colab</a><br>'
        '© DATA CUPBOP | Stay or Skip'
        '</div>', unsafe_allow_html=True
    )

# ================= Demo data (페이지 데모용 - 그대로) =================
np.random.seed(42)
dates = pd.date_range("2025-01-01", periods=60, freq="D")
df_demo = pd.DataFrame({
    "date": np.random.choice(dates, 1000),
    "channel": np.random.choice(["SNS","Search","Ad"], 1000, p=[0.45,0.35,0.20]),
    "event": np.random.choice(["visit","signup","first_play","subscribe"], 1000, p=[0.45,0.25,0.20,0.10]),
    "amount": np.random.gamma(2.2, 6.0, 1000).round(2)
})

# ================= Title =================
# ▶︎ 아이콘 경로 보강: assets/ 경로도 자동 탐색
icon_datauri = img_to_datauri("StayOrSkip/free-icon-play-4604241.png")
if icon_datauri.endswith("AQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="):  # 폴백픽셀이면 assets로 재시도
    icon_datauri = img_to_datauri("free-icon-play-4604241.png")
if icon_datauri.endswith("AQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="):
    icon_datauri = img_to_datauri("assets/free-icon-play-4604241.png")

st.markdown(f"""
<style>
  .cup-hero {{ display:inline-flex; align-items:baseline; gap:0; margin:-4.5rem 0 .25rem 0; transform:translateY(-8px); }}
  .cup-hero h1 {{ margin:0; line-height:1; font-weight:800; letter-spacing:-.2px; transform:translateY(-2px); }}
  .cup-hero img {{ width:3.05em; height:auto; vertical-align:baseline; transform:translateY(0.65em); margin-left:-6px!important; display:inline-block; }}
  [data-testid="stAppViewContainer"] .main .block-container {{ padding-top:.1rem!important; }}
  .cup-subtitle {{ color: var(--muted); font-size: 1.08rem; font-weight: 500; margin-top: -1.4rem!important; margin-bottom: 1.0rem!important; letter-spacing: .1px; }}
</style>
<div class="cup-hero"><h1>Stay or Skip</h1><img src="{icon_datauri}" alt="play icon" /></div>
<p class="cup-subtitle">Streaming Subscription Analysis with AARRR Framework</p>
""", unsafe_allow_html=True)
vgap(36)

# ================= Sections =================
if section == "PROJECT OVERVIEW":
    tabs = st.tabs(["Team Intro", "About Spotify", "Background & Objectives", "Dataset"])

    # ---- Team Intro ----
    with tabs[0]:
        section_title("Team Introduction")
        tight_top(-36)
        st.markdown("<style>.cup-logo{ display:block; margin:-1.2rem 0 2.2rem 0; width:35%; max-width:520px; height:auto; }</style>", unsafe_allow_html=True)
        logo_uri = img_to_datauri("Cup_8_copy_2.png")
        if logo_uri.endswith("AQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="):
            logo_uri = img_to_datauri("assets/Cup_8_copy_2.png")
        st.markdown(f'<img src="{logo_uri}" class="cup-logo" alt="team logo">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cup-info-box">
          <p style="font-weight:600;">빠르지만 든든한 데이터 분석, 인사이트 한 스푼으로 완성하는 데이터컵밥 🍚</p>
          <p class="cup-team-line"><span class="cup-team-name">함께</span><span class="cup-team-role">데이터 탐색(EDA) · 핵심 지표 선정 · 시각화 · 인사이트 도출</span></p>
          <p class="cup-team-line"><span class="cup-team-name">천지우</span><span class="cup-team-role">프로젝트 매니징 & 분석 구조 설계</span></p>
          <p class="cup-team-line"><span class="cup-team-name">이유주</span><span class="cup-team-role">데이터 스토리텔링 & 대시보드 디자인</span></p>
          <p class="cup-team-line"><span class="cup-team-name">김채린</span><span class="cup-team-role">데이터 정제 및 파생 변수 설계</span></p>
          <p class="cup-team-line"><span class="cup-team-name">서별</span><span class="cup-team-role">데이터 수집 및 탐색 과정 지원</span></p>
        </div>
        """, unsafe_allow_html=True)

    # ---- About Spotify ----
    with tabs[1]:
        section_title("About Spotify")
        tight_top(-36)

        st.markdown('<div class="kpi-tight">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Monthly Active Users", "696M")
        with c2: st.metric("Premium Subscribers", "276M")
        with c3: st.metric("Markets", "180+")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="cup-spotify-box" style="margin-bottom:1.0rem;">
          2008년 스웨덴에서 시작된 글로벌 음악 스트리밍 플랫폼<br>
          Freemium(광고 기반 무료) + Premium(유료 구독) 모델 운영<br>
          청취 로그와 오디오 피처 기반 <b>개인화 추천</b> 제공
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="cup-compact cup-gap-top">', unsafe_allow_html=True)
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Business Model**")
            st.markdown("- Freemium (광고 수익) + Premium (월 구독)\n- 주요 지표: 전환률, 리텐션, 청취 시간, 광고 노출/CTR")
            st.markdown('<div class="cup-gap-y"></div>', unsafe_allow_html=True)
            st.markdown("**Content Types**")
            st.markdown("- Music • Podcasts • Audiobooks")
        with colB:
            st.markdown("**Product Surfaces**")
            st.markdown("- Mobile / Desktop / Web\n- Spotify Connect (스피커·TV 등 기기 연동)")
            st.markdown('<div class="cup-gap-y"></div>', unsafe_allow_html=True)
            st.markdown("**Creator Tools**")
            st.markdown("- Spotify for Artists (지역별 청취자, 플레이리스트 유입, 재생 통계 제공)")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="cup-h2" style="margin-top:1.0rem;">Pricing Model</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="cup-spotify-box" style="margin-top:.5rem;">
          <b>Freemium</b>: 광고 기반 무료 서비스 (스트리밍 중 광고 삽입)<br>
          <b>Premium</b>: 월 구독제 — 광고 제거, 오프라인 재생, 고음질, 무제한 스킵<br>
          <small>※ 한국 기준 10,900원/월 (2025년 기준)</small>
        </div>
        """, unsafe_allow_html=True)
        st.caption("*Spotify 공식 회사 정보 기준 요약")

        # ---- Background & Objectives ----
        with tabs[2]:
            section_title("Background & Objectives")
            tight_top(-36)

            # ===================== CSS =====================
            st.markdown("""
            <style>
            /* 3열 카드 */
            .cup-3col {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 1.2rem;
            }
            .cup-hover-card {
                transition: all .25s ease;
                background: rgba(255,255,255,.03);
                border: 1px solid rgba(255,255,255,.10);
                border-radius: 12px;
                padding: 1.6rem 1.8rem;
                text-align: center;
            }
            .cup-hover-card:hover {
                background: rgba(255,255,255,.08);
                border-color: rgba(255,255,255,.18);
                transform: translateY(-4px);
                box-shadow: 0 0 15px rgba(29,185,84,.25);
            }

            /* 🎬 시네마틱 섹션 */
            .cup-scene {
                background: rgba(255,255,255,.03);
                border: 1px solid rgba(255,255,255,.10);
                border-radius: 12px;
                padding: 2.2rem 2.6rem;
                text-align: center;
                color: #F9FCF9;
                line-height: 1.9;
                box-shadow: 0 0 15px rgba(29,185,84,.18);
                margin-top: 1.4rem;
            }
            .cup-scene .brand { color: #1ED760; font-weight: 700; }
            .cup-scene .em { color: rgba(255,255,255,.85); font-style: italic; }
            .cup-scene strong { color: #FFF; }

            /* 🎯 미션 코드 */
            .cup-mission {
                display: inline-block;
                margin-top: 1.4rem;
                padding: .32rem .75rem;
                border-radius: 6px;
                border: 1px solid rgba(29,185,84,.45);
                background: rgba(29,185,84,.08);
                color: #1ED760;
                font-weight: 800;
                font-size: .88rem;
                letter-spacing: .13em;
                text-transform: uppercase;
            }

            /* 💬 엔딩 원라이너 */
            .cup-one-liner-bottom {
                font-size: 1.05rem;
                font-weight: 500;
                color: #D7E4DC;
                text-align: center;
                margin-top: 1.5rem;
                letter-spacing: .2px;
            }
            </style>
            """, unsafe_allow_html=True)

            # ===================== 카드 섹션 =====================
            st.markdown("""
            <div class="cup-3col">
            <div class="cup-hover-card">
                <p style="font-size:1.5rem;">📈</p>
                <p style="font-weight:800;font-size:1.1rem;margin-bottom:1rem;">스트리밍 시장 성장과 도전</p>
                <p style="color:rgba(255,255,255,.9);font-size:1.05rem;line-height:1.85;">
                글로벌 시장 급성장, 유입률↑ 이탈률↑<br>
                높은 경쟁 속 체험 후 구독 전환율 하락<br>
                콘텐츠 피로도·사용자 유지가 핵심 과제로 부상
                </p>
            </div>

            <div class="cup-hover-card">
                <p style="font-size:1.5rem;">🎧</p>
                <p style="font-weight:800;font-size:1.1rem;margin-bottom:1rem;">Spotify의 강점</p>
                <p style="color:rgba(255,255,255,.9);font-size:1.05rem;line-height:1.85;">
                세계 최대 규모 청취 로그 및 오디오 피처 데이터 보유<br>
                유저 행동 여정·이탈 패턴 분석에 최적화된 플랫폼
                </p>
            </div>

            <div class="cup-hover-card">
                <p style="font-size:1.5rem;">🧭</p>
                <p style="font-weight:800;font-size:1.1rem;margin-bottom:1rem;">AARRR 기반 분석 방향</p>
                <p style="color:rgba(255,255,255,.9);font-size:1.05rem;line-height:1.85;">
                Acquisition → Retention → Revenue<br>
                단계별 핵심 지표 정의<br>
                데이터 기반 리텐션·LTV 개선 전략 제안
                </p>
            </div>
            </div>
            """, unsafe_allow_html=True)

            # ===================== 시네마틱 박스 =====================
            st.markdown("""
            <div class="cup-scene">
            <p style="font-size:1.28rem; margin-bottom:1.1rem;">
                🎧 <b>“Skip Generation — 스킵은 빠르지만, 이탈은 더 빨랐다.”</b>
            </p>

            <p style="font-size:1.05rem; color:rgba(255,255,255,.86);">
                스트리밍 세상의 <span class="em">체험 유목민들</span>.<br>
                한 곡 듣고 넘기고, 한 달 듣고 떠난 사람들.
            </p>

            <p style="margin-top:1.1rem; font-size:1.05rem;">
                <b><span class="brand">Spotify Korea TF</span></b> <strong>데이터컵밥팀</strong>은<br>
                <span class="brand">유저의 행동 여정</span>을 데이터로 추적해,<br>
                ‘<span class="brand">스킵 제너레이션</span>’을 이탈로부터 구하고<br>
                ‘<span class="brand">스테이 제너레이션</span>’으로 재탄생시키기 위한 작전을 시작했다.
            </p>

            <div class="cup-mission">MISSION CODE · AARRR</div>

            <div class="cup-one-liner-bottom">
                “Retention is the new acquisition — 남게 만드는 전략이 Spotify Korea의 성장을 결정한다.”
            </div>
            </div>
            """, unsafe_allow_html=True)
            
    # ---- Dataset (tabs[3]) ----
    with tabs[3]:
        # ⚠️ 여기서 새로 함수 만들지 말고, 모듈을 불러 '호출'만 합니다.
        from sections import revenue   # sections/revenue.py 파일 필요
        revenue.render()               # ← 이 한 줄이 실제로 화면을 그립니다.
        # sections/revenue.py
        import os
        import numpy as np
        import pandas as pd
        import streamlit as st
        import matplotlib.pyplot as plt

        SPOTIFY_GREEN = "#1DB954"
        ACCENT_CYAN   = "#80DEEA"
        BG_DARK       = "#121212"
        PLOT_DARK     = "#191414"
        TICK_COLOR    = "#CFE3D8"

        def _load_csv(name: str):
            for p in (os.path.join("data", name), name):
                if os.path.exists(p):
                    return pd.read_csv(p)
            return None

        def _dark_ax(figsize=(6,3)):
            fig, ax = plt.subplots(figsize=figsize)
            fig.set_facecolor(BG_DARK)
            ax.set_facecolor(PLOT_DARK)
            ax.tick_params(colors=TICK_COLOR)
            for s in ax.spines.values(): s.set_color(TICK_COLOR)
            return fig, ax

        def render():
            st.title("💰 Revenue")
            st.caption("CSV(export) 기반 KPI / 트렌드 / 취향별 LTV / 중요 요인")

            kpi  = _load_csv("out_revenue_kpis.csv")
            retm = _load_csv("out_premium_retention_monthly.csv")
            arpu = _load_csv("out_arpu_monthly.csv")
            pref = _load_csv("out_pref_group_summary.csv")
            sig  = _load_csv("out_pref_significance_tests.csv")
            imp  = _load_csv("out_feature_importance_ltv.csv")

            miss = [n for n,d in {
                "out_revenue_kpis.csv":kpi,
                "out_premium_retention_monthly.csv":retm,
                "out_arpu_monthly.csv":arpu,
                "out_pref_group_summary.csv":pref,
                "out_pref_significance_tests.csv":sig,
                "out_feature_importance_ltv.csv":imp
            }.items() if d is None]
            if miss:
                st.warning("다음 파일을 찾지 못했습니다:\n- " + "\n- ".join(miss))
                st.info("노트북 STEP6에서 /data 폴더로 export 후 Rerun 해주세요.")
                return

            # === KPI ===
            conv  = float(kpi.loc[kpi.metric=="conversion_rate","value"])
            rmean = float(kpi.loc[kpi.metric=="premium_retention_mean","value"])
            arpu_v= float(kpi.loc[kpi.metric=="arpu_overall","value"])
            dur   = float(kpi.loc[kpi.metric=="avg_premium_duration","value"])
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("전환율", f"{conv*100:.1f}%")
            c2.metric("유지율(평균)", f"{rmean*100:.1f}%")
            c3.metric("ARPU(원)", f"{arpu_v:,.0f}")
            c4.metric("평균 Premium 기간", f"{dur:.2f}개월")

            with st.expander("KPI 계산식(분자/분모)"):
                st.markdown(
                    "- **전환율** = Premium으로 전환한 사용자 수 / 최초 Free 사용자 수\n"
                    "- **유지율(A→B)** = A,B 둘 다 Premium인 사용자 수 / A의 Premium 사용자 수\n"
                    "- **ARPU** = revenue 총합 / 전체 유저-월 수\n"
                    "- **평균 Premium 기간** = 사용자별 Premium 개월수 평균\n"
                    "- **LTV(유저)** = 사용자별 revenue 합(여기 표는 그룹 평균)"
                )

            # === Retention & ARPU ===
            st.subheader("📈 Retention & ARPU Trend")
            col1, col2 = st.columns(2)

            with col1:
                x = retm["from_to"].tolist(); y = retm["premium_retention"].tolist()
                fig, ax = _dark_ax()
                ax.plot(range(len(x)), y, marker="o", color=SPOTIFY_GREEN, linewidth=2)
                ax.set_xticks(range(len(x))); ax.set_xticklabels(x, rotation=0)
                ax.set_ylim(0,1.05); st.pyplot(fig, use_container_width=True)
                st.caption(f"• 유지율 최고 구간: **{x[int(np.nanargmax(y))]} = {max(y)*100:.1f}%**")

            with col2:
                x2 = arpu["month"].tolist(); y2 = arpu["arpu"].tolist()
                fig, ax = _dark_ax()
                ax.plot(range(len(x2)), y2, marker="o", color=ACCENT_CYAN, linewidth=2)
                ax.set_xticks(range(len(x2))); ax.set_xticklabels(x2, rotation=0)
                st.pyplot(fig, use_container_width=True)
                st.caption(f"• ARPU 최고 월: **{x2[int(np.nanargmax(y2))]} = {max(y2):,.0f}원**")

            # === 취향별 평균 LTV ===
            st.subheader("🎧 취향별 평균 LTV")
            def _pick_group(row):
                col = row["variable"]
                return row[col] if col in row.index else None
            view = pref.copy()
            view["group"] = view.apply(_pick_group, axis=1)
            view = view[["variable","group","users","avg_ltv","avg_premium_duration",
                        "avg_monthly_revenue","free_to_premium_rate"]].sort_values("avg_ltv", ascending=False)
            with st.expander("Top 10 보기"):
                st.dataframe(view.head(10), use_container_width=True)
            st.caption(f"• LTV 최고 세그: **{view.iloc[0]['variable']} = {view.iloc[0]['group']}**, 평균 LTV **{view.iloc[0]['avg_ltv']:,.0f}원**")

            # === 통계적으로 유의한 요인 ===
            st.subheader("🔍 통계적으로 유의한 요인 (p<0.05)")
            sig_view = sig.query("p_value < 0.05").sort_values("p_value")
            st.dataframe(sig_view.head(10), use_container_width=True)
            st.caption(f"• 최상위: **{sig_view.iloc[0]['feature']}** ({sig_view.iloc[0]['test_type']}), p={sig_view.iloc[0]['p_value']:.2e}")

            # === Feature Importance ===
            st.subheader("🌲 LTV 영향 요인 (Feature Importance)")
            if imp.shape[1] == 2:
                imp.columns = ["feature","importance"]
            else:
                imp = imp.rename(columns={imp.columns[0]:"feature", imp.columns[1]:"importance"})
            topk = imp.sort_values("importance", ascending=False).head(10)
            fig, ax = _dark_ax((10,3.2))
            ax.bar(range(len(topk)), topk["importance"], color=SPOTIFY_GREEN)
            ax.set_xticks(range(len(topk))); ax.set_xticklabels(topk["feature"], rotation=0)
            ax.set_ylabel("Importance", color=TICK_COLOR)
            st.pyplot(fig, use_container_width=True)
            st.caption(f"• LTV 최상위 영향: **{topk.iloc[0]['feature']}** (중요도 {topk.iloc[0]['importance']:.3f})")

            # === 종합 인사이트 ===
            st.markdown("---")
            st.success(
                "### 📦 종합 인사이트\n"
                f"- 전환율 **{conv*100:.1f}%**, 평균 유지율 **{rmean*100:.1f}%**, ARPU **{arpu_v:,.0f}원**, 평균 Premium 기간 **{dur:.2f}개월**\n"
                f"- 유지율 최고 구간: **{retm.iloc[int(np.nanargmax(y))]['from_to']}**, ARPU 최고 월: **{arpu.iloc[int(np.nanargmax(y2))]['month']}**\n"
                f"- LTV 상위 세그먼트: **{view.iloc[0]['variable']} = {view.iloc[0]['group']}**\n"
                f"- 최상위 영향 요인: **{topk.iloc[0]['feature']}**\n"
                "→ **제안:** 상위 세그 타깃 번들/추천 강화, 저유지 월에는 리마인드/추천 푸시 집중."
            )


elif section == "AARRR DASHBOARD":   # 섹션 이름은 그대로 두고, 탭만 AARR로 변경
    st.markdown('<div class="cup-h2">Visual Analytics Dashboard</div>', unsafe_allow_html=True)
    try:
        tight_top(-36)   # 네 앱에 있던 헬퍼 함수면 사용, 없으면 무시
    except:
        pass

    # 🔄 AARR: Acquisition / Activation / Retention / Revenue
    tabs = st.tabs(["Acquisition", "Activation", "Retention", "Revenue"])

    # -------------------------------
    # ① Acquisition (기존 Funnel 재사용)
    # -------------------------------
    with tabs[0]:
        st.subheader("Acquisition (Funnel)")
        st.caption("방문 → 가입 → 첫 재생 → 구독 전환율을 단계별로 비교합니다.")
        steps = ["visit","signup","first_play","subscribe"]
        counts = [df_demo.query("event==@s").shape[0] for s in steps]
        conv = [100] + [round(counts[i]/counts[i-1]*100,1) if counts[i-1] else 0 for i in range(1,len(steps))]

        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(steps, conv, marker="o", color="#1DB954")
        ax.set_ylim(0,105); ax.set_ylabel("Conversion %", color="#CFE3D8")
        ax.set_facecolor("#191414"); fig.set_facecolor("#121212")
        ax.tick_params(colors="#CFE3D8")
        try: sp(fig)
        except: st.pyplot(fig, use_container_width=True)

    # -------------------------------
    # ② Activation (간단 예시: 가입→첫 재생 비율/시간)
    # -------------------------------
    with tabs[1]:
        st.subheader("Activation")
        st.caption("가입 직후 첫 재생까지의 활성화 지표(예시). 실제 지표로 교체 권장.")

        # 예시 1) 가입 → 첫 재생 전환율 유사 지표
        daily = df_demo.groupby("date")["event"].count().sort_index()
        act_like = (daily.rolling(7).mean()/(daily.rolling(7).max()+1e-9)*100).fillna(0)

        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(act_like.index, act_like.values, color="#80DEEA")
        ax.set_ylabel("Activation-like %", color="#CFE3D8"); ax.set_xlabel("date", color="#CFE3D8")
        ax.set_facecolor("#191414"); fig.set_facecolor("#121212"); ax.tick_params(colors="#CFE3D8")
        try: sp(fig)
        except: st.pyplot(fig, use_container_width=True)

    # -------------------------------
    # ③ Retention (기존 유지율 예시)
    # -------------------------------
    with tabs[2]:
        st.subheader("Retention")
        st.caption("N-Day/Weekly 커브 예시 (실데이터로 교체 권장).")
        daily = df_demo.groupby("date")["event"].count().sort_index()
        roll = (daily.rolling(7).mean() / (daily.rolling(7).max()+1e-9) * 100).fillna(0)

        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(roll.index, roll.values, color="#80DEEA")
        ax.set_ylabel("Retention-like %", color="#CFE3D8"); ax.set_xlabel("date", color="#CFE3D8")
        ax.set_facecolor("#191414"); fig.set_facecolor("#121212"); ax.tick_params(colors="#CFE3D8")
        try: sp(fig)
        except: st.pyplot(fig, use_container_width=True)

    # -------------------------------
    # ④ Revenue (★ 네 파트: 우리가 만든 CSV 사용)
    # -------------------------------
    with tabs[3]:
        # sections/revenue.py  — simple & robust + captions + insights box
        import os, glob
        import pandas as pd
        import numpy as np
        import streamlit as st
        import matplotlib.pyplot as plt

        SPOTIFY_GREEN = "#1DB954"
        ACCENT_CYAN   = "#80DEEA"
        BG_DARK       = "#121212"
        PLOT_DARK     = "#191414"
        TICK_COLOR    = "#CFE3D8"

        def load_csv(name: str):
            """ /data/name 우선, 루트/name 보조 (캐시 없음) """
            for p in (os.path.join("data", name), name):
                if os.path.exists(p):
                    return pd.read_csv(p)
            return None

        def render():
            st.title("💰 Revenue")
            st.caption("CSV(export) 기반 KPI / 트렌드 / 취향별 LTV / 중요 요인")

            # ---------- 1) 파일 로드 ----------
            kpi  = load_csv("out_revenue_kpis.csv")
            retm = load_csv("out_premium_retention_monthly.csv")
            arpu = load_csv("out_arpu_monthly.csv")
            pref = load_csv("out_pref_group_summary.csv")
            sig  = load_csv("out_pref_significance_tests.csv")
            imp  = load_csv("out_feature_importance_ltv.csv")

            missing = [n for n,d in {
                "out_revenue_kpis.csv":kpi,
                "out_premium_retention_monthly.csv":retm,
                "out_arpu_monthly.csv":arpu,
                "out_pref_group_summary.csv":pref,
                "out_pref_significance_tests.csv":sig,
                "out_feature_importance_ltv.csv":imp
            }.items() if d is None]

            if missing:
                st.warning("다음 파일을 찾지 못했습니다:\n- " + "\n- ".join(missing))
                st.info("노트북 STEP6에서 /data 폴더로 export 후, 앱을 Rerun 하세요.")
                return

            # ---------- 2) KPI ----------
            conv  = float(kpi.loc[kpi.metric=="conversion_rate","value"])
            rmean = float(kpi.loc[kpi.metric=="premium_retention_mean","value"])
            arpu_v= float(kpi.loc[kpi.metric=="arpu_overall","value"])
            dur   = float(kpi.loc[kpi.metric=="avg_premium_duration","value"])

            c1,c2,c3,c4 = st.columns(4)
            c1.metric("전환율",           f"{conv*100:.1f}%")
            c2.metric("유지율(평균)",      f"{rmean*100:.1f}%")
            c3.metric("ARPU(원)",         f"{arpu_v:,.0f}")
            c4.metric("평균 Premium 기간", f"{dur:.2f}개월")

            with st.expander("KPI 계산식(분자/분모)"):
                st.markdown(
                    "- **전환율** = 이후 Premium으로 바뀐 사용자 수 / 처음 Free 사용자 수\n"
                    "- **유지율(A→B)** = A,B 둘 다 Premium 사용자 수 / A의 Premium 사용자 수\n"
                    "- **ARPU** = revenue 총합 / 전체 유저-월 수\n"
                    "- **평균 Premium 기간** = 사용자별 Premium 개월수 평균\n"
                    "- **LTV(유저)** = 사용자별 revenue 합 (표는 그룹 평균)"
                )

            # ---------- 3) Retention & ARPU Trend ----------
            st.markdown("### 📈 Retention & ARPU Trend")
            col1, col2 = st.columns(2)

            # Retention
            with col1:
                x = retm["from_to"].tolist()
                y = retm["premium_retention"].tolist()
                fig, ax = plt.subplots(figsize=(6,3))
                ax.plot(range(len(x)), y, marker="o", color=SPOTIFY_GREEN, linewidth=2)
                ax.set_xticks(range(len(x))); ax.set_xticklabels(x, rotation=0)
                ax.set_ylim(0,1.05); ax.set_facecolor(PLOT_DARK); fig.set_facecolor(BG_DARK)
                ax.tick_params(colors=TICK_COLOR)
                st.pyplot(fig, use_container_width=True)
                # 한 줄 설명
                try:
                    best_i = int(np.nanargmax(y)); st.caption(f"• 유지율 최고 구간: **{x[best_i]} = {y[best_i]*100:.1f}%**")
                except Exception:
                    st.caption("• 유지율 추세를 보여줍니다.")

            # ARPU
            with col2:
                x2 = arpu["month"].tolist()
                y2 = arpu["arpu"].tolist()
                fig, ax = plt.subplots(figsize=(6,3))
                ax.plot(range(len(x2)), y2, marker="o", color=ACCENT_CYAN, linewidth=2)
                ax.set_xticks(range(len(x2))); ax.set_xticklabels(x2, rotation=0)
                ax.set_facecolor(PLOT_DARK); fig.set_facecolor(BG_DARK)
                ax.tick_params(colors=TICK_COLOR)
                st.pyplot(fig, use_container_width=True)
                # 한 줄 설명
                try:
                    best_i = int(np.nanargmax(y2)); st.caption(f"• ARPU 최고 월: **{x2[best_i]} = {y2[best_i]:,.0f}원**")
                except Exception:
                    st.caption("• 월별 ARPU 변화를 보여줍니다.")

            # ---------- 4) 취향별 평균 LTV (깔끔 뷰) ----------
            st.markdown("### 🎧 취향별 평균 LTV")
            def pick_group(row):
                col = row["variable"]
                return row[col] if col in row.index else None
            view = pref.copy()
            view["group"] = view.apply(pick_group, axis=1)
            view = view[["variable","group","users","avg_ltv","avg_premium_duration",
                        "avg_monthly_revenue","free_to_premium_rate"]].sort_values("avg_ltv", ascending=False)

            with st.expander("Top 10 보기"):
                st.dataframe(view.head(10), use_container_width=True)
            # 한 줄 설명
            try:
                top_row = view.iloc[0]
                st.caption(f"• LTV 최고 세그먼트: **{top_row['variable']} = {top_row['group']}**, 평균 LTV **{top_row['avg_ltv']:,.0f}원**")
            except Exception:
                st.caption("• 취향별 평균 LTV 상위 그룹을 보여줍니다.")

            # ---------- 5) 유의 변수 ----------
            st.markdown("### 🔍 통계적으로 유의한 요인 (p<0.05)")
            sig_view = sig.query("p_value < 0.05").sort_values("p_value")
            st.dataframe(sig_view.head(10), use_container_width=True)
            # 한 줄 설명
            try:
                srow = sig_view.iloc[0]
                st.caption(f"• 가장 강한 통계적 차이: **{srow['feature']}** ({srow['test_type']}), p-value={srow['p_value']:.2e}")
            except Exception:
                st.caption("• p<0.05 변수들이 전환/LTV에 유의미한 차이를 보입니다.")

            # ---------- 6) Feature Importance ----------
            st.markdown("### 🌲 LTV 영향 요인")
            if imp.shape[1] == 2:
                imp.columns = ["feature","importance"]
            else:
                imp = imp.rename(columns={imp.columns[0]:"feature", imp.columns[1]:"importance"})
            topk = imp.sort_values("importance", ascending=False).head(10)

            fig, ax = plt.subplots(figsize=(10,3.2))
            ax.bar(range(len(topk)), topk["importance"], color=SPOTIFY_GREEN)
            ax.set_xticks(range(len(topk))); ax.set_xticklabels(topk["feature"], rotation=0)
            ax.set_facecolor(PLOT_DARK); fig.set_facecolor(BG_DARK); ax.tick_params(colors=TICK_COLOR)
            ax.set_ylabel("Importance", color=TICK_COLOR)
            st.pyplot(fig, use_container_width=True)
            # 한 줄 설명
            try:
                fr, fv = topk.iloc[0]["feature"], topk.iloc[0]["importance"]
                st.caption(f"• LTV에 가장 큰 영향: **{fr}** (중요도 {fv:.3f})")
            except Exception:
                st.caption("• 랜덤포레스트 기준 상위 영향 요인을 보여줍니다.")

            # ---------- 7) 종합 인사이트 박스 ----------
            try:
                best_ret_idx = int(np.nanargmax(retm["premium_retention"].values))
                best_ret = f"{retm.iloc[best_ret_idx]['from_to']} ({retm.iloc[best_ret_idx]['premium_retention']*100:.1f}%)"
            except Exception:
                best_ret = "—"

            try:
                best_arpu_idx = int(np.nanargmax(arpu['arpu'].values))
                best_arpu = f"{arpu.iloc[best_arpu_idx]['month']} ({arpu.iloc[best_arpu_idx]['arpu']:,.0f}원)"
            except Exception:
                best_arpu = "—"

            try:
                seg = view.iloc[0]
                best_seg = f"{seg['variable']} = {seg['group']} (LTV {seg['avg_ltv']:,.0f}원)"
            except Exception:
                best_seg = "—"

            try:
                top_feat = topk.iloc[0]["feature"]
            except Exception:
                top_feat = "—"

            st.markdown("---")
            st.success(
                "### 📦 종합 인사이트\n"
                f"- 전환율 **{conv*100:.1f}%**, 평균 유지율 **{rmean*100:.1f}%**, ARPU **{arpu_v:,.0f}원**, 평균 Premium 기간 **{dur:.2f}개월**\n"
                f"- 유지율 최고 구간: **{best_ret}** / ARPU 최고 월: **{best_arpu}**\n"
                f"- LTV 상위 세그먼트: **{best_seg}**\n"
                f"- LTV 최상위 영향 요인: **{top_feat}**\n"
                "→ **전략 제안:** 상위 세그먼트 타깃 프로모션(개인화 추천·플랜 번들), 유지율이 낮은 월에는 리텐션 캠페인(리마인드·추천 푸시)을 집중 운영."
            )

            st.caption("※ 파일은 Jupyter STEP6 export 결과(/data 또는 프로젝트 루트)에서 읽습니다.")

else:
    tabs = st.tabs(["Insights", "Strategy", "Next Steps"])
    with tabs[0]:
        st.markdown('<div class="cup-h2">Key Insights by AARRR Stage</div>', unsafe_allow_html=True); tight_top(-36)
        st.markdown("""
        <div class="cup-card">
          • Activation: 첫 재생 구간 이탈 높음 → 온보딩·첫 추천 큐레이션 개선<br>
          • Retention: 7일 복귀율 급락 → 리마인드/추천 콘텐츠 자동화<br>
          • Revenue: 상위 사용자 매출 편중 → VIP 업셀링·연간 구독 제안
        </div>
        """, unsafe_allow_html=True)
    with tabs[1]:
        st.markdown('<div class="cup-h2">Data-driven Strategy Proposal</div>', unsafe_allow_html=True); tight_top(-36)
        st.markdown("""
        <div class="cup-card">
          ① 온보딩 개선(튜토리얼 간소화, 첫 추천 강화)<br>
          ② 휴면 징후 타깃 푸시/이메일 자동화<br>
          ③ VIP 세그먼트 리워드/장기 구독 유도 캠페인<br>
          ④ 추천·공유 인센티브 단순화
        </div>
        """, unsafe_allow_html=True)
    with tabs[2]:
        st.markdown('<div class="cup-h2">Limitations & Next Steps</div>', unsafe_allow_html=True); tight_top(-36)
        st.markdown("""
        <div class="cup-card">
          관찰 기간·외생 변수 제한 → 외부 데이터 결합 및 예측모델(이탈 예측·LTV 추정) 확장
        </div>
        """, unsafe_allow_html=True)