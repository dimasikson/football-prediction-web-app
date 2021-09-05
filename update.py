from prepro import downloadFiles, preProcess
from train import train, predict
from storage import uploadFileAzure
from config import Config as cfg
import os

def pipelineRun(downloadYN, preprocessYN, predictYN, leagues, firstSeason, firstSeasonTest, lastSeason, trainData, trainYN):

    if downloadYN:
        downloadFiles(
            firstSeason=firstSeason, 
            firstSeasonTest=firstSeasonTest, 
            lastSeason=lastSeason, 
            trainData=trainData, 
            leagues=leagues
        )
        print('Files downloaded!')

    if preprocessYN:
        preProcess(
            firstSeason=firstSeason, 
            firstSeasonTest=firstSeasonTest, 
            lastSeason=lastSeason, 
            trainData=trainData, 
            leagues=leagues
        )
        print('Preprocessing done!')

    if trainYN:
        train(leagues=leagues)
        print('Training done!')

    if predictYN:
        predict(leagues=leagues)
        print('Predictions done!')

        uploadFileAzure(cfg.PREDICTED_FPATH, cfg.AZURE_CONNECTION_STRING, cfg.AZURE_CONTAINER_NAME)
        print('Uploaded to Azure!')

if __name__ == "__main__":
    pipelineRun(
        leagues=cfg.LEAGUES,
        firstSeason=cfg.FIRST_SEASON, 
        firstSeasonTest=cfg.FIRST_SEASON_TEST, 
        lastSeason=cfg.LAST_SEASON, 
        downloadYN=False,
        preprocessYN=True,
        trainData=True,
        trainYN=True,
        predictYN=True,
    )