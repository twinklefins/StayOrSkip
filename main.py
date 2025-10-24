# =============================
# 🎵 Stay or Skip — Main Streamlit App
# =============================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path
import base64
import os

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

def render_image(filename: str):
    """같은 폴더 우선, 실패 시 GitHub Raw로 폴백(경고 없이 조용히 패스)"""
    p = BASE / filename
    # 1) 로컬
    try:
        with open(p, "rb") as f:
            _st_image_compat(f.read())
        return
    except Exception:
        pass
    # 2) GitHub Raw
    try:
        import urllib.request
        url = f"{RAW_BASE}/{filename}"
        with urllib.request.urlopen(url, timeout=6) as resp:
            _st_image_compat(resp.read())
        return
    except Exception:
        pass
    # 3) 패스

def img_to_datauri(filename: str) -> str:
    """이미지를 data URI로 변환(로컬→실패 시 GitHub Raw 폴백)"""
    p = BASE / filename
    # 로컬
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

# ---------- 데이터 로드 ----------
@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_excel(BASE / "spotify_merged.xlsx")

try:
    tidy = load_data()
except FileNotFoundError:
    st.error("`spotify_merged.xlsx` 파일을 찾을 수 없습니다. StayOrSkip 폴더에 올려주세요.")
    st.stop()
