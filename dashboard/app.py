"""Home Credit risk analytics portfolio dashboard.

Reads aggregate validation results; never loads applicant-level records or models.
Run from the project root: streamlit run dashboard/app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Home Credit | Risk Analytics", page_icon="📊", layout="wide")
ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

@st.cache_data(show_spinner=False)
def read_report(filename: str) -> pd.DataFrame | None:
    path = REPORTS / filename
    if not path.is_file():
        return None
    return pd.read_csv(path)


def require_report(filename: str) -> pd.DataFrame | None:
    data = read_report(filename)
    if data is None:
        st.info(f"Missing `reports/{filename}`. Run the corresponding notebook and commit its aggregate CSV output.")
    return data


def pct(v: float) -> str:
    return f"{v:.2%}"


st.title("Home Credit · Risk Analytics")
st.caption("Portfolio research dashboard | Historical repayment-difficulty data | Validation sample only")
st.warning(
    "For exploratory analytics only. Predicted scores and hypothetical review costs are not "
    "validated lending, approval, denial, or financial-loss recommendations.", icon="ℹ️"
)

model_tab, risk_tab, decision_tab, explain_tab = st.tabs(
    ["Model overview", "Risk segmentation", "Review scenarios", "Explainability"]
)

with model_tab:
    st.subheader("Model comparison")
    model_df = require_report("day06_model_comparison.csv")
    if model_df is not None:
        if "Unnamed: 0" in model_df.columns:
            model_df = model_df.rename(columns={"Unnamed: 0": "Model"})
        if "Model" not in model_df.columns:
            st.error("Expected a model-name index or `Model` column in day06_model_comparison.csv")
        else:
            available = [x for x in ["ROC-AUC", "Average Precision", "Brier Score"] if x in model_df.columns]
            if available:
                st.dataframe(model_df[["Model"] + available].set_index("Model").style.format({k: "{:.4f}" for k in available}), use_container_width=True)
                if "ROC-AUC" in available:
                    fig = px.bar(model_df, x="Model", y="ROC-AUC", title="Validation ROC-AUC", text_auto=".4f")
                    fig.update_yaxes(range=[0, max(.8, float(model_df["ROC-AUC"].max()) + .02)])
                    st.plotly_chart(fig, use_container_width=True)
    st.caption("Validation metrics reflect an already-developed model. The final held-out test set is not displayed.")

with risk_tab:
    st.subheader("Risk deciles and cumulative capture")
    deciles = require_report("day09_risk_deciles.csv")
    if deciles is not None:
        needed = {"Risk_Decile", "Observed_Rate", "Mean_Predicted_Risk", "Lift", "Applicants", "Positive_Cases"}
        if not needed.issubset(deciles.columns):
            st.error(f"Decile file is missing columns: {sorted(needed - set(deciles.columns))}")
        else:
            deciles = deciles.sort_values("Risk_Decile")
            n = int(deciles["Applicants"].sum())
            pos = int(deciles["Positive_Cases"].sum())
            high = deciles.iloc[-1]
            a, b, c, d = st.columns(4)
            a.metric("Validation applications", f"{n:,}")
            b.metric("Observed positive rate", pct(pos / n))
            c.metric("Highest-decile rate", pct(float(high["Observed_Rate"])))
            d.metric("Highest-decile lift", f"{high['Lift']:.2f}×")

            chart_df = deciles[["Risk_Decile", "Observed_Rate", "Mean_Predicted_Risk"]].melt(
                "Risk_Decile", var_name="Series", value_name="Rate"
            )
            fig = px.line(chart_df, x="Risk_Decile", y="Rate", color="Series", markers=True,
                          title="Observed versus predicted payment difficulty by decile")
            fig.update_yaxes(tickformat=".0%")
            fig.update_xaxes(dtick=1)
            st.plotly_chart(fig, use_container_width=True)

            gains = deciles.sort_values("Risk_Decile", ascending=False).copy()
            gains["Population share"] = gains["Applicants"].cumsum() / n
            gains["Positive-case capture"] = gains["Positive_Cases"].cumsum() / pos
            gains = pd.concat([pd.DataFrame({"Population share": [0.], "Positive-case capture": [0.]}),
                               gains], ignore_index=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=gains["Population share"], y=gains["Positive-case capture"],
                                     name="LightGBM", mode="lines+markers"))
            fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], name="Random selection", line=dict(dash="dash")))
            fig.update_layout(title="Cumulative capture of positive cases", xaxis_title="Share of applicants reviewed",
                              yaxis_title="Share of positives captured", xaxis_tickformat=".0%", yaxis_tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(deciles, use_container_width=True, hide_index=True)

    st.subheader("Financial segments")
    group_choice = st.selectbox("Segment", ["Income", "Annuity burden", "Bureau availability"])
    report_files = {
        "Income": "day09_income_segments.csv",
        "Annuity burden": "day09_annuity_burden_segments.csv",
        "Bureau availability": "day09_bureau_segments.csv",
    }
    segments = require_report(report_files[group_choice])
    if segments is not None:
        if {"Segment", "Observed_Rate", "Mean_Predicted_Risk"}.issubset(segments.columns):
            compare = segments.melt("Segment", value_vars=["Observed_Rate", "Mean_Predicted_Risk"],
                                    var_name="Series", value_name="Rate")
            fig = px.bar(compare, x="Segment", y="Rate", color="Series", barmode="group",
                         title=f"Observed vs predicted rates — {group_choice}")
            fig.update_yaxes(tickformat=".1%")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(segments, use_container_width=True, hide_index=True)

with decision_tab:
    st.subheader("Hypothetical review scenarios")
    st.caption("All amounts are illustrative units. Flagging a case is assumed to avoid the missed-case penalty; this is not an observed intervention benefit.")
    review_cost = st.slider("Cost per review (hypothetical units)", 0, 200, 25, 5)
    missed_cost = st.slider("Cost per missed positive case (hypothetical units)", 50, 2000, 500, 50)
    threshold_df = require_report("day10_threshold_analysis.csv")
    if threshold_df is not None:
        expected = {"Threshold", "Flagged", "FN", "Applicants", "Recall", "Precision"}
        if not expected.issubset(threshold_df.columns):
            st.error(f"Threshold file is missing columns: {sorted(expected - set(threshold_df.columns))}")
        else:
            costs = threshold_df.copy()
            costs["Hypothetical cost"] = costs["Flagged"] * review_cost + costs["FN"] * missed_cost
            best = costs.loc[costs["Hypothetical cost"].idxmin()]
            k1, k2, k3 = st.columns(3)
            k1.metric("Lowest-cost tested threshold", f"{best['Threshold']:.2f}")
            k2.metric("Applications flagged", f"{int(best['Flagged']):,}")
            k3.metric("Modeled cost", f"{best['Hypothetical cost']:,.0f} units")
            fig = px.line(costs, x="Threshold", y="Hypothetical cost", title="Cost sensitivity across probability thresholds")
            fig.add_vline(x=float(best["Threshold"]), line_dash="dash")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(costs[["Threshold", "Flagged", "Precision", "Recall", "FN", "Hypothetical cost"]],
                         use_container_width=True, hide_index=True)

    st.subheader("Fixed-capacity review")
    capacity_df = require_report("day10_capacity_analysis.csv")
    if capacity_df is not None:
        required = {"Requested_Capacity", "Flagged", "Applicants", "FN", "TP", "Recall"}
        if not required.issubset(capacity_df.columns):
            st.error(f"Capacity file is missing columns: {sorted(required - set(capacity_df.columns))}")
        else:
            cap = capacity_df.copy()
            # Do not present old ceiling-rounded records as satisfying a hard capacity constraint.
            strict_max = np.floor(cap["Applicants"] * cap["Requested_Capacity"] + 1e-10).astype(int)
            stale = cap["Flagged"] > strict_max
            if stale.any():
                st.warning("Some capacity rows exceed their stated maximum, likely from the older ceiling-rounding notebook. "
                           "Rerun the corrected Day 10 notebook and regenerate day10_capacity_analysis.csv. "
                           "Noncompliant rows are excluded from capacity recommendations.")
            cap = cap.loc[~stale].copy()
            if not cap.empty:
                allowed_percent = st.slider("Maximum review capacity (%)", 5, 50, 20, 5)
                eligible = cap[cap["Flagged"] <= np.floor(cap["Applicants"] * allowed_percent / 100).astype(int)]
                cap["Hypothetical cost"] = cap["Flagged"] * review_cost + cap["FN"] * missed_cost
                if not eligible.empty:
                    eligible = cap.loc[eligible.index]
                    best_cap = eligible.loc[eligible["Hypothetical cost"].idxmin()]
                    st.success(f"Lowest-cost evaluated eligible strategy: {best_cap['Requested_Capacity']:.0%} "
                               f"capacity, {int(best_cap['Flagged']):,} reviews, "
                               f"{best_cap['Recall']:.2%} recall, "
                               f"{best_cap['Hypothetical cost']:,.0f} hypothetical units.")
                else:
                    st.info("No compliant capacity scenario is available below the selected limit.")
                fig = px.line(cap, x="Requested_Capacity", y="Hypothetical cost", markers=True,
                              title="Hypothetical cost versus fixed review capacity")
                fig.update_xaxes(tickformat=".0%")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(cap, hide_index=True, use_container_width=True)

with explain_tab:
    st.subheader("Model explanation — global SHAP importance")
    shap_df = require_report("day08_shap_importance.csv")
    if shap_df is not None:
        if {"Feature", "Mean Absolute SHAP"}.issubset(shap_df.columns):
            n_show = st.slider("Number of features", 5, 25, 15)
            top = shap_df.nlargest(n_show, "Mean Absolute SHAP").sort_values("Mean Absolute SHAP")
            fig = px.bar(top, x="Mean Absolute SHAP", y="Feature", orientation="h",
                         title="Mean absolute SHAP (raw-score / log-odds units)")
            st.plotly_chart(fig, use_container_width=True)
            st.caption("SHAP explains the fitted model's output, not causal effects. Feature names reflect transformed inputs.")
        else:
            st.error("Expected `Feature` and `Mean Absolute SHAP` in the SHAP CSV.")

st.divider()
st.caption("Research portfolio · Home Credit Default Risk · Aggregated validation analyses · Final held-out test results not included")
