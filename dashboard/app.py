"""Home Credit risk analytics portfolio dashboard.

Reads aggregate validation and held-out test results; never loads applicant-level records or models.
Run from the project root: streamlit run dashboard/app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Home Credit | Risk Analytics", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
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


with st.sidebar:
    st.header("About this project")
    st.markdown("**Home Credit Default Risk**\n\nExploratory credit risk modeling and portfolio analytics using SQL, LightGBM, and SHAP.")
    st.markdown("**Data:** Kaggle Home Credit Default Risk\n\n**Evaluation:** stratified validation + held-out test\n\n**Model:** LightGBM")
    st.divider()
    st.markdown("**How to use**")
    st.markdown("1. Compare validation models.\n2. Explore risk deciles.\n3. Adjust hypothetical costs.\n4. Review feature explanations.\n5. Check final held-out test results.")
    st.caption("Final held-out test metrics are shown separately from validation-based exploratory analysis. This is not a credit decision tool.")

st.title("Home Credit · Risk Analytics")
st.caption("Portfolio research dashboard | Historical repayment-difficulty data | Validation and held-out test results")
st.warning(
    "For exploratory analytics only. Predicted scores and hypothetical review costs are not "
    "validated lending, approval, denial, or financial-loss recommendations.", icon="ℹ️"
)

model_tab, risk_tab, decision_tab, explain_tab, final_tab = st.tabs(
    ["Model overview", "Risk segmentation", "Review scenarios", "Explainability", "Final test evaluation"]
)

with model_tab:
    st.subheader("Model comparison")
    st.markdown("**Question:** Does gradient boosting improve the ranking of repayment-difficulty cases compared with an interpretable linear baseline?")
    model_df = require_report("day06_model_comparison.csv")
    if model_df is not None:
        if "Unnamed: 0" in model_df.columns:
            model_df = model_df.rename(columns={"Unnamed: 0": "Model"})
        if "Model" not in model_df.columns:
            st.error("Expected a model-name index or `Model` column in day06_model_comparison.csv")
        else:
            available = [x for x in ["ROC-AUC", "Average Precision", "Brier Score"] if x in model_df.columns]
            if available:
                by_model = model_df.set_index("Model")
                if {"LightGBM", "Logistic Regression"}.issubset(by_model.index) and "ROC-AUC" in available:
                    k1, k2, k3 = st.columns(3)
                    k1.metric("LightGBM ROC-AUC", f"{by_model.loc['LightGBM', 'ROC-AUC']:.4f}")
                    if "Average Precision" in available:
                        k2.metric("LightGBM average precision", f"{by_model.loc['LightGBM', 'Average Precision']:.4f}")
                    if "Brier Score" in available:
                        k3.metric("LightGBM Brier score", f"{by_model.loc['LightGBM', 'Brier Score']:.4f}")
                st.dataframe(model_df[["Model"] + available].set_index("Model").style.format({k: "{:.4f}" for k in available}), width="stretch")
                if "ROC-AUC" in available:
                    fig = px.bar(model_df, x="Model", y="ROC-AUC", title="Validation ROC-AUC", text_auto=".4f")
                    fig.update_yaxes(range=[0, max(.8, float(model_df["ROC-AUC"].max()) + .02)])
                    st.plotly_chart(fig, width="stretch")
    st.caption("These are validation metrics used during model development. See **Final test evaluation** for the frozen-model results on unseen test observations.")

with risk_tab:
    st.subheader("Risk deciles and cumulative capture")
    st.markdown("**Question:** Does the model concentrate more recorded positive cases among applicants with higher scores?")
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
            st.plotly_chart(fig, width="stretch")

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
            st.plotly_chart(fig, width="stretch")
            st.dataframe(deciles, width="stretch", hide_index=True)
            st.download_button("Download decile summary CSV", deciles.to_csv(index=False).encode("utf-8"),
                               file_name="risk_deciles_summary.csv", mime="text/csv")

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
            st.plotly_chart(fig, width="stretch")
        st.dataframe(segments, width="stretch", hide_index=True)

with decision_tab:
    st.subheader("Hypothetical review scenarios")
    st.markdown("**Question:** How do review workload and assumed missed-case penalties affect a model-assisted prioritization scenario?")
    st.caption("All amounts are illustrative units. Flagging a case is assumed to avoid the missed-case penalty; this is not an observed intervention benefit.")
    st.caption("The interactive threshold and capacity comparisons use validation results only. The 0.06 threshold and strict 20% capacity were frozen before held-out testing.")
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
            st.plotly_chart(fig, width="stretch")
            st.dataframe(costs[["Threshold", "Flagged", "Precision", "Recall", "FN", "Hypothetical cost"]],
                         width="stretch", hide_index=True)

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
                st.plotly_chart(fig, width="stretch")
                st.dataframe(cap, hide_index=True, width="stretch")

with explain_tab:
    st.subheader("Model explanation — global SHAP importance")
    st.markdown("**Question:** Which transformed model inputs have the greatest average influence on raw scores?")
    shap_df = require_report("day08_shap_importance.csv")
    if shap_df is not None:
        if {"Feature", "Mean Absolute SHAP"}.issubset(shap_df.columns):
            n_show = st.slider("Number of features", 5, 25, 15)
            top = shap_df.nlargest(n_show, "Mean Absolute SHAP").sort_values("Mean Absolute SHAP")
            fig = px.bar(top, x="Mean Absolute SHAP", y="Feature", orientation="h",
                         title="Mean absolute SHAP (raw-score / log-odds units)")
            st.plotly_chart(fig, width="stretch")
            st.caption("SHAP explains the fitted model's output, not causal effects. Feature names reflect transformed inputs.")
        else:
            st.error("Expected `Feature` and `Mean Absolute SHAP` in the SHAP CSV.")


with final_tab:
    st.subheader("Final held-out model evaluation")
    st.markdown(
        "**Question:** Does LightGBM's validation performance generalize to the untouched "
        "test partition, and does it still outperform Logistic Regression?"
    )
    st.caption(
        "Final evaluation: 61,503 held-out applications. Model parameters, preprocessing, "
        "and the 0.06 threshold were selected without test labels."
    )

    final_models = require_report("day13_final_model_metrics.csv")
    if final_models is not None:
        final_models = final_models.rename(columns={"Unnamed: 0": "Model"})
        expected = {"Model", "ROC-AUC", "Average Precision", "Brier Score"}
        if expected.issubset(final_models.columns):
            test_by_model = final_models.set_index("Model")
            if "LightGBM" in test_by_model.index:
                test_lgbm = test_by_model.loc["LightGBM"]
                m1, m2, m3 = st.columns(3)
                m1.metric("Test ROC-AUC", f"{test_lgbm['ROC-AUC']:.4f}")
                m2.metric("Test average precision", f"{test_lgbm['Average Precision']:.4f}")
                m3.metric("Test Brier score", f"{test_lgbm['Brier Score']:.5f}")
            st.dataframe(
                test_by_model[["ROC-AUC", "Average Precision", "Brier Score"]].style.format("{:.4f}"),
                width="stretch",
            )
        else:
            st.error(f"day13_final_model_metrics.csv is missing: {sorted(expected - set(final_models.columns))}")

    st.divider()
    st.subheader("Validation vs. held-out test")
    generalization = require_report("day13_generalization.csv")
    if generalization is not None:
        expected = {"Model", "Metric", "Validation", "Test"}
        if expected.issubset(generalization.columns):
            metric_choice = st.selectbox(
                "Performance metric", ["ROC-AUC", "Average Precision", "Brier Score"],
                key="final_metric_choice",
            )
            metric_rows = generalization.loc[generalization["Metric"] == metric_choice]
            if not metric_rows.empty:
                metric_long = metric_rows.melt(
                    id_vars="Model", value_vars=["Validation", "Test"],
                    var_name="Dataset", value_name="Value",
                )
                fig = px.bar(
                    metric_long, x="Model", y="Value", color="Dataset",
                    barmode="group", text_auto=".4f",
                    title=f"{metric_choice}: validation vs. held-out test",
                )
                fig.update_yaxes(range=[0, 1] if metric_choice != "Brier Score" else [0, 0.10])
                st.plotly_chart(fig, width="stretch")
                st.dataframe(metric_rows, hide_index=True, width="stretch")
            else:
                st.info(f"No rows found for {metric_choice}.")
        else:
            st.error(f"day13_generalization.csv is missing: {sorted(expected - set(generalization.columns))}")

    intervals = require_report("day13_model_difference_intervals.csv")
    if intervals is not None:
        intervals = intervals.rename(columns={"Unnamed: 0": "Metric"})
        needed = {"Metric", "Mean_Difference", "CI_Lower", "CI_Upper"}
        if needed.issubset(intervals.columns):
            with st.expander("Paired bootstrap: LightGBM minus Logistic Regression"):
                st.dataframe(intervals.set_index("Metric").style.format("{:+.5f}"), width="stretch")
                st.caption(
                    "Approximate 95% paired bootstrap intervals on the test partition. "
                    "Positive differences favor LightGBM for ROC-AUC and average precision; "
                    "negative differences favor LightGBM for Brier score."
                )
        else:
            st.error(f"day13_model_difference_intervals.csv is missing: {sorted(needed - set(intervals.columns))}")

    st.divider()
    st.subheader("Risk deciles on unseen test applications")
    test_deciles = require_report("day13_test_risk_deciles.csv")
    if test_deciles is not None:
        needed = {"Decile", "Applicants", "Positive_Cases", "Observed_Rate", "Mean_Predicted_Risk", "Lift"}
        if needed.issubset(test_deciles.columns):
            test_deciles = test_deciles.sort_values("Decile")
            high_decile = test_deciles.iloc[-1]
            top_n = int(test_deciles["Applicants"].sum())
            top_pos = int(test_deciles["Positive_Cases"].sum())
            c1, c2, c3 = st.columns(3)
            c1.metric("Test applications", f"{top_n:,}")
            c2.metric("Overall observed rate", pct(top_pos / top_n))
            c3.metric("Top-decile lift", f"{high_decile['Lift']:.2f}×")
            rates = test_deciles[["Decile", "Observed_Rate", "Mean_Predicted_Risk"]].melt(
                id_vars="Decile", var_name="Series", value_name="Rate"
            )
            fig = px.line(
                rates, x="Decile", y="Rate", color="Series", markers=True,
                title="Held-out test: observed vs. predicted risk by decile",
            )
            fig.update_yaxes(tickformat=".1%")
            fig.update_xaxes(dtick=1)
            st.plotly_chart(fig, width="stretch")
            st.dataframe(test_deciles, hide_index=True, width="stretch")
            st.download_button(
                "Download test decile summary CSV",
                test_deciles.to_csv(index=False).encode("utf-8"),
                file_name="held_out_test_risk_deciles.csv", mime="text/csv",
            )
        else:
            st.error(f"day13_test_risk_deciles.csv is missing: {sorted(needed - set(test_deciles.columns))}")

    st.divider()
    st.subheader("Frozen screening policies: validation vs. test")
    policy = require_report("day13_policy_comparison.csv")
    if policy is not None:
        policy = policy.rename(columns={"Unnamed: 0": "Strategy"})
        needed = {"Strategy", "Reviewed", "Review_Rate", "TP", "FP", "FN", "Precision", "Recall"}
        if needed.issubset(policy.columns):
            visible = ["Strategy", "Reviewed", "Review_Rate", "TP", "FP", "FN", "Precision", "Recall"]
            if "Modeled_Cost" in policy.columns:
                visible.append("Modeled_Cost")
            st.dataframe(policy[visible], hide_index=True, width="stretch")
            chart = px.bar(
                policy, x="Strategy", y="Recall", color="Strategy", text_auto=".1%",
                title="Positive-case capture for frozen review strategies",
            )
            chart.update_yaxes(tickformat=".0%", range=[0, 1])
            chart.update_layout(showlegend=False)
            st.plotly_chart(chart, width="stretch")
            st.caption(
                "The threshold (0.06) and top-20% policy were selected using validation data. "
                "The test results evaluate those frozen choices; they are not used to retune them. "
                "Any displayed cost is illustrative, not measured financial savings."
            )