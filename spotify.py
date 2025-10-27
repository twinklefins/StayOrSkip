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
    """ /data/name 우선, 루트/name 보조 """
    for p in (os.path.join("data", name), name):
        if os.path.exists(p):
            return pd.read_csv(p)
    return None

def render():
    st.title("💰 Revenue")
    st.caption("CSV(export) 기반 KPI / 트렌드 / 취향별 LTV / 중요 요인")

    # 1) 데이터 로드
    kpi  = _load_csv("out_revenue_kpis.csv")
    retm = _load_csv("out_premium_retention_monthly.csv")
    arpu = _load_csv("out_arpu_monthly.csv")
    pref = _load_csv("out_pref_group_summary.csv")
    sig  = _load_csv("out_pref_significance_tests.csv")
    imp  = _load_csv("out_feature_importance_ltv.csv")

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

    # 2) KPI
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

    # 3) Retention & ARPU Trend
    st.markdown("### 📈 Retention & ARPU Trend")
    col1, col2 = st.columns(2)

    with col1:
        x = retm["from_to"].tolist()
        y = retm["premium_retention"].tolist()
        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(range(len(x)), y, marker="o", color=SPOTIFY_GREEN, linewidth=2)
        ax.set_xticks(range(len(x))); ax.set_xticklabels(x, rotation=0)
        ax.set_ylim(0,1.05); ax.set_facecolor(PLOT_DARK); fig.set_facecolor(BG_DARK)
        ax.tick_params(colors=TICK_COLOR)
        st.pyplot(fig, use_container_width=True)
        try:
            best_i = int(np.nanargmax(y))
            st.caption(f"• 유지율 최고 구간: **{x[best_i]} = {y[best_i]*100:.1f}%**")
        except Exception:
            st.caption("• 유지율 추세를 보여줍니다.")

    with col2:
        x2 = arpu["month"].tolist()
        y2 = arpu["arpu"].tolist()
        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(range(len(x2)), y2, marker="o", color=ACCENT_CYAN, linewidth=2)
        ax.set_xticks(range(len(x2))); ax.set_xticklabels(x2, rotation=0)
        ax.set_facecolor(PLOT_DARK); fig.set_facecolor(BG_DARK)
        ax.tick_params(colors=TICK_COLOR)
        st.pyplot(fig, use_container_width=True)
        try:
            best_i = int(np.nanargmax(y2))
            st.caption(f"• ARPU 최고 월: **{x2[best_i]} = {y2[best_i]:,.0f}원**")
        except Exception:
            st.caption("• 월별 ARPU 변화를 보여줍니다.")

    # 4) 취향별 평균 LTV
    st.markdown("### 🎧 취향별 평균 LTV")
    def _pick_group(row):
        col = row["variable"]
        return row[col] if col in row.index else None
    view = pref.copy()
    view["group"] = view.apply(_pick_group, axis=1)
    view = view[["variable","group","users","avg_ltv","avg_premium_duration",
                 "avg_monthly_revenue","free_to_premium_rate"]].sort_values("avg_ltv", ascending=False)
    with st.expander("Top 10 보기"):
        st.dataframe(view.head(10), use_container_width=True)
    try:
        top_row = view.iloc[0]
        st.caption(f"• LTV 최고 세그먼트: **{top_row['variable']} = {top_row['group']}**, 평균 LTV **{top_row['avg_ltv']:,.0f}원**")
    except Exception:
        st.caption("• 취향별 평균 LTV 상위 그룹을 보여줍니다.")

    # 5) 유의 변수
    st.markdown("### 🔍 통계적으로 유의한 요인 (p<0.05)")
    sig_view = sig.query("p_value < 0.05").sort_values("p_value")
    st.dataframe(sig_view.head(10), use_container_width=True)
    try:
        srow = sig_view.iloc[0]
        st.caption(f"• 가장 강한 통계적 차이: **{srow['feature']}** ({srow['test_type']}), p-value={srow['p_value']:.2e}")
    except Exception:
        st.caption("• p<0.05 변수들이 전환/LTV에 유의미한 차이를 보입니다.")

    # 6) Feature Importance
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
    try:
        fr, fv = topk.iloc[0]["feature"], topk.iloc[0]["importance"]
        st.caption(f"• LTV에 가장 큰 영향: **{fr}** (중요도 {fv:.3f})")
    except Exception:
        st.caption("• 랜덤포레스트 기준 상위 영향 요인을 보여줍니다.")

    # 7) 종합 인사이트
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
