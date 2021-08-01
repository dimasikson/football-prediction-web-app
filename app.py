from flask import Flask, render_template, url_for, request, redirect, session

from datetime import datetime
import string
import time
import datetime
import os

from update import pipelineRun
from utils import getUrlKwargs
from storage import downloadFileAzure
from config import Config as cfg

app = Flask(__name__)
app.secret_key = 'SECRET KEY'

downloadFileAzure(cfg.PREDICTED_FPATH, cfg.AZURE_CONNECTION_STRING, cfg.AZURE_CONTAINER_NAME)

@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

# hidden feature for emergency data refresh, /refreshData after URL
@app.route('/refreshData', methods=['POST','GET'])
def indexRefresh():

    # get args from url
    kwargs = getUrlKwargs(cfg.UPDATE_ARGS, request.args)

    pipelineRun(
        leagues=cfg.LEAGUES,
        firstSeason=cfg.FIRST_SEASON, 
        firstSeasonTest=cfg.FIRST_SEASON_TEST, 
        lastSeason=cfg.LAST_SEASON, 
        **kwargs,
    )
    return redirect('/')

if __name__ == "__main__":

    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True, use_reloader=False)