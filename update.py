from prepro import downloadFiles, preProcess
from train import predict
from storage import uploadFileAzure, AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME, PREDICTED_FPATH
import os

def updatePredictions(download, preprocess, predictYN, leagues, firstSeason, firstSeasonTest, lastSeason, train):

    if download:
        downloadFiles(
            firstSeason=firstSeason, 
            firstSeasonTest=firstSeasonTest, 
            lastSeason=lastSeason, 
            train=train, 
            leagues=leagues
        )
        print('Files downloaded!')

    if preprocess:
        preProcess(
            firstSeason=firstSeason, 
            firstSeasonTest=firstSeasonTest, 
            lastSeason=lastSeason, 
            train=train, 
            leagues=leagues
        )
        print('Preprocessing done!')

    if predictYN:
        predict(leagues=leagues)
        print('Predictions done!')

        uploadFileAzure(PREDICTED_FPATH, AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME)
        print('Uploaded to Azure!')