except Exception as e:
    st.exception(e)
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
</style>
""", unsafe_allow_html=True)

# ================= Sidebar =================
with st.sidebar:
    st.caption("build: v2025-10-24-spotify-compat-2")  # ← 새 코드 적용 확인용
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

# ================= Demo data (페이지 데모용) =================
np.random.seed(42)
dates = pd.date_range("2025-01-01", periods=60, freq="D")
df = pd.DataFrame({
    "date": np.random.choice(dates, 1000),
    "channel": np.random.choice(["SNS","Search","Ad"], 1000, p=[0.45,0.35,0.20]),
    "event": np.random.choice(["visit","signup","first_play","subscribe"], 1000, p=[0.45,0.25,0.20,0.10]),
    "amount": np.random.gamma(2.2, 6.0, 1000).round(2)
})

# ================= Title =================
icon_datauri = img_to_datauri("StayOrSkip/free-icon-play-4604241.png")
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
        st.markdown('<div class="cup-h2">Team Introduction</div>', unsafe_allow_html=True)
        tight_top(-36)
        st.markdown("<style>.cup-logo{ display:block; margin:-1.2rem 0 2.2rem 0; width:35%; max-width:520px; height:auto; }</style>", unsafe_allow_html=True)
        logo_uri = img_to_datauri("Cup_8_copy_2.png")
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
        st.markdown('<div class="cup-h2">About Spotify</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="cup-h2">Background & Objectives</div>', unsafe_allow_html=True)
        tight_top(-36)
        st.markdown("""
        <style>
          .cup-hover-card { transition:all .25s ease; background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.10); border-radius:12px; padding:1.6rem 1.8rem; }
          .cup-hover-card:hover { background:rgba(255,255,255,.08); border-color:rgba(255,255,255,.18); transform:translateY(-4px); box-shadow:0 0 15px rgba(29,185,84,.25); }
        </style>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem;">
          <div class="cup-hover-card" style="text-align:center;"><p style="font-size:1.5rem;">📈</p>
            <p style="font-weight:800;font-size:1.1rem;margin-bottom:1rem;">스트리밍 시장 성장과 도전</p>
            <p style="color:rgba(255,255,255,.9);font-size:1.05rem;line-height:1.85;">글로벌 시장 급성장, 유입률↑ 이탈률↑<br>높은 경쟁 속 체험 후 구독 전환율 하락<br>콘텐츠 피로도·사용자 유지가 핵심 과제로 부상</p>
          </div>
          <div class="cup-hover-card" style="text-align:center;"><p style="font-size:1.5rem;">🎧</p>
            <p style="font-weight:800;font-size:1.1rem;margin-bottom:1rem;">Spotify의 강점</p>
            <p style="color:rgba(255,255,255,.9);font-size:1.05rem;line-height:1.85;">세계 최대 규모 청취 로그 및 오디오 피처 데이터 보유<br>유저 행동 여정·이탈 패턴 분석에 최적화된 플랫폼</p>
          </div>
          <div class="cup-hover-card" style="text-align:center;"><p style="font-size:1.5rem;">🧭</p>
            <p style="font-weight:800;font-size:1.1rem;margin-bottom:1rem;">AARRR 기반 분석 방향</p>
            <p style="color:rgba(255,255,255,.9);font-size:1.05rem;line-height:1.85;">Acquisition → Retention → Revenue<br>단계별 핵심 지표 정의<br>데이터 기반 리텐션·LTV 개선 전략 제안</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ---- Dataset (tabs[3]) ----
    with tabs[3]:
        st.markdown('<div class="cup-h2">Dataset Overview</div>', unsafe_allow_html=True)
        tight_top(-36)
        st.markdown("""
        <div class="cup-card">
          <b>데이터셋명</b>: Spotify User Behavior + Revenue Dataset — 2023.01–06<br>
          <b>규모</b>: 3,120행 (6개월 × 520명), 24개 컬럼<br>
          <b>주요 컬럼</b>: userid, month, revenue, subscription_plan, timestamp, fav_music_genre 등<br>
          <b>출처</b>: Kaggle Spotify User Behavior Dataset + 강사 제공 매출지표
        </div>
        """, unsafe_allow_html=True)

        # Preview
        st.markdown("#### 📂 Dataset Preview  \n<span style='font-size:0.9rem;color:#888;'>데이터 상위 5행 미리보기</span>", unsafe_allow_html=True)
        st.dataframe(tidy.head(5))

        # Monthly Revenue
        st.markdown("#### 💹 Monthly Revenue Trend  \n<span style='font-size:0.9rem;color:#888;'>월별 매출 추이</span>", unsafe_allow_html=True)
        monthly = tidy.groupby("month")["revenue"].sum().reset_index()
        fmt_million_krw = FuncFormatter(lambda x, pos: f"₩{x/1_000_000:,.0f}M")
        fig_tr, ax_tr = plt.subplots(figsize=(6.5, 3.6))
        ax_tr.plot(monthly["month"], monthly["revenue"], marker="o", linewidth=2.5, color="#1DB954")
        ax_tr.set_xlabel("Month"); ax_tr.set_ylabel("Revenue (₩, 백만원 단위)")
        ax_tr.yaxis.set_major_formatter(fmt_million_krw); ax_tr.grid(alpha=0.2)
        plt.tight_layout(); sp(fig_tr)

        # Plan Comparison
        st.markdown("#### 📊 Plan Comparison Overview  \n<span style='font-size:0.9rem;color:#888;'>요금제별 매출·이용자 비중 비교</span>", unsafe_allow_html=True)
        col_left, col_right = st.columns(2, gap="medium")

        with col_left:
            plan_rev = tidy.groupby("subscription_plan")["revenue"].sum().reset_index()
            order = ["Free (ad-supported)", "Premium (paid subscription)"]
            plan_rev["subscription_plan"] = pd.Categorical(plan_rev["subscription_plan"], order, True)
            plan_rev = plan_rev.sort_values("subscription_plan")
            fig_rs, ax_rs = plt.subplots(figsize=(5, 3.6))
            pie_out = ax_rs.pie(
                plan_rev["revenue"], labels=None, autopct="%1.1f%%", startangle=90,
                colors=["#BFBFBF", "#1DB954"], pctdistance=0.75, wedgeprops=dict(width=0.35)
            )
            wedges, *_ = pie_out  # 버전 호환
            ax_rs.set_title("Revenue (₩) Share", pad=6)
            ax_rs.legend(wedges, plan_rev["subscription_plan"], loc="lower center",
                         bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
            plt.tight_layout(); sp(fig_rs)

        with col_right:
            latest = tidy["month"].max()
            users_mix = (
                tidy[tidy["month"] == latest]
                .groupby("subscription_plan")["userid"].nunique()
                .reset_index(name="users").sort_values("users", ascending=False)
            )
            fig_um, ax_um = plt.subplots(figsize=(5, 3.6))
            colors = ["#1DB954" if "Premium" in x else "#BFBFBF" for x in users_mix["subscription_plan"]]
            ax_um.bar(users_mix["subscription_plan"], users_mix["users"], color=colors)
            ax_um.set_ylabel("Users (Unique)"); ax_um.set_title(f"Active Users by Plan — {latest}")
            ax_um.set_ylim(0, max(users_mix["users"]) * 1.15)
            for i, v in enumerate(users_mix["users"]): ax_um.text(i, v, f"{int(v):,}", ha="center", va="bottom", fontsize=10)
            plt.tight_layout(); sp(fig_um)

        # Data Quality
        st.markdown("#### 🧹 Data Quality Check  \n<span style='font-size:0.9rem;color:#888;'>데이터 정합성 및 결측치 현황</span>", unsafe_allow_html=True)
        st.markdown("""
        <div class="cup-card">
          - 병합 기준: <b>userid</b> (매출 ⟷ 원본 설문)<br>
          - 기간/규모: <b>2023-01 ~ 2023-06</b>, <b>3,120행</b> (6개월 × 520명)<br>
          - 매출 기준: <b>Premium만 유료매출</b> (Free=0원)
        </div>
        """, unsafe_allow_html=True)

        na = tidy.isna().sum().sort_values(ascending=False)
        na_top = na[na > 0].head(5).reset_index(); na_top.columns = ["column", "na_cnt"]
        fig_na, ax_na = plt.subplots(figsize=(10, 3.6))
        if len(na_top) > 0:
            ax_na.barh(na_top["column"], na_top["na_cnt"], color="#BFBFBF"); ax_na.invert_yaxis()
            ax_na.set_xlabel("Missing Values"); ax_na.set_title("Top Missing Columns", pad=6)
            ax_na.set_xlim(0, max(na_top["na_cnt"]) * 1.15)
            for i, v in enumerate(na_top["na_cnt"]): ax_na.text(v, i, f" {int(v):,}", va="center")
        else:
            ax_na.axis("off"); ax_na.text(0.5, 0.5, "결측치 없음", ha="center", va="center")
        plt.tight_layout(); sp(fig_na)

        st.markdown(f"""
        <div class="cup-card">
          ✅ <b>정합성 요약</b><br>
          - 중복 행: <b>0</b> · 조인 누락: <b>없음</b> (both = 3120)<br>
          - 사용자 수: <b>{tidy['userid'].nunique():,}</b>명 · 기간: <b>{tidy['month'].min()} ~ {tidy['month'].max()}</b><br>
          - 분석 가능 상태: <b>양호</b>
        </div>
        """, unsafe_allow_html=True)
        st.success("✅ 데이터 병합 및 품질 검증 완료 — 분석에 활용 가능합니다.")

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
        counts = [df.query("event==@s").shape[0] for s in steps]
        conv = [100] + [round(counts[i]/counts[i-1]*100,1) if counts[i-1] else 0 for i in range(1,len(steps))]
        fig, ax = plt.subplots(figsize=(6,3)); ax.plot(steps, conv, marker="o", color="#1DB954")
        ax.set_ylim(0,105); ax.set_ylabel("Conversion %", color="#CFE3D8"); ax.set_facecolor("#191414"); fig.set_facecolor("#121212")
        ax.tick_params(colors="#CFE3D8"); sp(fig)
    with tabs[1]:
        st.subheader("Retention Analysis"); st.caption("N-Day/Weekly 커브 예시 (실데이터로 교체 권장).")
        daily = df.groupby("date")["event"].count().sort_index()
        roll = (daily.rolling(7).mean() / (daily.rolling(7).max()+1e-9) * 100).fillna(0)
        fig, ax = plt.subplots(figsize=(6,3)); ax.plot(roll.index, roll.values, color="#80DEEA")
        ax.set_ylabel("Retention-like %", color="#CFE3D8"); ax.set_xlabel("date", color="#CFE3D8")
        ax.set_facecolor("#191414"); fig.set_facecolor("#121212"); ax.tick_params(colors="#CFE3D8"); sp(fig)
    with tabs[2]:
        st.subheader("Cohort Analysis"); st.info("가입월 × 경과주 코호트 유지율 히트맵(추가 예정).")
    with tabs[3]:
        st.subheader("LTV Analysis")
        last30 = df[df["date"] >= (df["date"].max() - pd.Timedelta(days=30))]
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
