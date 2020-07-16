from prepro import downloadFiles, preProcess
from train import predict
from aws import up

firstSeason = 0
firstSeasonTest = 19
lastSeason = 19

leagues = {
    'E0': 5,
    'D1': 6,
    'I1': 5,
    'SP1': 5,
    'F1': 5
}

# AWS access
AWS_ACCESS_KEY_ID = 'AKIAIDGSP4IVPNH4W7BQ'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'football-prediction-web-app'
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
#     download=False, 
#     preprocess=False, 
#     predictYN=True, 
#     leagues=leagues,
#     firstSeason=firstSeason, 
#     firstSeasonTest=firstSeasonTest, 
#     lastSeason=lastSeason, 
#     train=False
# )


