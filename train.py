
import numpy as np
import pandas as pd

from sklearn.ensemble import GradientBoostingRegressor
import pickle
import shap

import os
import datetime
import time
import json

from utils import loadDf, printResults
from config import Config as cfg

def train(leagues, odds=True):

    for league in leagues:

        X_train, y_train, _ = loadDf(f'processedData/train_{league}.csv', shuffle_yn=True, odds=odds)

        reg = GradientBoostingRegressor(
            random_state=0,
            n_estimators=200,
            loss='ls',
            learning_rate=0.1,
            verbose=1,
            n_iter_no_change=10,
            max_depth=6,
        )
        
        reg.fit(X_train, y_train)

        # save
        sfx = "" if odds else "_mini"
        file_name = f"models/model_{league}{sfx}.pkl"
        pickle.dump(reg, open(file_name, "wb"))
        print(f'{league} done')


def predict(leagues, odds=True):

    out = {}

    for league in leagues:
        print(league)

        X_test, _, test = loadDf(f'processedData/test_{league}.csv', shuffle_yn=False, odds=odds)
        if len(X_test) == 0:
            continue

        file_name = f"models/model_{league}.pkl"
        gbr_model_loaded = pickle.load(open(file_name, "rb"))

        explainer = shap.TreeExplainer(gbr_model_loaded)
        shap_values = explainer.shap_values(X_test)

        for i, f in enumerate(X_test.columns.values):
            cname = 'shap_'+f
            test.loc[:, cname] = shap_values[:, i]
    
        test.loc[:, 'intercept'] = explainer.expected_value
        test.loc[:, 'preds'] = gbr_model_loaded.predict(X_test)

        maxDt = max(test.loc[:, 'Date']) + pd.DateOffset(1-7*52)
        tmp = test.loc[test.loc[:, 'Date']>=maxDt, :]

        for idx, row in tmp.iterrows():

            gameId = f'{idx}_{league}'
            out[gameId] = {}

            for col in tmp.columns.values[1:]:
                val = row[col]

                if type(val) == np.int64:
                    val = int(val)
                
                if type(val) == np.float32 or type(val) == np.float64:
                    val = float(val)
                
                if type(val) == np.ndarray:
                    val = None
                    
                if type(val) == pd.Timestamp:
                    val = val.strftime('%Y-%m-%d')
                    
                out[gameId][col] = val

        # print performance (accuracy, ROI)
        printResults(tmp, league)
    
    with open(cfg.PREDICTED_FPATH, 'w') as outfile:
        json.dump(out, outfile)


if __name__ == "__main__":
    train(cfg.LEAGUES.keys())
    predict(cfg.LEAGUES.keys())
