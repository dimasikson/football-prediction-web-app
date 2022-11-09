import streamlit as st
import pandas as pd

from .metrics import metric_dashboard
from ..utils.config import Config as cfg


class MatchReport:
    def __init__(self, row):
        self.row = row
        self.div = self.row['F_DIV']
        self.ret = "{0:.2f}".format(self.row['PRED_RETURNS'])
        self.pred_diff = "{0:.2f}".format(self.row['PRED_DIFF'])
        self.res = self.row['F_RESULT']
        self.pred_res = cfg.PRED_MAPPING[self.row['PRED_RESULT_NUM']]
        self.dt = self.row['F_DATE']
        self.tm = self.row['F_TIME']
        self.f = st.expander(self.title, False)
        self.shap_intercept = "SHAP_INTERCEPT"

    def __get_feature_value(self, shap_name):
        return self.row.get(shap_name.replace("SHAP_", ""))

    def get_shap_table(self, shap_values):
        shap_df = pd.DataFrame([{"Feature name": k,
                                 "Feature value": self.__get_feature_value(k),
                                 "SHAP value": v} for k, v in shap_values.items()]) \
            .sort_index(ascending=False) \
            .reset_index(drop=True)

        shap_df["Cumulative SHAP value"] = shap_df["SHAP value"].cumsum()
        return shap_df.style.background_gradient(cmap="RdYlGn",
                                                 subset=["SHAP value",
                                                         "Cumulative SHAP value"])

    def render(self):
        self.f.header(self.score)
        self.f.subheader(f"Kick-off: {self.dt.strftime('%d %b %Y')}, {self.tm}")
        metric_dashboard(self.f, "Odds:", {"Home": self.row["ODDS_H_MAX"],
                                           "Draw": self.row["ODDS_D_MAX"],
                                           "Away": self.row["ODDS_A_MAX"]})
        self.f.subheader(self.res_detailed)
        self.f.markdown("SHAP local explanation:")
        shap_values = dict(self.row[(self.row.index.str.startswith("SHAP")) & (self.row.values != 0)])
        shap_df = self.get_shap_table(shap_values)
        self.f.table(shap_df)

class FixtureReport(MatchReport):
    def __init__(self, row):
        super().__init__(row)

    @property
    def res_detailed(self):
        return f"Predicted result: {self.pred_diff} ({self.pred_res})"

    @property
    def title(self):
        return f"{self.score} | league: {self.div} | kick-off: {self.tm} | predicted: {self.pred_diff} ({self.pred_res})"

    @property
    def score(self):
        ht = self.row['F_H_TEAM']
        at = self.row['F_A_TEAM']
        return f"{ht} - {at}"


class ResultReport(MatchReport):
    def __init__(self, row):
        super().__init__(row)

    @property
    def res_detailed(self):
        return f"Return: {self.ret} | Predicted result: {self.pred_diff} ({self.pred_res})"

    @property
    def title(self):
        return f"{self.score} | league: {self.div} | predicted: {self.pred_diff} ({self.pred_res}) | result: {self.res} | return: {self.ret}"

    @property
    def score(self):
        ht = self.row['F_H_TEAM']
        at = self.row['F_A_TEAM']
        hg = int(self.row['F_H_GOALS'])
        ag = int(self.row['F_A_GOALS'])
        return f"{ht} {hg} - {ag} {at}"
