import math

import pandas as pd
import numpy as np

from .config import Config as cfg


def get_partitions(min_season, max_season):
    partitions = []
    for league, first_season in cfg.LEAGUES.items():
        rng = range(max(min_season, first_season), max_season + 1)
        seasons = ["{:02d}".format(num) for num in rng]
        partitions += [f"{left + right}/{league}" for left, right in zip(seasons[:-1], seasons[1:])]

    return partitions

def rmse(y, y_pred):
    return math.sqrt(np.square(np.subtract(y, y_pred)).mean())

def split_features_target(df):
    y = df.loc[:, cfg.TARGET_COL]
    X = df.loc[:, df.columns.str.startswith("F_DIV") |
                    df.columns.str.startswith("T_") |
                    df.columns.str.startswith("H_") |
                    df.columns.str.startswith("A_") |
                    df.columns.str.startswith("F5_") |
                    df.columns.str.startswith("ODDS_")]
    X = X.loc[:, ~X.columns.str.contains("GAMES")]
    X = pd.get_dummies(X)

    return X, y

def enrich_df_with_predictions(df, pred):
    df["PRED_DIFF"] = pred
    df["PRED_RESULT_NUM"] = np.sign(df["PRED_DIFF"].round())
    df["F_RESULT_NUM"] = np.sign(df[cfg.TARGET_COL])
    df["PRED_CORRECT"] = df["PRED_RESULT_NUM"] == df["F_RESULT_NUM"]
    df["PRED_ODDS"] = df.apply(lambda x: x[f"ODDS_{cfg.PRED_MAPPING[x['PRED_RESULT_NUM']]}_MAX"], axis=1)
    df["PRED_RETURNS"] = (df["PRED_ODDS"] * df["PRED_CORRECT"]) - 1
    return df

def clean_results(df):
    SELECT_COLS = ["F_DIV",
                   "F_DATE",
                   "F_TIME",
                   "F_RESULT",
                   "F_H_TEAM",
                   "F_A_TEAM",
                   "F_H_GOALS",
                   "F_A_GOALS",
                   "F_H_SHOTS",
                   "F_A_SHOTS",
                   "F_H_TSHOTS",
                   "F_A_TSHOTS",
                   "F_H_FOULS",
                   "F_A_FOULS",
                   "F_H_CORNERS",
                   "F_A_CORNERS",
                   "F_H_YELLOWS",
                   "F_A_YELLOWS",
                   "F_H_REDS",
                   "F_A_REDS",
                   "ODDS_H_MAX",
                   "ODDS_D_MAX",
                   "ODDS_A_MAX",
                   "ODDS_H_AVG",
                   "ODDS_D_AVG",
                   "ODDS_A_AVG"]

    # select columns and mapping
    df = df.rename(columns=cfg.COL_MAPPING)
    df = df.reindex(SELECT_COLS, axis=1)

    # remove rows with no team
    df = df.loc[df.loc[:,"F_H_TEAM"] == df.loc[:,"F_H_TEAM"],:]
    df = df.loc[df.loc[:,"F_A_TEAM"] == df.loc[:,"F_A_TEAM"],:]

    # patch date and time
    df["F_TIME"] = df["F_TIME"].fillna("00:00")
    df["F_DATE"] = pd.to_datetime(df["F_DATE"], dayfirst=True)
    df = df.sort_values(["F_DATE", "F_TIME"])

    # add additional vectorized features
    df["F_H_POINTS"] = df.apply(lambda x: 3 if x["F_RESULT"] == "H" else (1 if x["F_RESULT"] == "D" else 0), axis=1)
    df["F_A_POINTS"] = df.apply(lambda x: 3 if x["F_RESULT"] == "A" else (1 if x["F_RESULT"] == "D" else 0), axis=1)
    df["F_H_DIFF"] = df["F_H_GOALS"] - df["F_A_GOALS"]
    df["F_A_DIFF"] = df["F_A_GOALS"] - df["F_H_GOALS"]
    df["F_H_GAMES"] = 1
    df["F_A_GAMES"] = 1

    # dedupe games
    dedupe_dimensions = ["F_DIV", "F_H_TEAM", "F_A_TEAM"]
    dedupe_condition = df.sort_values(dedupe_dimensions + ["F_RESULT"]).groupby(dedupe_dimensions).cumcount() == 0
    df = df.loc[dedupe_condition, :]

    return df
