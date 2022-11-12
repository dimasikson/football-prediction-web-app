# Football predictor web app

### Link: https://football-prediction-web-app.azurewebsites.net/

## 1. What is this project?

This project aims to predict football results and explain the predictions. Those things are done using `XGBoost` and `SHAP` respectively. There is also a `streamlit` app to visualize / track performance.

### Front page:

<img width="535" alt="image" src="https://user-images.githubusercontent.com/47122797/201469493-bb60bee7-047c-4293-a75a-6868271993d9.png">

### Match page:

<img width="536" alt="image" src="https://user-images.githubusercontent.com/47122797/201469516-53900aa8-0f02-403b-8718-eaba00a9b8de.png">

## 2. How was it done?

### 2.1 Gathering data & storage

Initial data is taken from: https://www.football-data.co.uk/

Data is then enriched with features, mainly consisting of stats (goals, shots, fouls, etc.). It is tricky to reconstruct what the table looked like before the game, for that I made a `LeagueTable` class. Check out `src/preprocess/features.py` for more detail.

For storage I use Azure Blob. I wrote common read/write methods to simplify data management, check out `src/storage/tables.py` for more detail.

### 2.2 Model choice

I used `XGBoost` as it's a highly performing algorithm on tabular data. It also handles missing data well, which is important as in this project there are naturally some missing features which should not be imputed (at the start of the season, all statistics are empty for each team).

![image](https://user-images.githubusercontent.com/47122797/201469876-32d7f46c-918c-40b8-8aac-d6fb1dc94240.png)

Source: https://towardsdatascience.com/https-medium-com-vishalmorde-xgboost-algorithm-long-she-may-rein-edd9f99be63d

### 2.3 Training & hyperparameter experiment

I used `hyperopt` to optimize the model. It accepts any abstract objective function with the following form `f(X) -> y` where `y` is a float, but I used a standard RMSE output to optimize the model. Please check out `train.ipynb` and `src/modelling/experiment.py` for more detail.

NOTE: Training is fully offline & local. Eventually I want to move to Azure ML / Synapse but for now that's too much work for a pet project :^)

<img width="739" alt="image" src="https://user-images.githubusercontent.com/47122797/201470160-5cd6d3c9-d131-4076-9f20-10eeffbca266.png">

### 2.4 Explaning predictions

XGBoost also pairs well with the `SHAP` package which helps to explain each prediction by assigning marginal impact on the output to each input variable. To be perfectly honest, this part of the project has been underwhelming as most of the variation in the predictions are usually explained by the odds.

![](https://raw.githubusercontent.com/slundberg/shap/master/docs/artwork/shap_header.png)

Source: https://github.com/slundberg/shap

### 2.5 Frontend

Frontend was done with `streamlit`, I would highly recommend it for anyone who hates doing frontend as much as I do. Really easy to use. Pretty limited framework but that's the point. A previous version of this project used the normal JS/CSS/HTML stack and I hated it so much.

### 2.6 Deployment

Deployment is done with Azure App Service + Github Actions for CI/CD.

## 3. How to re-deploy (notes for future me)

### 3.0 [Setup] How to set up App Service + GH Actions

It's straightforward, just don't forget to specify the startup command in the portal.

### 3.1 Re-deploy web-app

- Commit / merge to master.
- Wait for build & release to come through.
- [OPTIONAL] Restart application from portal.

### 3.2 Set up data refresh

- SSH into the VM in the portal
- Run `crontab -e` and press `2`
- Add the following cron expressions:
  - `*/10 * * * * date > /tmp/test.txt` (TODO: determine if this is even needed, but for now I'm using it to keep the app alive)
  - `0 0 * * 3,6 {full_python_path} run_pipelines.py` (3 and 6 denotes Wednesday and Saturday, approximately when the fixtures get refreshed)
- NOTE: cron needs absolute paths for everything. You can get `{full_python_path}` by running `which python`
- TODO: can these steps be automated?
- TODO: set up occasional model re-training in Azure ML / Synapse and do away with this cron scheduling
