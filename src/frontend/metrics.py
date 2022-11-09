import streamlit as st
import pandas as pd
import numpy as np

from ..utils.config import Config as cfg

def nullable_pct(num, den):
    return 100 * num / den

def format_pct(n):
    return "{0:.1f}%".format(n if n == n else 0)

def get_metrics(df, fmt=True):
    df["Finished Games"] = df.F_H_GAMES
    df["Accuracy (%)"] = nullable_pct(df.PRED_CORRECT, df.F_H_GAMES)
    df["ROI (%)"] = nullable_pct(df.PRED_RETURNS, df.F_H_GAMES)
    return df if not fmt else format_metrics(df)

def format_metrics(df):
    df["Finished Games"] = df["Finished Games"].astype(int).astype(str)
    df["Accuracy (%)"] = df["Accuracy (%)"].apply(lambda x: format_pct(x))
    df["ROI (%)"] = df["ROI (%)"].apply(lambda x: format_pct(x))
    return df

def metric_dashboard(c, name, metrics):
    metric_containers = c.columns(len(metrics) + 1)
    metric_containers[0].metric("", name)
    for cont, (name, val) in zip(metric_containers[1:], metrics.items()):
        cont.metric(name, val)
