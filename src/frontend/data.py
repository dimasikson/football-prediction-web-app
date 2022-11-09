import streamlit as st
import pandas as pd
import numpy as np

from ..utils.config import Config as cfg
from ..storage.tables import AzureBlobTable


@st.cache(allow_output_mutation=True)
def read_data():
    df = AzureBlobTable(cfg.AZURE_PREDICTIONS_TABLE, ftype="parquet").read("data")
    df["F_DATE"] = pd.to_datetime(df["F_DATE"])
    df["Predicted result"] = df.PRED_RESULT_NUM.apply(lambda x: cfg.PRED_MAPPING[x])
    return df

def load_data(leagues):
    df = read_data()
    conditions = [f"F_DIV == '{lg}'" for lg in leagues]
    if len(conditions):
        df = df.query(" or ".join(conditions))

    return df.sort_values(["F_DATE", "F_TIME", "F_DIV"], ascending=False).reset_index(drop=True)

def aggregate_df(df, col=""):
    df = df.loc[df.F_RESULT == df.F_RESULT]
    return df.groupby(col).sum(numeric_only=True) if col else np.transpose(pd.DataFrame(df.sum(numeric_only=True)))

def aggregate_by_date(df, col, rolling=1):
    df = df.loc[df.F_RESULT == df.F_RESULT]
    df = df.groupby(col).sum(numeric_only=True).reset_index()
    mn_dt = df[col].min()
    mx_dt = df[col].max()
    daily_df = pd.DataFrame(data={col: pd.date_range(mn_dt, mx_dt)})
    df = df.merge(daily_df, how="left", on=col).fillna(0)
    return df.set_index(col).rolling(rolling).sum(numeric_only=True)

