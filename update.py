from prepro import downloadFiles, preProcess
from train import predict

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


# updatePredictions(
#     download=True, 
#     preprocess=True, 
#     predictYN=True, 
#     leagues=leagues,
#     firstSeason=firstSeason, 
#     firstSeasonTest=firstSeasonTest, 
#     lastSeason=lastSeason, 
#     train=False
# )


