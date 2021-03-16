
import numpy as np
import pandas as pd

import xgboost as xgb
import pickle
import shap
import sklearn

import os
import datetime
import time
import json

from utils import cleanDate, loadDf, printResults

leagues = [
    'E0',
    'D1',
    'I1',
    'SP1',
    'F1',
    'E1',
    'P1',
    'N1'
]


def train(leagues):

    for league in leagues:

        X_train, y_train, _ = loadDf(f'processedData/train_{league}.csv', shuffle_yn=True)
        X_test, y_test, _ = loadDf(f'processedData/test_{league}.csv', shuffle_yn=False)

        num_round = 200
        features = X_train.columns.values

        param = {
            'objective': 'reg:squarederror',
            'eta': 0.2,
            'scale_pos_weight': (y_train.size - y_train.sum()) / y_train.sum()
        }

        xg_train = xgb.DMatrix(X_train.values, feature_names = features, label = y_train.values)
        xg_test = xgb.DMatrix(X_test.values, feature_names = features, label = y_test.values)

        watchlist = [
            (xg_train, 'train'),
            (xg_test, 'test'),
        ]
        
        reg = xgb.train(
            param, 
            xg_train, 
            num_round, 
            watchlist,
            verbose_eval=True, 
            early_stopping_rounds=10
        )

        # save
        file_name = f"models/model_{league}.pkl"
        pickle.dump(reg, open(file_name, "wb"))
        print(f'{league} done')


def predict(leagues):

    out = {}

    for league in leagues:
        print(league)

        X_test, y_test, test = loadDf(f'processedData/test_{league}.csv', shuffle_yn=False)
        if len(X_test) == 0:
            continue

        file_name = f"models/model_{league}.pkl"
        xgb_model_loaded = pickle.load(open(file_name, "rb"))

        features = X_test.columns.values

        xg_test = xgb.DMatrix(
            X_test.values, feature_names = features, label = y_test.values
        )

        explainer = shap.TreeExplainer(xgb_model_loaded)
        shap_values = explainer.shap_values(X_test)

        for i, f in enumerate(features):
            cname = 'shap_'+f
            test.loc[:, cname] = shap_values[:, i]
    
        test.loc[:, 'intercept'] = explainer.expected_value
        test.loc[:, 'preds'] = xgb_model_loaded.predict(xg_test)

        maxDt = max(test.loc[:, 'Date']) + pd.DateOffset(1-7*52)
        tmp = test.loc[test.loc[:, 'Date']>=maxDt, :]

        for i in tmp.index:

            gameId = f'{i}_{league}'
            out[gameId] = {}

            for j, col in enumerate(tmp.columns.values[1:]):
                val = tmp.loc[i][j+1]

                if type(val) == np.int64:
                    val = int(val)
                
                if type(val) == np.float32 or type(val) == np.float64:
                    val = float(val)
                
                if type(val) == np.ndarray:
                    val = None
                    
                if type(val) == pd.Timestamp:
                    val = str(val)
                    
                out[gameId][col] = val

        # print performance (accuracy, ROI)
        printResults(tmp, league)
    
    with open(f'static/predicted.txt', 'w') as outfile:
        json.dump(out, outfile)


# train(leagues)
# predict(leagues)
