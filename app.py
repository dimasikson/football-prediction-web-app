import streamlit as st
import pandas as pd
import numpy as np

from src.utils.config import Config as cfg
from src.frontend.data import load_data, aggregate_df, aggregate_by_date
from src.frontend.metrics import get_metrics, metric_dashboard
from src.frontend.match_report import ResultReport, FixtureReport


METRICS = ["Finished Games",
           "Accuracy (%)",
           "ROI (%)"]


# ---- MAIN -------
st.title("Football Prediction Web App")
selected_leagues = st.multiselect("Select league: ", cfg.LEAGUES.keys())
df = load_data(selected_leagues)

# ---- DISPLAY METRICS DASHBOARD -------
agg_df = aggregate_df(df)
overall_metrics = get_metrics(agg_df)
c = st.container()
metric_dashboard(c, "Stats:", overall_metrics[METRICS].loc[0,:])

# ---- DISPLAY METRICS TABLE -------
agg_df = aggregate_df(df, "Predicted result").reset_index().sort_values("PRED_RESULT_NUM", ascending=False)
metrics_table = get_metrics(agg_df)[["Predicted result"] + METRICS]
st.table(metrics_table)

# ---- DISPLAY ROLLING-28D METRICS -------
st.subheader("Stats over time:")
rlng = st.slider("Moving average rollup (days):", 1, 28, 14)
agg_df = aggregate_by_date(df, "F_DATE", rlng)
date_metrics = get_metrics(agg_df, fmt=False)
st.line_chart(date_metrics[METRICS[1:]])

# ---- RESULTS -------
c = st.container()
res_c = c.columns(3)
res_c[0].header("Results:")
n_games = res_c[-1].selectbox("Select how many games to show:", [25, 50, 100, "All"])
dates = (df.head(n_games) if n_games != "All" else df).F_DATE.unique()
results = df.loc[df.F_DATE.isin(dates),:]

# ---- DISPLAY DATE METRICS -------
for date, date_df in list(results.groupby("F_DATE"))[::-1]:
    pretty_date = date.strftime("%d %b")
    date_metrics = get_metrics(aggregate_df(date_df))[METRICS].loc[0,:]
    c = st.container()
    metric_dashboard(c, pretty_date, date_metrics)

    # ---- DISPLAY MATCHES -------
    for idx, row in date_df.iterrows():
        res = row['F_RESULT']
        report = ResultReport if res else FixtureReport
        title = report(row).render()
