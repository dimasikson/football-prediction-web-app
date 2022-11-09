from collections import deque
from itertools import product
import copy

import pandas as pd
import numpy as np

from ..utils.config import Config as cfg


class SeasonProcessor:
    def __init__(self, results):
        self.results = results
        self.home_team_col = "F_H_TEAM"
        self.away_team_col = "F_A_TEAM"
        self.games_played_col = "GAMES_FOR"
        self.res_cols = ["GAMES",
                         "GOALS",
                         "DIFF",
                         "POINTS",
                         "SHOTS",
                         "TSHOTS",
                         "FOULS",
                         "CORNERS",
                         "YELLOWS",
                         "REDS"]

        self.table_cols = [*[f"{c}_FOR" for c in self.res_cols],
                           *[f"{c}_AGA" for c in self.res_cols]]

        # define tables
        self.teams = list(pd.concat([results[self.home_team_col], results[self.away_team_col]]).sort_values().unique())
        self.table = LeagueTable(self.teams, self.table_cols)
        self.home_table = LeagueTable(self.teams, self.table_cols)
        self.away_table = LeagueTable(self.teams, self.table_cols)
        self.table_form5 = LeagueTable(self.teams, self.table_cols, 5)

    @property
    def opponent(self):
        return {"H": "A",
                "A": "H"}

    def get_single_result(self, row, side):
        return {c: row[f"F_{side}_{c}"] for c in self.res_cols}

    def get_result_report(self, row, f, a):
        for_res = self.get_single_result(row, f)
        aga_res = self.get_single_result(row, a)
        return {**{f"{k}_FOR": v for k, v in for_res.items()}, 
                **{f"{k}_AGA": v for k, v in aga_res.items()}}

    def enrich_with_stats(self, row, stats, prefix):
        if stats[self.games_played_col] == 0:
            return row

        stats = {f"{prefix}_{k}": v for k, v in stats.items()}
        return {**row, **stats}

    def run(self):
        out = []
        for row in self.results.to_dict("records"):

            # enrich the row with stats
            row = self.enrich_with_stats(row, self.table.live[row[self.home_team_col]], "T_H")
            row = self.enrich_with_stats(row, self.table.live[row[self.away_team_col]], "T_A")
            row = self.enrich_with_stats(row, self.home_table.live[row[self.home_team_col]], "H_H")
            row = self.enrich_with_stats(row, self.away_table.live[row[self.away_team_col]], "A_A")
            row = self.enrich_with_stats(row, self.table_form5.live[row[self.home_team_col]], "F5_H")
            row = self.enrich_with_stats(row, self.table_form5.live[row[self.away_team_col]], "F5_A")

            # get latest result report
            home_res = self.get_result_report(row, "H", "A")
            away_res = self.get_result_report(row, "A", "H")

            # update table
            self.table.add_result(row[self.home_team_col], home_res)
            self.table.add_result(row[self.away_team_col], away_res)
            self.home_table.add_result(row[self.home_team_col], home_res)
            self.away_table.add_result(row[self.away_team_col], away_res)
            self.table_form5.add_result(row[self.home_team_col], home_res)
            self.table_form5.add_result(row[self.away_team_col], away_res)

            # save enriched row
            out.append(row)

        return pd.DataFrame(out)

class LeagueTable:
    def __init__(self, teams, cols, form=0):
        self.teams = teams
        self.cols = cols
        self.form = form
        self.stats = {t: {c: 0 for c in self.cols} for t in self.teams}
        self.queue = {t: deque([{c: 0 for c in self.cols}] * self.form, self.form) for t in self.teams}

        self.points_col = "POINTS_FOR"
        self.goals_for_col = "GOALS_FOR"
        self.games_played_col = "GAMES_FOR"
        self.goal_diff_col = "DIFF_FOR"
        self.position_col = "POSITION_FOR"

    def add_result(self, team, result):
        for k, v in result.items():
            self.stats[team][k] += v

        if self.form > 0:
            old_result = self.queue[team].popleft()
            for k, v in old_result.items():
                self.stats[team][k] -= v

            self.queue[team].append(result)
    
    def update_position(self, table):
        sort_conditions = lambda team_name: (
            -table[team_name].get(self.points_col, 0),
            -table[team_name].get(self.goal_diff_col, 0),
            -table[team_name].get(self.goals_for_col, 0),
            team_name)

        sorted_teams = sorted(table, key = sort_conditions)
        for pos, team in enumerate(sorted_teams):
            table[team][self.position_col] = pos + 1
        
        return table

    def convert_to_avg(self, table):
        cols = [c for c in self.cols if c not in [self.games_played_col, self.position_col]]
        for team, col in product(self.teams, cols):
            if table[team][self.games_played_col] > 0:
                table[team][col] = table[team][col] / table[team][self.games_played_col]

        return table
    
    @property
    def live(self):
        table = copy.deepcopy(self.stats)
        table = self.update_position(table)
        table = self.convert_to_avg(table)
        return table
