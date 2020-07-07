
from datetime import datetime
import pandas as pd


def cleanDate(obj, dtFormat=r'%Y-%m-%d'):

    year = obj.apply(lambda x: '20'+x.split('/')[2][-2:]) 
    month = obj.apply(lambda x: x.split('/')[1])
    day = obj.apply(lambda x: x.split('/')[0]) 

    obj = year + '-' + month + '-' + day
    return obj.apply(lambda x: datetime.strptime(x, dtFormat))


def loadData(leagues):

    trainDf = None

    for league in leagues:

        df = pd.read_csv('processedData/' + league + '.csv', engine='python')

        if trainDf is None:
            trainDf = df
        else:
            trainDf = trainDf.append(df)

    trainDf['Date'] = cleanDate(trainDf['Date'])

    return trainDf
