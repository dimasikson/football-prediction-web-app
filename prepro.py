
import numpy as np
import pandas as pd
import sys
import wget
import os
import math
from hyperparams import Hyperparams as hp

def downloadFiles(firstSeason, firstSeasonTest, lastSeason, train, leagues):

    fixtFpath = 'rawFiles/test/fixtures.csv'
    if os.path.exists(fixtFpath):
        os.remove(fixtFpath)

    wget.download(
        r'https://www.football-data.co.uk/fixtures.csv', 
        fixtFpath
    )

    for league in leagues:

        firstSeasonLeague = max(firstSeason, leagues[league])

        if train==False:
            firstSeasonLeague = firstSeasonTest

        for i in range(firstSeasonLeague, lastSeason+1):

            yearStart = '0' + str(i)
            yearEnd = '0' + str(i+1)

            season = yearStart[-2:] + yearEnd[-2:]

            url = r'https://www.football-data.co.uk/mmz4281/' + season + '/' + league + '.csv'

            filename = league + '-' + season
            print(filename)


            if i >= firstSeasonTest:
                fpath = 'rawFiles/test/' + filename + '.csv'

            else:
                fpath = 'rawFiles/train/' + filename + '.csv'

            if os.path.exists(fpath):
                os.remove(fpath)

            wget.download(url, fpath)

            df = pd.read_csv(fpath, engine='python')
            df = df.loc[df['FTHG'] == df['FTHG']]
            df.to_csv(fpath)


# downloadFiles()

