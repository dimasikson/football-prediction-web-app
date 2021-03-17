from flask import Flask, render_template, url_for, request, redirect, session

from datetime import datetime
import string
import time
import datetime
import os

from update import updatePredictions
from storage import downloadFileAzure, AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME, PREDICTED_FPATH

app = Flask(__name__)
app.secret_key = 'SECRET KEY'

downloadFileAzure(PREDICTED_FPATH, AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME)

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

@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

# hidden feature for emergency data refresh, /refreshData after URL
@app.route('/refreshData', methods=['POST','GET'])
def indexRefresh():
    updatePredictions(
        download=True,
        preprocess=True, 
        predictYN=True, 
        leagues=leagues,
        firstSeason=firstSeason, 
        firstSeasonTest=firstSeasonTest, 
        lastSeason=lastSeason, 
        train=False
    )
    return redirect('/')

if __name__ == "__main__":

    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True, use_reloader=False)