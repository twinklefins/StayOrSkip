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
            st.markdown("""
            <style>
            .cup-hover-card {
                transition: all .25s ease;
                background: rgba(255,255,255,.03);
                border: 1px solid rgba(255,255,255,.10);
                border-radius: 12px;
                padding: 1.6rem 1.8rem;
            }
            .cup-hover-card:hover {
                background: rgba(255,255,255,.08);
                border-color: rgba(255,255,255,.18);
                transform: translateY(-4px);
                box-shadow: 0 0 15px rgba(29,185,84,.25);
            }
            .cup-scene {
                background: linear-gradient(145deg, rgba(29,185,84,.10), rgba(255,255,255,.02));
                border: 1px solid rgba(29,185,84,.25);
                border-radius: 14px;
                padding: 2.2rem 2.8rem;
                margin-top: 2.2rem;
                text-align: center;
                font-size: 1.08rem;
                line-height: 1.95;
                color: rgba(255,255,255,.92);
                box-shadow: 0 0 20px rgba(29,185,84,.15);
            }
            .cup-scene strong { color: #1ED760; font-weight: 700; }
            .cup-scene em { color: rgba(255,255,255,.85); font-style: italic; }
            .cup-scene-title {
                font-weight: 800;
                font-size: 1.3rem;
                color: #1DB954;
                margin-bottom: 1.0rem;
            }
            .cup-one-liner {
                font-size: 1.1rem;
                font-weight: 600;
                color: #D7E4DC;
                text-align: center;
                margin-top: 2.0rem;
                margin-bottom: -0.8rem;
                letter-spacing: 0.2px;
            }
            </style>

            <!-- 기존 3열 카드 -->
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem;">
            <div class="cup-hover-card" style="text-align:center;">
                <p style="font-size:1.5rem;">📈</p>
                <p style="font-weight:800;font-size:1.1rem;margin-bottom:1rem;">스트리밍 시장 성장과 도전</p>
                <p style="color:rgba(255,255,255,.9);font-size:1.05rem;line-height:1.85;">
                글로벌 시장 급성장, 유입률↑ 이탈률↑<br>
                높은 경쟁 속 체험 후 구독 전환율 하락<br>
                콘텐츠 피로도·사용자 유지가 핵심 과제로 부상
                </p>
            </div>

            <div class="cup-hover-card" style="text-align:center;">
                <p style="font-size:1.5rem;">🎧</p>
                <p style="font-weight:800;font-size:1.1rem;margin-bottom:1rem;">Spotify의 강점</p>
                <p style="color:rgba(255,255,255,.9);font-size:1.05rem;line-height:1.85;">
                세계 최대 규모 청취 로그 및 오디오 피처 데이터 보유<br>
                유저 행동 여정·이탈 패턴 분석에 최적화된 플랫폼
                </p>
            </div>

            <div class="cup-hover-card" style="text-align:center;">
                <p style="font-size:1.5rem;">🧭</p>
                <p style="font-weight:800;font-size:1.1rem;margin-bottom:1rem;">AARRR 기반 분석 방향</p>
                <p style="color:rgba(255,255,255,.9);font-size:1.05rem;line-height:1.85;">
                Acquisition → Retention → Revenue<br>
                단계별 핵심 지표 정의<br>
                데이터 기반 리텐션·LTV 개선 전략 제안
                </p>
            </div>
            </div>

            <!-- 🎬 시네마틱 도입부 -->
            <div class="cup-one-liner">“Retention is the new acquisition — 남게 만드는 전략이 Spotify Korea의 성장을 결정한다.”</div>

            <div class="cup-scene">
            <div class="cup-scene-title">🎬 가상 시나리오 — <strong>Spotify Korea TF</strong></div>
            <p>한때 ‘음악은 스킵, 구독은 무료’로 시작된 그들의 여정.<br>
            무료의 달콤함만 맛보고 사라진 <strong>‘구독 유목민들’</strong>이 늘어났다.<br>
            <p><strong>Spotify Korea TF</strong>는 데이터로 그들의 발자국을 추적한다.<br>
            <em>“그들은 왜 떠났을까? 그리고 어떻게 다시 머물게 할 수 있을까?”</em><br>
            리텐션 미션을 위해 모인 <strong>데이터컵밥 팀</strong>의 분석이 시작된다.</p>
            </div>
            """, unsafe_allow_html=True)


    # ---- Dataset (tabs[3]) ----
    with tabs[3]:
        # --- Dataset Overview (간격 통일: section_title 사용) ---
        section_title("Dataset Overview")

        # 요약값
        n_rows, n_cols = tidy.shape
        month_min = tidy["month"].min() if "month" in tidy.columns else "—"
        month_max = tidy["month"].max() if "month" in tidy.columns else "—"

        # ✅ “주요 컬럼”은 실제 분석 핵심만: userid, month, subscription_plan, revenue_num
        # (timestamp 는 기록용이라 Full Column List 에서만 노출)
        key_cols_txt = "userid, month, revenue_num, subscription_plan"

        st.markdown(f"""
        <div class="cup-card" style="margin-top:0.3rem;">
        <b>데이터셋명</b>: Spotify User Behavior Dataset
        <b>규모</b>: {n_rows:,}행, {n_cols}개 컬럼<br>
        <b>주요 컬럼</b>: userid, month, revenue_num, subscription_plan<br>
        <b>출처</b>: Kaggle Spotify 사용자행동 데이터 + 추가 생성한 프리미엄 구독료(6개월) 컬럼 병합 (merged)
        </div>
        """, unsafe_allow_html=True)

        # --- 기존 핵심 요약표 아래에 추가 ---
        section_title("Full Column List", "머지드 데이터셋의 전체 컬럼 및 설명 요약", top_gap=10, bottom_gap=6)

        # 전체 컬럼 설명 자동 생성
        all_columns = [
            ("userid", "사용자 고유 ID"),
            ("month", "관측 월 (2023-01 ~ 2023-06)"),
            ("revenue", "월별 매출액 (문자형 원화 표시)"),
            ("subscription_plan", "요금제 유형 (Free / Premium)"),
            ("timestamp", "응답 시각 (설문 타임스탬프)"),
            ("Age", "사용자 연령대"),
            ("Gender", "사용자 성별"),
            ("spotify_usage_period", "Spotify 사용 기간"),
            ("spotify_listening_device", "주 청취 기기"),
            ("spotify_subscription_plan", "Spotify 계정의 요금제 정보"),
            ("premium_sub_willingness", "프리미엄 구독 의향 (예/아니오)"),
            ("preffered_premium_plan", "선호 프리미엄 요금제 유형"),
            ("preferred_listening_content", "주 청취 콘텐츠 (Music / Podcast 등)"),
            ("fav_music_genre", "가장 선호하는 음악 장르"),
            ("music_time_slot", "주 청취 시간대 (출근/퇴근/야간 등)"),
            ("music_Influencial_mood", "음악 선택에 영향을 주는 감정 상태"),
            ("music_lis_frequency", "음악 청취 빈도"),
            ("music_expl_method", "음악 탐색 방법 (추천/검색/친구 공유 등)"),
            ("music_recc_rating", "음악 추천 만족도 (1~5점 척도)"),
            ("pod_lis_frequency", "팟캐스트 청취 빈도"),
            ("fav_pod_genre", "선호 팟캐스트 장르"),
            ("preffered_pod_format", "선호 팟캐스트 형식 (토크/뉴스 등)"),
            ("pod_host_preference", "선호하는 진행자 스타일"),
            ("preffered_pod_duration", "선호 팟캐스트 길이"),
            ("pod_variety_satisfaction", "팟캐스트 다양성 만족도"),
        ]

        df_cols = pd.DataFrame(all_columns, columns=["컬럼명", "설명"])
        st.dataframe(df_cols, hide_index=True, use_container_width=True)
        vgap(20)

        # Preview
        section_title("Dataset Preview", "데이터 상위 5행 미리보기", top_gap=12, bottom_gap=12)
        st.dataframe(tidy.head(5), use_container_width=True)
        vgap(16)

        # ===== 인터랙티브 차트들 (Altair) =====
        # 공통 테마
        brand = "#1DB954"
        muted = "rgba(255,255,255,0.65)"

        # 1) 월별 매출 라인 (툴팁+줌)
        section_title("Monthly Revenue Trend", "월별 총매출 추이(₩)")
        rev_col = "revenue_num" if "revenue_num" in tidy.columns else "revenue"
        df_rev = tidy[["month", rev_col]].copy()
        # revenue 문자열일 수 있어 숫자화 한번 더 안전 처리
        if rev_col == "revenue":
            df_rev[rev_col] = (
                df_rev[rev_col]
                .astype(str)
                .str.replace(r"[^0-9.\-]", "", regex=True)
                .replace("", np.nan)
                .astype(float)
            )
        # 월을 날짜형으로(가로 정렬 예쁘게)
        df_rev["month_dt"] = pd.to_datetime(df_rev["month"].astype(str) + "-01", errors="coerce")
        monthly = df_rev.groupby("month_dt", as_index=False)[rev_col].sum()

        selector = alt.selection_interval(encodings=["x"])
        line = (
            alt.Chart(monthly)
            .mark_line(point=True)
            .encode(
                x=alt.X("month_dt:T", axis=alt.Axis(title="Month", labelAngle=0)),
                y=alt.Y(f"{rev_col}:Q", axis=alt.Axis(title="Revenue (₩)")),
                tooltip=[alt.Tooltip("month_dt:T", title="Month"),
                        alt.Tooltip(f"{rev_col}:Q", title="Revenue", format=",.0f")]
            )
            .properties(height=320)
            .interactive()
            .add_params(selector)
            .configure_mark(color=brand)
            .configure_axis(labelColor=muted, titleColor=muted, grid=True, gridOpacity=0.12)
        )
        st.altair_chart(line, use_container_width=True)
        vgap(18)

        # 2) 최신월 요금제별 활성 사용자 바 (툴팁+정렬)
        section_title("Active Users by Plan — Latest Month", "최신 월 기준 요금제별 고유 사용자 수")
        if {"month", "userid"} <= set(tidy.columns):
            plan_col = "subscription_plan" if "subscription_plan" in tidy.columns else \
                    ("spotify_subscription_plan" if "spotify_subscription_plan" in tidy.columns else None)
            if plan_col:
                latest = tidy["month"].max()
                users_mix = (
                    tidy[tidy["month"] == latest]
                    .groupby(plan_col)["userid"].nunique()
                    .reset_index(name="users")
                    .sort_values("users", ascending=False)
                )
                ch_users = (
                    alt.Chart(users_mix)
                    .mark_bar()
                    .encode(
                        x=alt.X("users:Q", title="Users (unique)"),
                        y=alt.Y(f"{plan_col}:N", sort="-x", title=None),
                        tooltip=[alt.Tooltip(f"{plan_col}:N", title="Plan"),
                                alt.Tooltip("users:Q", title="Users", format=",.0f")],
                        color=alt.value(brand)
                    )
                    .properties(height=220)
                    .configure_axis(labelColor=muted, titleColor=muted)
                )
                st.altair_chart(ch_users, use_container_width=True)
            else:
                st.info("요금제 컬럼을 찾을 수 없어요.")
        else:
            st.info("month / userid 컬럼이 필요합니다.")
        vgap(18)

        # 3) 요금제별 총 매출 바
        section_title("Revenue by Plan (Total)", "관측 기간 동안 요금제별 총 매출 합계")
        if plan_col and rev_col in tidy.columns:
            plan_rev = (
                tidy.groupby(plan_col, as_index=False)[rev_col]
                .sum().rename(columns={rev_col: "revenue_sum"})
                .sort_values("revenue_sum", ascending=False)
            )
            ch_rev = (
                alt.Chart(plan_rev)
                .mark_bar()
                .encode(
                    x=alt.X("revenue_sum:Q", title="Revenue (₩)"),
                    y=alt.Y(f"{plan_col}:N", sort="-x", title=None),
                    tooltip=[alt.Tooltip(f"{plan_col}:N", title="Plan"),
                            alt.Tooltip("revenue_sum:Q", title="Revenue", format=",.0f")],
                    color=alt.value(brand)
                )
                .properties(height=220)
                .configure_axis(labelColor=muted, titleColor=muted)
            )
            st.altair_chart(ch_rev, use_container_width=True)
        else:
            st.info("요금제/매출 컬럼이 없어 매출 구성을 그릴 수 없어요.")
        vgap(18)

        # 4) 데이터 정합성 & 결측치
        section_title("Data Quality Check", "결측치 현황 및 데이터 정합성")
        st.markdown(f"""
        <div class="cup-card">
        - 병합 기준: <b>userid</b> (매출 ⟷ 원본 설문)<br>
        - 기간/규모: <b>{month_min} ~ {month_max}</b>, <b>{n_rows:,}행</b><br>
        - 매출 기준: <b>Premium만 유료매출</b> (Free=0원)
        </div>
        """, unsafe_allow_html=True)

        na = tidy.isna().sum().sort_values(ascending=False)
        na_top = na[na > 0].head(5).reset_index()
        na_top.columns = ["column", "na_cnt"]

        if len(na_top) > 0:
            ch_na = (
                alt.Chart(na_top)
                .mark_bar()
                .encode(
                    x=alt.X("na_cnt:Q", title="Missing Values"),
                    y=alt.Y("column:N", sort="-x", title=None),
                    tooltip=[alt.Tooltip("column:N", title="Column"),
                            alt.Tooltip("na_cnt:Q", title="Missing", format=",.0f")],
                    color=alt.value("#BFBFBF")
                )
                .properties(height=220)
                .configure_axis(labelColor=muted, titleColor=muted)
            )
            st.altair_chart(ch_na, use_container_width=True)
        else:
            st.markdown("<div class='cup-card'>결측치 상위 5개 컬럼 요약입니다. 이상 없으면 완료 메시지를 표시합니다.</div>", unsafe_allow_html=True)

        # 정합성 요약 + 완료 배지 (간격 넉넉)
        vgap(10)
        total_rev_val = tidy.get("revenue_num", tidy.get("revenue", 0))
        try:
            total_rev = int(np.nansum(
                pd.to_numeric(total_rev_val, errors="coerce")
            ))
        except Exception:
            total_rev = 0

        st.markdown(f"""
        <div class="cup-card">
        ✅ <b>정합성 요약</b><br>
        - 사용자 수: <b>{tidy['userid'].nunique():,}</b>명 · 기간: <b>{month_min} ~ {month_max}</b><br>
        - 총 매출(합산): <b>₩{total_rev:,.0f}</b><br>
        - 분석 가능 상태: <b>양호</b>
        </div>
        """, unsafe_allow_html=True)

        st.success("✅ 데이터 병합 및 품질 검증 완료 — 분석에 활용 가능합니다.")
        vgap(12)

