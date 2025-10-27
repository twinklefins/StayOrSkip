# =============================
# 🎨 Dark Mode — Global Theme (final)
# =============================
import streamlit as st
st.set_page_config(page_title="Stay or Skip 🎧", page_icon="🎧", layout="wide")

# ---- Common imports ----
import altair as alt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import base64, os, re, textwrap

# ---- Colors (Dark) ----
BG_DARK   = "#121212"; PANEL = "#191414"; TEXT = "#F9FCF9"; MUTED = "#CFE3D8"
GREEN     = "#1DB954"; MINT = "#7CE0B8"; CYAN = "#80DEEA"; GRID_CLR = "#FFFFFF"; GRID_ALPHA = 0.07

# ---- CSS ----
st.markdown(f"""
<style>
:root {{ --bg:{BG_DARK}; --panel:{PANEL}; --text:{TEXT}; --muted:{MUTED}; --brand:{GREEN}; }}
html, body, .stApp,[data-testid="stAppViewContainer"], [data-testid="stMain"]{{ background:{BG_DARK}; color:{TEXT}; }}
section[data-testid="stSidebar"]{{ background:{PANEL}; color:{TEXT}; }}
.cu-h2{{ display:flex; align-items:center; gap:.6rem; font-weight:800; font-size:1.25rem; margin:0 0 .8rem 0; }}
.cu-h2::before{{ content:""; width:4px; height:20px; background:{GREEN}; border-radius:2px; }}
div[data-testid="stMetric"] div[data-testid="stMetricLabel"] p{{ color:#EAF7EF; font-weight:700; }}
div[data-testid="stMetric"] div[data-testid="stMetricValue"]{{ color:{GREEN}; font-weight:800; }}
.stTabs [data-baseweb="tab"][aria-selected="true"]{{ border-bottom:2px solid {GREEN}; }}
</style>
""", unsafe_allow_html=True)

# ---- Matplotlib / Altair ----
try:
    plt.rcParams["font.family"] = ["Apple SD Gothic Neo","Malgun Gothic","Noto Sans CJK KR","NanumGothic","DejaVu Sans"]
except Exception:
    pass
plt.rcParams.update({
    "figure.facecolor": BG_DARK, "axes.facecolor": PANEL, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": MUTED, "grid.color": GRID_CLR,
    "grid.alpha": GRID_ALPHA, "axes.grid": True, "axes.unicode_minus": False,
})

def _alt_dark():
    return {"config":{
        "background": BG_DARK, "view":{"stroke":"transparent"},
        "axis":{"labelColor":MUTED,"titleColor":MUTED,"gridColor":GRID_CLR,"gridOpacity":GRID_ALPHA,"tickColor":MUTED},
        "legend":{"labelColor":MUTED,"titleColor":MUTED},
        "range":{"category":[GREEN,MINT,CYAN,"#A7FFEB","#B39DDB"]},
}}
try: alt.themes.register("cup_dark", _alt_dark)
except Exception: pass
alt.themes.enable("cup_dark")

# ---------- Paths / helpers ----------
BASE = Path(__file__).parent
RAW_BASE = "https://raw.githubusercontent.com/twinklefins/modu_project/main/StayOrSkip"

def vgap(px:int): st.markdown(f"<div style='height:{px}px;'></div>", unsafe_allow_html=True)
def tight_top(px:int): st.markdown(f"<div style='margin-top:{px}px;'></div>", unsafe_allow_html=True)
def section_title(text, caption="", top_gap=18, bottom_gap=8):
    vgap(top_gap); st.markdown(f"<div class='cu-h2'>{text}</div>", unsafe_allow_html=True)
    if caption: st.caption(caption); vgap(bottom_gap)

def img_to_datauri(filename:str)->str:
    for p in (BASE/filename, BASE/"assets"/filename, BASE/"StayOrSkip"/filename):
        try:
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            return f"data:image/png;base64,{b64}"
        except Exception: pass
    # fallback raw
    try:
        import urllib.request
        with urllib.request.urlopen(f"{RAW_BASE}/{filename}", timeout=6) as r:
            b64 = base64.b64encode(r.read()).decode("ascii")
        return f"data:image/png;base64,{b64}"
    except Exception:
        return "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="

