from prepro import downloadFiles, preProcess
from train import predict
from aws import uploadFileAWS
import os

firstSeason = 0
firstSeasonTest = 20
lastSeason = 20

leagues = {
    'E0': 5,
    'D1': 6,
    'I1': 5,
    'SP1': 5,
    'F1': 5,
    'E1': 5,
    'P1': 17,
    'N1': 17
}

# AWS access
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.environ.get('S3_BUCKET')
fpath = "static/predicted.txt"


def updatePredictions(download, preprocess, predictYN, leagues, firstSeason, firstSeasonTest, lastSeason, train):

    if download:
        downloadFiles(
            firstSeason=firstSeason, 
            firstSeasonTest=firstSeasonTest, 
            lastSeason=lastSeason, 
            train=train, 
            leagues=leagues
        )

    if preprocess:
        preProcess(
            firstSeason=firstSeason, 
            firstSeasonTest=firstSeasonTest, 
            lastSeason=lastSeason, 
            train=train, 
            leagues=leagues
        )

    if predictYN:
        predict(leagues=leagues)
        uploadFileAWS(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME, fpath)


# updatePredictions(
#     download=True, 
#     preprocess=True, 
#     predictYN=True, 
#     leagues=leagues,
#     firstSeason=firstSeason, 
#     firstSeasonTest=firstSeasonTest, 
#     lastSeason=lastSeason, 
#     train=True
# )


