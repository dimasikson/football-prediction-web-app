# Football predictor web app

### Link: https://football-prediction-web-app.azurewebsites.net/

## 1. What is this?

This is a web app that helps to visualize football predictions and how each input variable affects the output. Below is an example of a match report. Each bar represents the marginal contribution of the corresponding variable on the output.

![](https://i.imgur.com/1DK65Mh.png)

## 2. How was it done?

### 2.1 Modelling

We use Gradient Boosted Regression Trees to predict the goal difference of a game, Home team goals [minus] Away team goals. Boosted trees are a great choice for this as it performs well with tabular data with non-linear interactions with the output. Below chart explains how the residuals of each tree are fed into each next tree, thus performing gradient boosting:

![](https://media.geeksforgeeks.org/wp-content/uploads/20200721214745/gradientboosting.PNG)

Source: https://www.geeksforgeeks.org/ml-gradient-boosting/

The algorithm also pairs well with the SHAP package which helps to explain each prediction by assigning marginal impact on the output to each input variable:

![](https://raw.githubusercontent.com/slundberg/shap/master/docs/artwork/shap_header.png)

Source: https://github.com/slundberg/shap

Below we can see the model performance in terms of accuracy and ROI:

![alt text](https://i.imgur.com/sKYeq3O.png)

All data taken from: https://www.football-data.co.uk/

### 2.2 Deployment

- Model training is done offline, inference is done daily with a scheduled data refresh
- Backend is done in Flask
- Frontend is done with vanilla JS, HTML, CSS
- Website hosted on Azure App Service, using Azure Blob Storage for storing data

## 3. Why was it done?

This web app is primarily for demonstration of data preprocessing, data modeling and some basic web development. The secondary purpose is to use it myself :)

## 4. Feature glossary

Below is an explanation for each feature in the model:
- Home/Draw/Away odds: European style odds for each outcome. If odds are 1.82 -> you pay 1.00 unit and receive 1.82 in case of a win.
- Goals + (H/A): Cumulative average goals scored
- Goals - (H/A): Cumulative average goals concered
- Conversion (H/A): Shot-to-goal conversion, Goals / Shots on target
- Accuracy (H/A): Shots on target / Shots
- Pts average (H/A): Cumulative average points obtained 
- Pts in last 3 (H/A): Average points in the last 3 games
- Table position (H/A): Position in the table, treated as a continuous variable
- Variance (H/A): Deviation of actual result from odds for each team. High variance means team has produced more surprising results, whether positive or negative 
