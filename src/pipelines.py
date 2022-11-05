import os
import sys
from datetime import datetime

import pandas as pd

from config import Config as cfg
from explain import get_shap_explanations
from preprocess import SeasonProcessor
from storage import AzureBlobTable, ExternalBlobTable
from utils import get_partitions, clean_results, split_features_target


def refresh_fixtures():
    ex_table = ExternalBlobTable(table_name="")
    az_table = AzureBlobTable(cfg.AZURE_FIXTURES_TABLE)

    partitions = [cfg.AZURE_FIXTURES_TABLE]
    fixtures = ex_table.download(partitions, concat=False)
    az_table.upload(fixtures)

def refresh_results(partitions):
    ex_table = ExternalBlobTable(cfg.FOOTBALL_DATA_TABLE)
    az_table = AzureBlobTable(cfg.AZURE_RESULTS_TABLE)

    results = ex_table.download(partitions, concat=False)
    az_table.upload(results)

def preprocess_results(partitions, output_partition_name, add_fixtures=False):
    res_table = AzureBlobTable(cfg.AZURE_RESULTS_TABLE)
    fix_table = AzureBlobTable(cfg.AZURE_FIXTURES_TABLE)

    res = res_table.download(partitions, concat=False)
    if add_fixtures:
        fix = fix_table.download([cfg.AZURE_FIXTURES_TABLE], concat=True)

    dfs = []
    for p, df in res.items():    
        if add_fixtures:
            div = p.split("/")[-1]
            df = pd.concat([df, fix.query(f"Div == '{div}'")]).reset_index(drop=True)

        df = clean_results(df)
        df = SeasonProcessor(df).run()
        dfs.append(df)
        print(datetime.now(), f"processed: {p}")

    az_table = AzureBlobTable(cfg.AZURE_PROCESSED_TABLE)
    az_table.upload({output_partition_name: pd.concat(dfs)})

def generate_predictions(table_name):
    data = AzureBlobTable(cfg.AZURE_PROCESSED_TABLE).download([table_name], concat=True)
    model = AzureBlobTable(table_name=cfg.AZURE_MODELS_FOLDER, ftype="pkl").download(["model"])["model"]

    # generate prediction
    X_data, y_data = split_features_target(data)
    data["Y_PRED"] = model.predict(X_data)

    # add shap values
    shap_values = get_shap_explanations(X_data, model)
    data = pd.merge(data, shap_values, left_index=True, right_index=True)

    az_table = AzureBlobTable(cfg.AZURE_PREDICTIONS_TABLE, ftype="parquet")
    az_table.upload({"data": data})

if __name__ == "__main__":
    train_partitions = get_partitions(cfg.FIRST_SEASON, cfg.CURRENT_SEASON - 1)
    test_partitions = get_partitions(cfg.CURRENT_SEASON - 1, cfg.CURRENT_SEASON)
    valid_partitions = get_partitions(cfg.CURRENT_SEASON, cfg.CURRENT_SEASON + 1)

    # refresh_fixtures()
    # refresh_results(train_partitions)
    # refresh_results(test_partitions)
    # refresh_results(valid_partitions)

    # preprocess_results(train_partitions, "train")
    # preprocess_results(test_partitions, "test")
    # preprocess_results(valid_partitions, "valid", add_fixtures=True)

    # generate_predictions("valid")
