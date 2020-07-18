
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

from utils import cleanDate

print(xgb.__version__)

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

        df = pd.read_csv(f'processedData/train_{league}.csv', engine='python')

        df.loc[:, 'Date'] = cleanDate(df.loc[:, 'Date'])
        df = df.loc[(df['T_GamesPlayed_H'] >= 3) & (df['T_GamesPlayed_A'] >= 3)]

        cols = list(range(15,18))+list(range(22,26))+list(range(34,38))+list(range(60,62))
        
        X_train = df.iloc[:,cols]
        y_train = df.loc[:, 'GoalsFor_H'] - df.loc[:, 'GoalsFor_A']

        param = {
            'objective': 'reg:squarederror',
            'eta': 0.2
        }

        num_round = 20

        param['scale_pos_weight']= (y_train.size - y_train.sum()) / y_train.sum()

        features = X_train.columns.values

        xg_train = xgb.DMatrix(
            X_train.values, feature_names = features, label = y_train.values
        )

        watchlist = [(xg_train, 'train')]
        reg = xgb.train(
            param, xg_train, num_round, watchlist, verbose_eval=True
        )

        file_name = f"models/model_{league}.pkl"

        # save
        pickle.dump(reg, open(file_name, "wb"))

        print('done')


# train(leagues)


def predict(leagues):

    out = {}

    for league in leagues:

        df = pd.read_csv(f'processedData/test_{league}.csv', engine='python')

        file_name = f"models/model_{league}.pkl"

        # load
        xgb_model_loaded = pickle.load(open(file_name, "rb"))

        df.loc[:, 'Date'] = cleanDate(df.loc[:, 'Date'])
        df = df.loc[(df['T_GamesPlayed_H'] >= 3) & (df['T_GamesPlayed_A'] >= 3)]

        df = df.fillna(0)

        cols = list(range(15,18))+list(range(22,26))+list(range(34,38))+list(range(60,62))
        
        X_test = df.iloc[:,cols]
        y_test = df.loc[:, 'GoalsFor_H'] - df.loc[:, 'GoalsFor_A']

        features = X_test.columns.values

        xg_test = xgb.DMatrix(
            X_test.values, feature_names = features, label = y_test.values
        )

        explainer = shap.TreeExplainer(xgb_model_loaded)
        shap_values = explainer.shap_values(X_test)

        test = df

        for i, f in enumerate(features):
            cname = 'shap_'+f
            
            test.loc[:, cname] = shap_values[:, i]
    
        test.loc[:, 'intercept'] = explainer.expected_value
        test.loc[:, 'preds'] = xgb_model_loaded.predict(xg_test)

        maxDt = max(test.loc[:, 'Date']) + pd.DateOffset(1-7*52)

        tmp = test.loc[test.loc[:, 'Date']>=maxDt, :]

        for i in tmp.index:

            gameId = str(i)+'_'+league

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
    
    with open(f'static/predicted.txt', 'w') as outfile:
        json.dump(out, outfile)


# predict(leagues)
