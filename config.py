
import os

class Config:

    # Azure access
    AZURE_CONNECTION_STRING = os.environ["AZURE_CONNECTION_STRING"]
    AZURE_CONTAINER_NAME = os.environ["AZURE_CONTAINER_NAME"]

    # AWS access
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    BUCKET_NAME = os.environ['S3_BUCKET']

    # fpath
    PREDICTED_FPATH = "static/predicted.txt"

    # starting year for each league
    LEAGUES = {
        'E0': 5,
        'D1': 6,
        'I1': 5,
        'SP1': 5,
        'F1': 5,
        'E1': 5,
        'P1': 17,
        'N1': 17,
        'T1': 17,
        'B1': 17,
        'SC0': 17,
    }

    # train / test split by season
    FIRST_SEASON = 0
    FIRST_SEASON_TEST = 21
    LAST_SEASON = 21

    # args of update url
    UPDATE_ARGS = {
        "downloadYN": "True",
        "preprocessYN": "True",
        "trainData": "False",
        "trainYN": "False",
        "predictYN": "True",
    }