elif section == "DATA EXPLORATION":
    tabs = st.tabs(["Cleaning", "EDA", "Metrics Definition"])
    with tabs[0]:
        st.markdown('<div class="cup-h2">Data Cleaning & Preprocessing</div>', unsafe_allow_html=True); tight_top(-36)
        st.markdown('<div class="cup-card">결측/이상치 처리, 타입 정규화, 세션 집계, 파생변수 생성 기준을 명시합니다.</div>', unsafe_allow_html=True)
    with tabs[1]:
        st.markdown('<div class="cup-h2">Exploratory Data Analysis (EDA)</div>', unsafe_allow_html=True); tight_top(-36)
        st.markdown('<div class="cup-card">채널별 유입 분포, 활동량 분포, 이탈 여부에 따른 차이를 탐색합니다.</div>', unsafe_allow_html=True)
    with tabs[2]:
        st.markdown('<div class="cup-h2">AARRR Metrics Definition</div>', unsafe_allow_html=True); tight_top(-36)
        st.markdown("""
| Stage | Metric (예시) | 계산 개념 |
|---|---|---|
| Acquisition | 신규 유저 수 | 특정 기간 내 최초 가입 수 |
| Activation | 첫 재생 완료율 | first_play / signup |
| Retention | N-day 유지율 | 기준일 대비 N일 후 복귀 비율 |
| Revenue | ARPU/LTV | 매출 / 활성 사용자 수, 누적 기여 |
| Referral | 초대/공유율 | 공유 건수 / 활성 사용자 수 |
""")