# ---------- Load main dataset ----------
@st.cache_data(show_spinner=False)
def load_data():
    xlsx = BASE/"spotify_merged.xlsx"
    if xlsx.exists():
        df = pd.read_excel(xlsx); src="xlsx"
    else:
        for p in (BASE/"spotify_merged.csv", BASE/"data"/"raw"/"spotify_merged.csv"):
            if p.exists(): df = pd.read_csv(p); src="csv"; break
        else: raise FileNotFoundError
    if "revenue" in df.columns and "revenue_num" not in df.columns:
        df["revenue_num"] = (
            df["revenue"].astype(str).str.replace(r"[^0-9.\-]","",regex=True).replace("", np.nan).astype(float)
        )
    if "month" in df.columns: df["month"] = df["month"].astype(str)
    return df, src

try:
    tidy, _ = load_data()
except FileNotFoundError:
    st.error("데이터가 없습니다. `spotify_merged.xlsx` 또는 `spotify_merged.csv`를 업로드하세요.")
    st.stop()

# ================= Sidebar =================
with st.sidebar:
    st.caption("build: v2025-10-24-spotify-compat-CSV")
    logo = img_to_datauri("Cup_3_copy_4.png")
    st.markdown(f'<img src="{logo}" style="width:65%;height:auto;margin:.2rem 0 1rem 0;" />', unsafe_allow_html=True)
    st.markdown('<hr style="opacity:.15">', unsafe_allow_html=True)
    section = st.radio("", ["PROJECT OVERVIEW","DATA EXPLORATION","RARR DASHBOARD","INSIGHTS & STRATEGY"])
    st.markdown('<hr style="opacity:.15">', unsafe_allow_html=True)
    st.markdown('[🔗 Open in Google Colab](https://colab.research.google.com/drive/1kmdOCUneO2tjT8NqOd5MvYaxJqiiqb9y?usp=sharing)')

# ================= Title =================
icon = img_to_datauri("StayOrSkip/free-icon-play-4604241.png")
st.markdown(f"""
<style>
.cup-hero{{display:inline-flex;align-items:baseline;gap:0;margin:-4.5rem 0 .25rem 0;transform:translateY(-8px);}}
.cup-hero h1{{margin:0;line-height:1;font-weight:800;letter-spacing:-.2px;}}
.cup-hero img{{width:3.05em;transform:translateY(.65em);margin-left:-6px;}}
.cup-subtitle{{color:rgba(255,255,255,.7);font-size:1.08rem;margin-top:-1.4rem;margin-bottom:1rem;}}
</style>
<div class="cup-hero"><h1>Stay or Skip</h1><img src="{icon}" /></div>
<p class="cup-subtitle">Streaming Subscription Analysis with RARRA Framework</p>
""", unsafe_allow_html=True)
vgap(24)

