import os, numpy as np, pandas as pd
import streamlit as st, matplotlib.pyplot as plt

SPOTIFY_GREEN="#1DB954"; ACCENT_CYAN="#80DEEA"
BG_DARK="#121212"; PLOT_DARK="#191414"; TICK_COLOR="#CFE3D8"

def _load_csv(name):
    for p in (os.path.join("data", name), name):
        if os.path.exists(p): return pd.read_csv(p)
    return None

def _dark_ax(figsize=(6,3)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.set_facecolor(BG_DARK); ax.set_facecolor(PLOT_DARK)
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

    miss=[n for n,d in {
        "out_revenue_kpis.csv":kpi,"out_premium_retention_monthly.csv":retm,
        "out_arpu_monthly.csv":arpu,"out_pref_group_summary.csv":pref,
        "out_pref_significance_tests.csv":sig,"out_feature_importance_ltv.csv":imp}.items() if d is None]
    if miss:
        st.warning("누락 파일:\n- " + "\n- ".join(miss))
        st.info("노트북 Step6에서 /data로 export 후 Rerun 하세요.")
        return

    # KPI
    conv=float(kpi.loc[kpi.metric=="conversion_rate","value"])
    rmean=float(kpi.loc[kpi.metric=="premium_retention_mean","value"])
    arpu_v=float(kpi.loc[kpi.metric=="arpu_overall","value"])
    dur=float(kpi.loc[kpi.metric=="avg_premium_duration","value"])
    c1,c2,c3,c4=st.columns(4)
    c1.metric("전환율",f"{conv*100:.1f}%"); c2.metric("유지율(평균)",f"{rmean*100:.1f}%")
    c3.metric("ARPU(원)",f"{arpu_v:,.0f}"); c4.metric("평균 Premium 기간",f"{dur:.2f}개월")
    with st.expander("KPI 계산식(분자/분모)"):
        st.markdown("- 전환율 = Premium 전환 수 / 최초 Free 수\n- 유지율(A→B) = A,B 둘다 Premium / A의 Premium 수\n- ARPU = revenue 합 / 전체 유저-월 수\n- 평균 Premium 기간 = 사용자별 Premium 개월 평균\n- LTV(유저) = 사용자별 revenue 합")

    # Retention
    st.subheader("📈 Retention & ARPU Trend")
    cA,cB=st.columns(2)
    with cA:
        x=retm["from_to"].tolist(); y=retm["premium_retention"].tolist()
        fig,ax=_dark_ax(); ax.plot(range(len(x)),y,marker="o",color=SPOTIFY_GREEN,linewidth=2)
        ax.set_xticks(range(len(x))); ax.set_xticklabels(x,rotation=0); ax.set_ylim(0,1.05)
        st.pyplot(fig, use_container_width=True)
        st.caption(f"• 유지율 최고: **{x[int(np.nanargmax(y))]} = {max(y)*100:.1f}%**")
    with cB:
        x2=arpu["month"].tolist(); y2=arpu["arpu"].tolist()
        fig,ax=_dark_ax(); ax.plot(range(len(x2)),y2,marker="o",color=ACCENT_CYAN,linewidth=2)
        ax.set_xticks(range(len(x2))); ax.set_xticklabels(x2,rotation=0)
        st.pyplot(fig, use_container_width=True)
        st.caption(f"• ARPU 최고: **{x2[int(np.nanargmax(y2))]} = {max(y2):,.0f}원**")

    # 취향별 LTV
    st.subheader("🎧 취향별 평균 LTV")
    pick=lambda r: r[r["variable"]] if r["variable"] in r.index else None
    view=pref.copy(); view["group"]=view.apply(pick,axis=1)
    view=view[["variable","group","users","avg_ltv","avg_premium_duration","avg_monthly_revenue","free_to_premium_rate"]].sort_values("avg_ltv",ascending=False)
    with st.expander("Top 10 보기"): st.dataframe(view.head(10), use_container_width=True)
    st.caption(f"• LTV 최고 세그: **{view.iloc[0]['variable']} = {view.iloc[0]['group']}**, LTV **{view.iloc[0]['avg_ltv']:,.0f}원**")

    # 유의 변수
    st.subheader("🔍 통계적으로 유의한 요인 (p<0.05)")
    sigv=sig.query("p_value < 0.05").sort_values("p_value")
    st.dataframe(sigv.head(10), use_container_width=True)
    st.caption(f"• 최상위: **{sigv.iloc[0]['feature']}** ({sigv.iloc[0]['test_type']}), p={sigv.iloc[0]['p_value']:.2e}")

    # Feature Importance
    st.subheader("🌲 LTV 영향 요인")
    if imp.shape[1]!=2: imp=imp.rename(columns={imp.columns[0]:"feature",imp.columns[1]:"importance"})
    else: imp.columns=["feature","importance"]
    topk=imp.sort_values("importance",ascending=False).head(10)
    fig,ax=_dark_ax((10,3.2)); ax.bar(range(len(topk)),topk["importance"],color=SPOTIFY_GREEN)
    ax.set_xticks(range(len(topk))); ax.set_xticklabels(topk["feature"],rotation=0); ax.set_ylabel("Importance",color=TICK_COLOR)
    st.pyplot(fig, use_container_width=True)
    st.caption(f"• 최상위 영향: **{topk.iloc[0]['feature']}** (중요도 {topk.iloc[0]['importance']:.3f})")

    # 종합 인사이트
    st.markdown("---")
    st.success(
        f"### 📦 종합 인사이트\n"
        f"- 전환율 **{conv*100:.1f}%**, 평균 유지율 **{rmean*100:.1f}%**, ARPU **{arpu_v:,.0f}원**, 평균 Premium 기간 **{dur:.2f}개월**\n"
        f"- 유지율 최고: **{retm.iloc[int(np.nanargmax(retm['premium_retention']))]['from_to']}**, "
        f"ARPU 최고: **{arpu.iloc[int(np.nanargmax(arpu['arpu']))]['month']}**\n"
        f"- LTV 상위 세그: **{view.iloc[0]['variable']} = {view.iloc[0]['group']}**, "
        f"최상위 영향 요인: **{topk.iloc[0]['feature']}**"
    )
