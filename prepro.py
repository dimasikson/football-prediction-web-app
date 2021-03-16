
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
                df = df.rename(columns={
                    'AvgH': 'BbAvH', 
                    'AvgD': 'BbAvD', 
                    'AvgA': 'BbAvA'
                })

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

            # COLUMN NAMING SYSTEM: T/H/A + statName + H/A
            # example: total goals for the season by the home team -> T_GoalsFor_H

            tableColumns = [
                # main table
                'T_GoalsFor', 'T_GoalsAg','T_GoalsForHT', 'T_GoalsAgHT','T_ShotsTaken', 'T_ShotsFaced','T_TShotsTaken', 'T_TShotsFaced',
                'T_Points','T_GamesPlayed','T_GoalDif','T_Variance'
            ]

            teams = df.loc[:, 'HomeTeam'].append(df.loc[:, 'AwayTeam'])

            table = {}

            for idx, team in enumerate(teams.sort_values().unique()):
                table[team] = {}
                table[team]['T_TablePosition'] = idx
                table[team]['Team'] = team

                for col in tableColumns:
                    table[team][col] = 0

            dfColumns = [
                #goals, all season
                'T_GamesPlayed_H','T_GamesPlayed_A',
                'T_GoalsFor_H','T_GoalsAg_H','T_GoalsFor_A','T_GoalsAg_A',
                'T_ShotsTaken_H','T_ShotsFaced_H','T_ShotsTaken_A','T_ShotsFaced_A',
                'T_TShotsTaken_H','T_TShotsFaced_H','T_TShotsTaken_A','T_TShotsFaced_A',
                'T_Points_H','T_Points_A',
                'T_TablePosition_H','T_TablePosition_A',
                'T_GoalsForHT_H','T_GoalsAgHT_H','T_GoalsForHT_A','T_GoalsAgHT_A',
                'T_Variance_H','T_Variance_A',
                'L3M_Points_H', 'L3M_Points_A'
            ]

            computedVals = {}

            for col in dfColumns:
                computedVals[col] = []

            qPoints = {j: [] for j in teams.unique().tolist()}

            for _, tempDfRow in df.iterrows():
                tempDfRow = {k:v for k, v in zip(tempDfRow.index, tempDfRow)}
                HTeam = tempDfRow['HomeTeam']
                ATeam = tempDfRow['AwayTeam']
                
                tempTableHome = table[HTeam]
                tempTableAway = table[ATeam]

                # update df for home team
                if tempTableHome['T_GamesPlayed'] > 0:

                    cols = ['GoalsFor', 'GoalsAg', 'GoalsForHT', 'GoalsAgHT', 'ShotsTaken', 'TShotsTaken', 'ShotsFaced', 'TShotsFaced', 'Points', 'Variance']
                    for col in cols:
                        computedVals['T_' + col + '_H'].append(tempTableHome['T_' + col] / tempTableHome['T_GamesPlayed'])

                    cols = ['TablePosition']
                    for col in cols:
                        computedVals['T_' + col + '_H'].append(tempTableHome['T_' + col])
                else:
                    cols = ['GoalsFor', 'GoalsAg', 'GoalsForHT', 'GoalsAgHT', 'ShotsTaken', 'TShotsTaken', 'ShotsFaced', 'TShotsFaced', 'Points', 'Variance', 'TablePosition']
                    for col in cols:
                        computedVals['T_' + col + '_H'].append(None)

                computedVals['T_GamesPlayed_H'].append(tempTableHome['T_GamesPlayed'])

                # update df for away team
                if tempTableAway['T_GamesPlayed'] > 0:

                    cols = ['GoalsFor', 'GoalsAg', 'GoalsForHT', 'GoalsAgHT', 'ShotsTaken', 'TShotsTaken', 'ShotsFaced', 'TShotsFaced', 'Points', 'Variance']
                    for col in cols:
                        computedVals['T_' + col + '_A'].append(tempTableAway['T_' + col] / tempTableAway['T_GamesPlayed'])

                    cols = ['TablePosition']
                    for col in cols:
                        computedVals['T_' + col + '_A'].append(tempTableAway['T_' + col])
                else:
                    cols = ['GoalsFor', 'GoalsAg', 'GoalsForHT', 'GoalsAgHT', 'ShotsTaken', 'TShotsTaken', 'ShotsFaced', 'TShotsFaced', 'Points', 'Variance', 'TablePosition']
                    for col in cols:
                        computedVals['T_' + col + '_A'].append(None)

                computedVals['T_GamesPlayed_A'].append(tempTableAway['T_GamesPlayed'])

                # unpack L6H_Goals
                if tempTableHome['T_GamesPlayed'] >= 3 and tempTableAway['T_GamesPlayed'] >= 3:
                    computedVals['L3M_Points_H'].append(np.mean(qPoints[HTeam][-3:]))
                    computedVals['L3M_Points_A'].append(np.mean(qPoints[ATeam][-3:]))
                else:
                    computedVals['L3M_Points_H'].append(None)
                    computedVals['L3M_Points_A'].append(None)

                # calculate variance of result
                hBin = 1 if tempDfRow['FTR'] == 'H' else 0
                dBin = 1 if tempDfRow['FTR'] == 'D' else 0
                aBin = 1 if tempDfRow['FTR'] == 'A' else 0

                hVariance = hBin - 1 / ( tempDfRow['HomeOdds'] * 20 )
                dVariance = dBin - 1 / ( tempDfRow['DrawOdds'] * 20 )
                aVariance = aBin - 1 / ( tempDfRow['AwayOdds'] * 20 )

                resultVariance = ( hVariance ** 2 + dVariance ** 2 + aVariance ** 2 ) / 3

                # update table for home team
                tempTableHome['T_GamesPlayed'] += 1

                cols = ['GoalsFor', 'ShotsTaken', 'TShotsTaken', 'Points']
                for col in cols:
                    tempTableHome['T_' + col] += tempDfRow[col + '_H']

                tempTableHome['T_GoalsAg'] += tempDfRow['GoalsFor_A']
                tempTableHome['T_ShotsFaced'] += tempDfRow['ShotsTaken_A']
                tempTableHome['T_TShotsFaced'] += tempDfRow['TShotsTaken_A']

                tempTableHome['T_GoalsForHT'] += tempDfRow['GoalsForHT_H']
                tempTableHome['T_GoalsAgHT'] += tempDfRow['GoalsForHT_A']
                tempTableHome['T_Variance'] += resultVariance

                # update table for away team
                tempTableAway['T_GamesPlayed'] += 1

                cols = ['GoalsFor', 'ShotsTaken', 'TShotsTaken', 'Points']
                for col in cols:
                    tempTableAway['T_' + col] += tempDfRow[col + '_A']

                tempTableAway['T_GoalsAg'] += tempDfRow['GoalsFor_H']
                tempTableAway['T_ShotsFaced'] += tempDfRow['ShotsTaken_H']
                tempTableAway['T_TShotsFaced'] += tempDfRow['TShotsTaken_H']

                tempTableAway['T_GoalsForHT'] += tempDfRow['GoalsForHT_A']
                tempTableAway['T_GoalsAgHT'] += tempDfRow['GoalsForHT_H']
                tempTableAway['T_Variance'] += resultVariance

                # update qPoints
                qPoints[HTeam].append(tempDfRow['Points_H'])
                qPoints[ATeam].append(tempDfRow['Points_A'])

                # sort table + update T_TablePosition

                table[HTeam] = tempTableHome
                table[ATeam] = tempTableAway

                for team in table:
                    table[team]['T_GoalDif'] = table[team]['T_GoalsFor'] - table[team]['T_GoalsAg']

                sortedTeams = sorted(table, key = lambda k: (
                    -table[k]['T_Points'], # negative for descending order
                    -table[k]['T_GoalDif'], 
                    -table[k]['T_GoalsFor'], 
                    table[k]['Team']
                ))

                for idx, team in enumerate(sortedTeams):
                    table[team]['T_TablePosition'] = idx+1

            for k, v in computedVals.items():
                df.loc[:, k] = v

            # additional features
            for ha in ['H', 'A']:
                df.loc[:, f'T_Conversion_{ha}'] = df.loc[:, f'T_GoalsFor_{ha}'] / df.loc[:, f'T_TShotsTaken_{ha}']
                df.loc[:, f'T_Accuracy_{ha}'] = df.loc[:, f'T_TShotsTaken_{ha}'] / df.loc[:, f'T_ShotsTaken_{ha}']

                df.loc[:, f'T_Conversion_{ha}'] = np.clip(df.loc[:, f'T_Conversion_{ha}'],0,1)
                df.loc[:, f'T_Accuracy_{ha}'] = np.clip(df.loc[:, f'T_Accuracy_{ha}'],0,1)

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