# ================= Sections =================
if section == "PROJECT OVERVIEW":
    tabs = st.tabs(["Team Intro", "About Spotify", "Background & Objectives", "Dataset"])

    # ---- Team Intro
    with tabs[0]:
        section_title("Team Introduction"); tight_top(-36)
        mark = img_to_datauri("Cup_8_copy_2.png")
        st.markdown(f'<img src="{mark}" style="width:35%;max-width:520px;margin:-1.2rem 0 2.2rem 0;" />', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.10);border-radius:12px;padding:1.6rem;">
          <p style="font-weight:600;">빠르지만 든든한 데이터 분석, 인사이트 한 스푼으로 완성하는 데이터컵밥 🍚</p>
          <p>데이터 탐색(EDA) · 핵심 지표 선정 · 시각화 · 인사이트 도출</p>
        </div>
        """, unsafe_allow_html=True)

    # ---- About Spotify
    with tabs[1]:
        section_title("About Spotify"); tight_top(-36)
        c1,c2,c3 = st.columns(3)
        c1.metric("Monthly Active Users","696M"); c2.metric("Premium Subscribers","276M"); c3.metric("Markets","180+")
        st.markdown("""
        <div style="margin-top:.8rem;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.10);
                    border-radius:12px;padding:1.2rem;">
          Freemium(광고) + Premium(구독) 모델. 개인화 추천이 강점.
        </div>
        """, unsafe_allow_html=True)

    # ---- Background & Objectives
    with tabs[2]:
        section_title("Background & Objectives"); tight_top(-36)
        colA,colB,colC = st.columns(3)
        with colA: st.info("📈 시장 성장과 도전: 유입↑ 이탈↑. 전환·유지 핵심.")
        with colB: st.info("🎧 강점: 대규모 청취 로그·오디오 피처 → 행동 분석 최적.")
        with colC: st.info("🧭 방향: RARRA(유지→활성→수익→획득)로 전략 설계.")

    # ---- Dataset
    with tabs[3]:
        section_title("Dataset Overview")
        n_rows, n_cols = tidy.shape
        month_min = tidy["month"].min() if "month" in tidy.columns else "—"
        month_max = tidy["month"].max() if "month" in tidy.columns else "—"
        st.markdown(f"""
        <div style="border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:1rem 1.2rem;">
          <b>규모</b>: {n_rows:,}행 · {n_cols}컬럼<br>
          <b>주요 컬럼</b>: userid, month, subscription_plan, revenue_num
        </div>
        """, unsafe_allow_html=True)

        section_title("Full Column List", "병합 데이터 전체 컬럼 요약", top_gap=12, bottom_gap=6)
        cols_desc = [
            ("userid","사용자 ID"),("month","관측 월"),("revenue","월 매출(문자)"),("revenue_num","월 매출(숫자)"),
            ("subscription_plan","요금제(Free/Premium)"),("timestamp","설문 시각"),
            ("Age","연령대"),("Gender","성별"),("spotify_listening_device","주 청취 기기"),
            ("music_time_slot","주 청취 시간대"),("fav_music_genre","선호 장르"),
        ]
        st.dataframe(pd.DataFrame(cols_desc,columns=["컬럼명","설명"]), hide_index=True, use_container_width=True)

        section_title("Dataset Preview","상위 5행")
        st.dataframe(tidy.head(5), use_container_width=True)

        # Quick charts
        section_title("Monthly Revenue Trend","월별 총매출 추이(₩)")
        rev_col = "revenue_num" if "revenue_num" in tidy.columns else "revenue"
        df_rev = tidy[["month", rev_col]].copy()
        if rev_col=="revenue":
            df_rev[rev_col] = df_rev[rev_col].astype(str).str.replace(r"[^0-9.\-]","",regex=True).replace("",np.nan).astype(float)
        df_rev["month_dt"] = pd.to_datetime(df_rev["month"]+"-01", errors="coerce")
        monthly = df_rev.groupby("month_dt",as_index=False)[rev_col].sum()
        ch = (alt.Chart(monthly).mark_line(point=True,color=GREEN)
              .encode(x=alt.X("month_dt:T",axis=alt.Axis(labelAngle=0,title="Month")),
                      y=alt.Y(f"{rev_col}:Q",axis=alt.Axis(title="Revenue (₩)")),
                      tooltip=[alt.Tooltip("month_dt:T","Month"),alt.Tooltip(f"{rev_col}:Q","Revenue",format=",.0f")])
              .properties(height=300))
        st.altair_chart(ch, use_container_width=True)

elif section == "DATA EXPLORATION":
    tabs = st.tabs(["Cleaning","EDA","Framework Comparison"])

    # Cleaning
    with tabs[0]:
        section_title("Data Cleaning & Preprocessing"); tight_top(-36)
        st.markdown("""
        <div class="cup-card">
          - 문자 매출 → 숫자 변환, 음수/이상치 제거<br>
          - 카테고리 변수 정리, 월/타임스탬프 파싱
        </div>
        """, unsafe_allow_html=True)
        na = tidy.isna().sum().sort_values(ascending=False)
        na_top = (na/len(tidy)*100).head(10).reset_index()
        na_top.columns=["column","missing(%)"]
        st.altair_chart(
            alt.Chart(na_top).mark_bar(color=GREEN).encode(
                x=alt.X("missing(%):Q",title="Missing %"),
                y=alt.Y("column:N",sort="-x",title=None),
                tooltip=["column","missing(%)"]
            ).properties(height=260),
            use_container_width=True
        )

    # EDA
    with tabs[1]:
        section_title("Exploratory Data Analysis (EDA)"); tight_top(-36)
        plan_col = next((c for c in ["subscription_plan","spotify_subscription_plan"] if c in tidy.columns), None)

        section_title("User Distribution by Subscription Plan","Free vs Premium")
        if plan_col:
            plan_count = tidy[plan_col].value_counts().reset_index()
            plan_count.columns=["plan","users"]
            st.altair_chart(
                alt.Chart(plan_count).mark_arc(innerRadius=60).encode(
                    theta=alt.Theta("users:Q"), color=alt.Color("plan:N",scale=alt.Scale(scheme="greens"),legend=None),
                    tooltip=["plan","users"]
                ).properties(height=260),
                use_container_width=True
            )
        else: st.info("요금제 컬럼을 찾지 못했습니다.")

        section_title("Listening Device Preference","상위 5개")
        if "spotify_listening_device" in tidy.columns:
            dev = tidy["spotify_listening_device"].value_counts().head(5).reset_index()
            dev.columns=["device","count"]
            st.altair_chart(
                alt.Chart(dev).mark_bar(color=GREEN).encode(
                    x="count:Q", y=alt.Y("device:N",sort="-x",title=None), tooltip=["device","count"]
                ).properties(height=240),
                use_container_width=True
            )
        else: st.info("청취 기기 컬럼이 없습니다.")

        section_title("Listening Time Slot Distribution","시간대별")
        if "music_time_slot" in tidy.columns:
            order=["Morning","Afternoon","Evening","Night"]
            cnt = tidy["music_time_slot"].value_counts().rename_axis("slot").reset_index(name="users")
            cnt["slot"]=pd.Categorical(cnt["slot"],categories=order,ordered=True); cnt=cnt.dropna().sort_values("slot")
            st.altair_chart(
                alt.Chart(cnt).mark_line(point=alt.OverlayMarkDef(size=70,filled=True,fill=GREEN),
                                         stroke=GREEN, strokeWidth=3).encode(
                    x=alt.X("slot:N",sort=order,axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("users:Q",title="Users"), tooltip=["slot","users"]
                ).properties(height=260),
                use_container_width=True
            )
        else: st.info("청취 시간대 컬럼이 없습니다.")

        # Insight
        section_title("EDA Summary Insight", top_gap=8, bottom_gap=4)
        ins=[]
        if plan_col:
            prem_ratio = tidy[plan_col].astype(str).str.contains("Premium",case=False,na=False).mean()
            ins.append(f"Premium 비중 {prem_ratio*100:.1f}%.")
        if "spotify_listening_device" in tidy.columns:
            top_dev = tidy["spotify_listening_device"].dropna().astype(str).value_counts().idxmax()
            ins.append(f"가장 많이 쓰는 기기는 {top_dev}.")
        if "music_time_slot" in tidy.columns and tidy["music_time_slot"].notna().any():
            top_slot = tidy["music_time_slot"].dropna().astype(str).value_counts().idxmax()
            ins.append(f"{top_slot} 시간대 청취가 가장 활발.")
        st.markdown("<div class='cup-card'>• " + "<br>• ".join(ins) + "</div>", unsafe_allow_html=True)

    # Framework Comparison
    with tabs[2]:
        section_title("Framework Comparison"); tight_top(-36)
        st.markdown("### ⚙️ Growth Framework: AARRR vs RARRA")
        comp = pd.DataFrame({
            "구분":["핵심 목표","접근 방식","적합한 비즈니스","장점","단점"],
            "AARRR":[
                "신규 고객 확보 및 초기 시장 진출",
                "획득 중심 선형 퍼널",
                "초기 스타트업 등 빠른 유입 필요",
                "병목 구간 파악·개선이 용이",
                "획득에 치우치면 낮은 유지율로 성장 정체"
            ],
            "RARRA":[
                "고객 충성/장기 가치 증대",
                "유지 중심 순환 성장 고리",
                "SaaS·구독형/성숙시장",
                "유지에 집중해 안정적 성장",
                "초기엔 고객 풀이 적으면 한계"
            ],
        })
        st.dataframe(comp, use_container_width=True, hide_index=True)
        st.caption("※ 본 프로젝트는 ‘Retention-first’ 관점의 RARRA 프레임워크를 채택했습니다.")

elif section == "RARR DASHBOARD":
    st.markdown('<div class="cu-h2">Visual Analytics Dashboard</div>', unsafe_allow_html=True)
    try: tight_top(-36)
    except: pass

    # 🔄 RARRA 탭 (R → A → Revenue → Acquisition)
    tabs = st.tabs(["Retention","Activation","Revenue","Acquisition"])

    with tabs[0]:
        st.subheader("Retention")
        st.caption("N-Day/Weekly 커브(예시)")

    with tabs[1]:
        st.subheader("Activation")
        st.caption("가입 직후 첫 재생까지의 활성화 지표(예시)")

    with tabs[2]:
        # --- CSV loader for revenue parts
        def _load_csv(name:str):
            for p in (os.path.join("data", name), name):
                if os.path.exists(p): return pd.read_csv(p)
            return None

        kpi  = _load_csv("out_revenue_kpis.csv")
        retm = _load_csv("out_premium_retention_monthly.csv")
        arpu = _load_csv("out_arpu_monthly.csv")
        pref = _load_csv("out_pref_group_summary.csv")
        sig  = _load_csv("out_pref_significance_tests.csv")
        imp  = _load_csv("out_feature_importance_ltv.csv")

        missing = [n for n,d in {
            "out_revenue_kpis.csv":kpi, "out_premium_retention_monthly.csv":retm,
            "out_arpu_monthly.csv":arpu, "out_pref_group_summary.csv":pref,
            "out_pref_significance_tests.csv":sig, "out_feature_importance_ltv.csv":imp
        }.items() if d is None]
        if missing:
            st.warning("다음 파일이 없어 Revenue를 표시할 수 없어요:\n- " + "\n- ".join(missing))
            st.info("노트북 Step6에서 /data 폴더로 export 후 다시 실행해주세요.")
            st.stop()

        # KPI
        conv   = float(kpi.loc[kpi.metric=="conversion_rate","value"])
        rmean  = float(kpi.loc[kpi.metric=="premium_retention_mean","value"])
        arpu_v = float(kpi.loc[kpi.metric=="arpu_overall","value"])
        dur    = float(kpi.loc[kpi.metric=="avg_premium_duration","value"])

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("전환율", f"{conv*100:.1f}%")
        c2.metric("유지율(평균)", f"{rmean*100:.1f}%")
        c3.metric("ARPU(원)", f"{arpu_v:,.0f}")
        c4.metric("평균 Premium 기간", f"{dur:.2f}개월")

        with st.expander("KPI 계산식(분자/분모)"):
            st.markdown(
                "- **전환율** = Premium 전환 수 / 최초 Free 수\n"
                "- **유지율(A→B)** = A·B 모두 Premium / A의 Premium\n"
                "- **ARPU** = revenue 총합 / 전체 유저-월 수\n"
                "- **평균 Premium 기간** = 사용자별 Premium 개월수 평균\n"
                "- **LTV(유저)** = 사용자별 revenue 합(세그먼트 평균)"
            )

        # Trends (green line+dots)
        st.markdown("### 📈 Retention & ARPU Trend")
        col1,col2 = st.columns(2)

        def _short(s:str)->str:
            return f"{s.split('→')[0][-2:]}→{s.split('→')[-1][-2:]}" if "→" in s else s

        with col1:
            x = [_short(s) for s in retm["from_to"].astype(str).tolist()]
            y = pd.to_numeric(retm["premium_retention"], errors="coerce").tolist()
            fig, ax = plt.subplots(figsize=(6.2,3.2))
            ax.plot(range(len(x)), y, marker="o", markersize=6, linewidth=2.2, color=GREEN)
            ax.set_xticks(range(len(x))); ax.set_xticklabels(x)
            ax.set_ylim(0,1.05); ax.set_ylabel("Premium Retention"); ax.grid(True, axis="y", alpha=.25)
            st.pyplot(fig, use_container_width=True)
            try:
                i=int(np.nanargmax(y)); st.caption(f"• 최고 구간: **{x[i]} = {y[i]*100:.1f}%**")
            except: pass

        with col2:
            xm = arpu["month"].astype(str).tolist()
            ym = pd.to_numeric(arpu["arpu"], errors="coerce").tolist()
            fig, ax = plt.subplots(figsize=(6.2,3.2))
            ax.plot(range(len(xm)), ym, marker="o", markersize=6, linewidth=2.2, color=GREEN)
            ax.set_xticks(range(len(xm))); ax.set_xticklabels(xm)
            ax.set_ylabel("ARPU (₩)"); ax.grid(True, axis="y", alpha=.25)
            st.pyplot(fig, use_container_width=True)
            try:
                i=int(np.nanargmax(ym)); st.caption(f"• ARPU 최고 월: **{xm[i]} = {ym[i]:,.0f}원**")
            except: pass

        # Top10 LTV segments
        st.markdown("### 🎧 세그먼트별 평균 LTV (Top 10)")
        def _pick_group(row): return row.get(row["variable"], None)
        view = pref.copy(); view["group"] = view.apply(_pick_group, axis=1)
        view = (view[["variable","group","avg_ltv","users","avg_premium_duration","avg_monthly_revenue","free_to_premium_rate"]]
                .dropna(subset=["avg_ltv"]).sort_values("avg_ltv", ascending=False).head(10).reset_index(drop=True))
        view["row_lab"] = (view["variable"]+" = "+view["group"].astype(str)).map(lambda s: "<br>".join(textwrap.wrap(re.sub(r"[_\-]+"," ", s),36)))
        st.altair_chart(
            alt.Chart(view).mark_bar(color=GREEN).encode(
                x=alt.X("avg_ltv:Q", title="평균 LTV (₩)", axis=alt.Axis(format="~s")),
                y=alt.Y("row_lab:N", sort="-x", title=None, axis=alt.Axis(labelLimit=900)),
                tooltip=[alt.Tooltip("row_lab:N","세그먼트"),alt.Tooltip("avg_ltv:Q","평균 LTV",format=",.0f"),
                         alt.Tooltip("users:Q","Users")]
            ).properties(height=560),
            use_container_width=True
        )
        if len(view)>0:
            st.caption(f"• 상위 세그먼트: **{view.iloc[0]['variable']} = {view.iloc[0]['group']}**, 평균 LTV **{view.iloc[0]['avg_ltv']:,.0f}원**")

        # Significance
        st.markdown("### 🔍 통계적으로 유의한 요인 (p<0.05)")
        sig_view = sig.query("p_value < 0.05").sort_values("p_value")
        st.dataframe(sig_view.head(10), use_container_width=True)
        if len(sig_view)>0:
            r0=sig_view.iloc[0]; st.caption(f"• 최상위 요인: **{r0['feature']}** ({r0['test_type']}) — p={r0['p_value']:.2e}")

        # Feature importance
        st.markdown("### 🌲 LTV 영향 요인 (Feature Importance)")
        imp2 = imp.rename(columns={imp.columns[0]:"feature", imp.columns[1]:"importance"}) if imp.shape[1]>=2 else imp.copy()
        imp2 = imp2[["feature","importance"]].dropna()
        topk = imp2.sort_values("importance", ascending=False).head(10)
        st.altair_chart(
            alt.Chart(topk).mark_bar(color=GREEN).encode(
                x=alt.X("importance:Q", title="Importance"),
                y=alt.Y("feature:N", sort="-x", title=None, axis=alt.Axis(labelLimit=900)),
                tooltip=[alt.Tooltip("feature:N","Feature"),alt.Tooltip("importance:Q","Importance",format=".3f")]
            ).properties(height=380),
            use_container_width=True
        )
        if not topk.empty:
            st.caption(f"• 가장 큰 영향 요인: **{topk.iloc[0]['feature']}** (중요도 {topk.iloc[0]['importance']:.3f})")

        st.markdown("---")
        # Extra charts (selector)
        st.markdown("### 📊 다양한 분석")
        chart_h = 520
        extra = st.selectbox("", ["ARPU 누적 곡선(기간별)","유지율 vs ARPU 산점도","Premium 기간 분포(히스토그램)","월별 매출 합계(막대)","유지율 코호트 히트맵(간이)"], label_visibility="collapsed")
        def to_num(s): return pd.to_numeric(s, errors="coerce")
        def ensure_cols(df, num_cols=(), str_cols=()):
            df=df.copy()
            for c in num_cols: df[c]=to_num(df[c])
            for c in str_cols: df[c]=df[c].astype(str)
            return df

        if extra=="ARPU 누적 곡선(기간별)":
            df=arpu.copy(); df["cum_arpu"]=to_num(df["arpu"]).cumsum()
            st.altair_chart(
                alt.Chart(df).mark_line(point=alt.OverlayMarkDef(size=70,filled=True,fill=GREEN),
                                        color=GREEN, strokeWidth=3).encode(
                    x=alt.X("month:N",axis=alt.Axis(labelAngle=0)), y=alt.Y("cum_arpu:Q",title="누적 ARPU (₩)",axis=alt.Axis(format="~s")),
                    tooltip=[alt.Tooltip("month:N","월"),alt.Tooltip("cum_arpu:Q","누적 ARPU",format=",.0f")]
                ).properties(height=chart_h), use_container_width=True)
        elif extra=="유지율 vs ARPU 산점도":
            rr=retm.copy(); rr["month"]=rr["from_to"].astype(str).str.split("→").str[-1].str.strip()
            df=pd.merge(arpu, rr[["month","premium_retention"]], on="month", how="inner")
            df=ensure_cols(df, num_cols=["arpu","premium_retention"]).dropna()
            st.altair_chart(
                alt.Chart(df).mark_circle(size=140,color=GREEN).encode(
                    x=alt.X("premium_retention:Q",title="유지율",scale=alt.Scale(domain=[0,1])),
                    y=alt.Y("arpu:Q",title="ARPU (₩)",axis=alt.Axis(format="~s")),
                    tooltip=[alt.Tooltip("month:N","월"),alt.Tooltip("premium_retention:Q","유지율",format=".1%"),alt.Tooltip("arpu:Q","ARPU",format=",.0f")]
                ).properties(height=chart_h), use_container_width=True)
        elif extra=="Premium 기간 분포(히스토그램)":
            if "premium_duration" in tidy.columns:
                samples=ensure_cols(tidy[["premium_duration"]], num_cols=["premium_duration"]).dropna().rename(columns={"premium_duration":"months"})
            else:
                samples=pd.DataFrame({"months":np.clip(np.random.normal(dur,1.0,400),0,None)})
            st.altair_chart(
                alt.Chart(samples).mark_bar(color=GREEN).encode(
                    x=alt.X("months:Q",bin=alt.Bin(maxbins=18),title="Premium 이용 개월 수"),
                    y=alt.Y("count():Q",title="사용자 수"), tooltip=[alt.Tooltip("count():Q","사용자 수")]
                ).properties(height=chart_h), use_container_width=True)
        elif extra=="월별 매출 합계(막대)":
            rev_col = "revenue_num" if "revenue_num" in tidy.columns else "revenue"
            df_rev = tidy[["month",rev_col]].copy()
            if rev_col=="revenue": df_rev[rev_col]=df_rev[rev_col].astype(str).str.replace(r"[^0-9.\-]","",regex=True)
            df_rev=ensure_cols(df_rev,num_cols=[rev_col],str_cols=["month"]).dropna(subset=[rev_col,"month"])
            monthly=df_rev.groupby("month",as_index=False)[rev_col].sum().sort_values("month")
            st.altair_chart(
                alt.Chart(monthly).mark_bar(color=GREEN).encode(
                    x=alt.X("month:N",axis=alt.Axis(labelAngle=0)), y=alt.Y(f"{rev_col}:Q",title="월별 매출 합계 (₩)",axis=alt.Axis(format="~s")),
                    tooltip=[alt.Tooltip("month:N","월"),alt.Tooltip(f"{rev_col}:Q","매출",format=",.0f")]
                ).properties(height=chart_h), use_container_width=True)
        elif extra=="유지율 코호트 히트맵(간이)":
            rr=retm.copy(); rr[["m0","m1"]]=rr["from_to"].astype(str).str.split("→",expand=True)
            rr["m0"]=rr["m0"].str[-2:]; rr["m1"]=rr["m1"].str[-2:]
            rr["premium_retention"]=pd.to_numeric(rr["premium_retention"], errors="coerce"); rr=rr.dropna(subset=["premium_retention"])
            st.altair_chart(
                alt.Chart(rr).mark_rect().encode(
                    x=alt.X("m1:N",title="대상 월",axis=alt.Axis(labelAngle=0)), y=alt.Y("m0:N",title="기준 월"),
                    color=alt.Color("premium_retention:Q",title="유지율",scale=alt.Scale(scheme="greens")),
                    tooltip=[alt.Tooltip("from_to:N","구간"),alt.Tooltip("premium_retention:Q","유지율",format=".1%")]
                ).properties(height=chart_h), use_container_width=True)

        st.markdown("---")
        st.success(
            "### 📦 종합 인사이트\n"
            f"- 전환율 **{conv*100:.1f}%**, 평균 유지율 **{rmean*100:.1f}%**, ARPU **{arpu_v:,.0f}원**, 평균 Premium 기간 **{dur:.2f}개월**\n"
            "- **유지율은 초반이 가장 높음** → 초반 체류 강화\n"
            "- **ARPU 꾸준 개선** → 상위 세그먼트 공략 유지"
        )

    with tabs[3]:
        st.subheader("Acquisition")
        st.caption("방문 → 가입 → 첫 재생 → 구독 전환율(예시)")

else:
    tabs = st.tabs(["Insights","Strategy","Next Steps"])
    with tabs[0]:
        st.markdown('<div class="cu-h2">Key Insights by AARRR Stage</div>', unsafe_allow_html=True); tight_top(-36)
        st.markdown("""
        <div class="cup-card">
          • Activation: 첫 재생 이탈 높음 → 온보딩·첫 추천 강화<br>
          • Retention: 7일 복귀율 급락 → 리마인드/추천 자동화<br>
          • Revenue: 상위 사용자 매출 편중 → VIP 업셀·연간 구독
        </div>
        """, unsafe_allow_html=True)
    with tabs[1]:
        st.markdown('<div class="cu-h2">Data-driven Strategy Proposal</div>', unsafe_allow_html=True); tight_top(-36)
        st.markdown("""
        <div class="cup-card">
          ① 온보딩 개선 ② 휴면징후 타깃 알림 ③ VIP 리워드/장기 구독 ④ 추천·공유 인센티브
        </div>
        """, unsafe_allow_html=True)
    with tabs[2]:
        st.markdown('<div class="cu-h2">Limitations & Next Steps</div>', unsafe_allow_html=True); tight_top(-36)
        st.markdown("""
        <div class="cup-card">
          관찰 기간·외생 변수 제한 → 외부 데이터 결합 및 예측모델(이탈 예측·LTV) 확장
        </div>
        """, unsafe_allow_html=True)