def preProcess(firstSeason, firstSeasonTest, lastSeason, train, leagues):

    for league in leagues:

        trainDfNone, testDfNone = True, True

        firstSeasonLeague = max(firstSeason, leagues[league])

        if train==False:
            firstSeasonLeague = firstSeasonTest

        for i in range(firstSeasonLeague, lastSeason+1):

            yearStart = '0' + str(i)
            yearEnd = '0' + str(i+1)
            season = yearStart[-2:] + yearEnd[-2:]
            filename = league + '-' + season
            print(filename)

            if i >= firstSeasonTest:
                folder = 'test'

            else:
                folder = 'train'

            fpath = f'rawFiles/{folder}/{filename}.csv'

            df = pd.read_csv(fpath, engine='python')

            if i == lastSeason:
                # read fixtures
                fixtures = pd.read_csv('rawFiles/test/fixtures.csv', engine='python')

                fixtures = fixtures.loc[fixtures.loc[:, 'Div']==league, :]

                fixtures.index = range(len(fixtures))

                for row in range(len(fixtures)):
                    tmp = df.loc[
                        (df.loc[:, 'Div']==fixtures.loc[:, 'Div'][row]) &
                        (df.loc[:, 'HomeTeam']==fixtures.loc[:, 'HomeTeam'][row]) &
                        (df.loc[:, 'AwayTeam']==fixtures.loc[:, 'AwayTeam'][row])
                    ,:]

                    if len(tmp) == 0:
                        df = df.append(fixtures.iloc[row, :])

            if i >= 19:
                df = df.rename(columns={'AvgH': 'BbAvH', 'AvgD': 'BbAvD', 'AvgA': 'BbAvA'})

            df = df[[
                'Div',
                'Date',
                'HomeTeam', 'AwayTeam',
                'FTHG', 'FTAG',
                'HTHG', 'HTAG',
                'FTR', 'HTR',
                'HS', 'AS',
                'HST', 'AST',
                'BbAvH', 'BbAvD', 'BbAvA'
                ]]

            df.columns = [
                    'Div',
                    'Date',
                    'HomeTeam', 'AwayTeam',
                    'GoalsFor_H', 'GoalsFor_A',
                    'GoalsForHT_H', 'GoalsForHT_A',
                    'FTR', 'HTR',
                    'ShotsTaken_H', 'ShotsTaken_A',
                    'TShotsTaken_H', 'TShotsTaken_A',
                    'HomeOdds', 'DrawOdds', 'AwayOdds'
                ]

            for col in ['HomeOdds', 'DrawOdds', 'AwayOdds', 'ShotsTaken_H', 'ShotsTaken_A','TShotsTaken_H', 'TShotsTaken_A']:
                df[col] = df[col].apply(lambda x: 1. if x > 20 else x/20)

            for col in ['GoalsFor_H', 'GoalsFor_A','GoalsForHT_H', 'GoalsForHT_A']:
                df[col] = df[col].apply(lambda x: 1. if x > 10 else x/10)

            df['Points_H'] = df['FTR'].apply(lambda x: 1. if x == 'H' else (1/3 if x == 'D' else 0))
            df['Points_A'] = df['FTR'].apply(lambda x: 1. if x == 'A' else (1/3 if x == 'D' else 0))

            table = pd.DataFrame(df.HomeTeam.sort_values().unique(), columns=['Team'])

            table['T_TablePosition'] = np.arange(len(table.Team))+1

            # COLUMN NAMING SYSTEM: T/H/A + statName + H/A
            # example: total goals for the season by the home team -> T_GoalsFor_H

            tableColumns = [
                # main table
                'T_GoalsFor', 'T_GoalsAg','T_GoalsForHT', 'T_GoalsAgHT','T_ShotsTaken', 'T_ShotsFaced','T_TShotsTaken', 'T_TShotsFaced',
                'T_Points','T_GamesPlayed','T_GoalDif','T_VAR',
                'H_GoalsFor', 'H_GoalsAg','H_ShotsTaken', 'H_ShotsFaced','H_TShotsTaken', 'H_TShotsFaced','H_Points','H_GamesPlayed', 'H_VAR',
                'A_GoalsFor', 'A_GoalsAg','A_ShotsTaken', 'A_ShotsFaced','A_TShotsTaken', 'A_TShotsFaced','A_Points','A_GamesPlayed', 'A_VAR'
            ]

            for col in tableColumns:
                table[col] = 0

            dfColumns = [
                #goals, all season
                'T_GamesPlayed_H','T_GamesPlayed_A',
                'T_GoalsFor_H','T_GoalsAg_H','T_GoalsFor_A','T_GoalsAg_A',
                'T_ShotsTaken_H','T_ShotsFaced_H','T_ShotsTaken_A','T_ShotsFaced_A',
                'T_TShotsTaken_H','T_TShotsFaced_H','T_TShotsTaken_A','T_TShotsFaced_A',
                'T_Points_H','T_Points_A',
                'T_TablePosition_H','T_TablePosition_A',
                'T_GoalsForHT_H','T_GoalsAgHT_H','T_GoalsForHT_A','T_GoalsAgHT_A',
                'T_VAR_H','T_VAR_A',
                'H_GoalsFor_H','H_GoalsAg_H','H_ShotsTaken_H','H_ShotsFaced_H','H_TShotsTaken_H','H_TShotsFaced_H','H_Points_H','H_VAR_H',
                'A_GoalsFor_A','A_GoalsAg_A','A_ShotsTaken_A','A_ShotsFaced_A','A_TShotsTaken_A','A_TShotsFaced_A','A_Points_A','A_VAR_A',
                'L3M_Points_H', 'L3M_Points_A'
            ]

            for col in dfColumns:
                df[col] = 0

            df['L3M_Points_H'] = 0
            df['L3M_Points_A'] = 0

            qPoints = {j: [] for j in df.HomeTeam.unique().tolist()}

            for row in range(len(df)):

                if row % 10 == 0:
                    print(row)

                HTeam = df['HomeTeam'].iloc[row]
                ATeam = df['AwayTeam'].iloc[row]

                tempDfRow = df.iloc[row]
                tempTableHome = table[table['Team']==HTeam]
                tempTableAway = table[table['Team']==ATeam]

                # update df for home team
                if tempTableHome['T_GamesPlayed'].values[0] > 0:

                    cols = ['GoalsFor', 'GoalsAg', 'GoalsForHT', 'GoalsAgHT', 'ShotsTaken', 'TShotsTaken', 'ShotsFaced', 'TShotsFaced', 'Points', 'VAR']
                    for col in cols:
                        tempDfRow['T_' + col + '_H'] = tempTableHome['T_' + col].values[0] / tempTableHome['T_GamesPlayed'].values[0]

                    cols = ['TablePosition']
                    for col in cols:
                        tempDfRow['T_' + col + '_H'] = tempTableHome['T_' + col].values[0]

                    if table[table['Team']==HTeam]['H_GamesPlayed'].values[0] > 0:
                        cols = ['GoalsFor', 'GoalsAg', 'ShotsTaken', 'TShotsTaken', 'ShotsFaced', 'TShotsFaced', 'Points', 'VAR']
                        for col in cols:
                            tempDfRow['H_' + col + '_H'] = tempTableHome['H_' + col].values[0] / tempTableHome['H_GamesPlayed'].values[0]

                tempDfRow['T_GamesPlayed_H'] = tempTableHome['T_GamesPlayed'].values[0]

                # update df for away team
                if tempTableAway['T_GamesPlayed'].values[0] > 0:

                    cols = ['GoalsFor', 'GoalsAg', 'GoalsForHT', 'GoalsAgHT', 'ShotsTaken', 'TShotsTaken', 'ShotsFaced', 'TShotsFaced', 'Points', 'VAR']
                    for col in cols:
                        tempDfRow['T_' + col + '_A'] = tempTableAway['T_' + col].values[0] / tempTableAway['T_GamesPlayed'].values[0]

                    cols = ['TablePosition']
                    for col in cols:
                        tempDfRow['T_' + col + '_A'] = tempTableAway['T_' + col].values[0]

                    if tempTableAway['A_GamesPlayed'].values[0] > 0:
                        cols = ['GoalsFor', 'GoalsAg', 'ShotsTaken', 'TShotsTaken', 'ShotsFaced', 'TShotsFaced', 'Points', 'VAR']
                        for col in cols:
                            tempDfRow['A_' + col + '_A'] = tempTableAway['A_' + col].values[0] / tempTableAway['A_GamesPlayed'].values[0]

                tempDfRow['T_GamesPlayed_A'] = tempTableAway['T_GamesPlayed'].values[0]

                # unpack L6H_Goals
                if tempTableHome['T_GamesPlayed'].values[0] >= 3 and tempTableAway['T_GamesPlayed'].values[0] >= 3:
                    tempDfRow['L3M_Points_H'] = np.mean(qPoints[HTeam][-3:])
                    tempDfRow['L3M_Points_A'] = np.mean(qPoints[ATeam][-3:])

                # update table for home team
                tempTableHome['T_GamesPlayed'] += 1
                tempTableHome['H_GamesPlayed'] += 1

                cols = ['GoalsFor', 'ShotsTaken', 'TShotsTaken', 'Points']
                for col in cols:
                    tempTableHome['T_' + col] += tempDfRow[col + '_H']
                    tempTableHome['H_' + col] += tempDfRow[col + '_H']

                tempTableHome['T_GoalsAg'] += tempDfRow['GoalsFor_A']
                tempTableHome['T_ShotsFaced'] += tempDfRow['ShotsTaken_A']
                tempTableHome['T_TShotsFaced'] += tempDfRow['TShotsTaken_A']

                tempTableHome['T_GoalsForHT'] += tempDfRow['GoalsForHT_H']
                tempTableHome['T_GoalsAgHT'] += tempDfRow['GoalsForHT_A']

                tempTableHome['H_GoalsAg'] += tempDfRow['GoalsFor_A']
                tempTableHome['H_ShotsFaced'] += tempDfRow['ShotsTaken_A']
                tempTableHome['H_TShotsFaced'] += tempDfRow['TShotsTaken_A']

                # update table for away team
                tempTableAway['T_GamesPlayed'] += 1
                tempTableAway['A_GamesPlayed'] += 1

                cols = ['GoalsFor', 'ShotsTaken', 'TShotsTaken', 'Points']
                for col in cols:
                    tempTableAway['T_' + col] += tempDfRow[col + '_A']
                    tempTableAway['A_' + col] += tempDfRow[col + '_A']

                tempTableAway['T_GoalsAg'] += tempDfRow['GoalsFor_H']
                tempTableAway['T_ShotsFaced'] += tempDfRow['ShotsTaken_H']
                tempTableAway['T_TShotsFaced'] += tempDfRow['TShotsTaken_H']

                tempTableAway['T_GoalsForHT'] += tempDfRow['GoalsForHT_A']
                tempTableAway['T_GoalsAgHT'] += tempDfRow['GoalsForHT_H']

                tempTableAway['A_GoalsAg'] += tempDfRow['GoalsFor_H']
                tempTableAway['A_ShotsFaced'] += tempDfRow['ShotsTaken_H']
                tempTableAway['A_TShotsFaced'] += tempDfRow['TShotsTaken_H']

                # update qPoints
                qPoints[HTeam].append(tempDfRow['Points_H'])
                qPoints[ATeam].append(tempDfRow['Points_A'])

                # sort table + update T_TablePosition

                df.iloc[row] = tempDfRow
                table[table['Team']==HTeam] = tempTableHome
                table[table['Team']==ATeam] = tempTableAway

                table['T_GoalDif'] = table['T_GoalsFor'] - table['T_GoalsAg']

                table = table.sort_values(['T_Points', 'T_GoalDif', 'T_GoalsFor', 'Team'], ascending=[False,False,False,True])
                table['T_TablePosition'] = np.arange(len(table.Team))+1

            if i < firstSeasonTest:
                if trainDfNone:
                    trainDf = df
                    trainDfNone = False

                else:
                    trainDf = trainDf.append(df)

            else:
                if testDfNone:
                    testDf = df
                    testDfNone = False

                else:
                    testDf = testDf.append(df)


        if train:

            trainDf.index = range(len(trainDf))

            fpath = f'processedData/train_{league}.csv'

            if os.path.exists(fpath):
                os.remove(fpath)

            trainDf.to_csv(fpath)

        testDf.index = range(len(testDf))

        fpath = f'processedData/test_{league}.csv'

        if os.path.exists(fpath):
            os.remove(fpath)

        testDf.to_csv(fpath)


# preProcess()