elif section == "AARRR DASHBOARD":
    st.markdown('<div class="cup-h2">Visual Analytics Dashboard</div>', unsafe_allow_html=True); tight_top(-36)
    tabs = st.tabs(["Funnel", "Retention", "Cohort", "LTV"])
    with tabs[0]:
        st.subheader("Funnel Analysis"); st.caption("가입 → 첫 재생 → 구독 전환율을 단계별로 비교합니다.")
        steps = ["visit","signup","first_play","subscribe"]
        counts = [df_demo.query("event==@s").shape[0] for s in steps]
        conv = [100] + [round(counts[i]/counts[i-1]*100,1) if counts[i-1] else 0 for i in range(1,len(steps))]
        fig, ax = plt.subplots(figsize=(6,3)); ax.plot(steps, conv, marker="o", color="#1DB954")
        ax.set_ylim(0,105); ax.set_ylabel("Conversion %", color="#CFE3D8"); ax.set_facecolor("#191414"); fig.set_facecolor("#121212")
        ax.tick_params(colors="#CFE3D8"); sp(fig)
    with tabs[1]:
        st.subheader("Retention Analysis"); st.caption("N-Day/Weekly 커브 예시 (실데이터로 교체 권장).")
        daily = df_demo.groupby("date")["event"].count().sort_index()
        roll = (daily.rolling(7).mean() / (daily.rolling(7).max()+1e-9) * 100).fillna(0)
        fig, ax = plt.subplots(figsize=(6,3)); ax.plot(roll.index, roll.values, color="#80DEEA")
        ax.set_ylabel("Retention-like %", color="#CFE3D8"); ax.set_xlabel("date", color="#CFE3D8")
        ax.set_facecolor("#191414"); fig.set_facecolor("#121212"); ax.tick_params(colors="#CFE3D8"); sp(fig)
    with tabs[2]:
        st.subheader("Cohort Analysis"); st.info("가입월 × 경과주 코호트 유지율 히트맵(추가 예정).")
    with tabs[3]:
        st.subheader("LTV Analysis")
        last30 = df_demo[df_demo["date"] >= (df_demo["date"].max() - pd.Timedelta(days=30))]
        rev = last30["amount"].sum(); active = max(int(last30["event"].nunique()*100), 1)
        arpu = rev / active; c1, c2 = st.columns(2)
        c1.metric("총 수익(30일, 예시)", f"${rev:,.0f}"); c2.metric("ARPU(30일, 예시)", f"${arpu:,.2f}")
    st.caption("※ Assumptions: 관찰기간=30일, 환불/부가세 제외, 할인율 0%, 예시 값")

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