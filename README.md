# Football predictor web app

### Link: https://football-prediction-web-app.herokuapp.com/

## 1. The 'what?'

This is a web app that helps to visualize football predictions and how each input variable affects the output. Below is an example of a match report. Each bar represents the marginal contribution of the corresponding variable on the output.

![alt text](https://gyazo.com/a29cdca94b617367f1dd41bd3d8b8d10.png)

## 2. The 'how?'

We use XGBoost to predict the goal difference of a game, Home team goals [minus] Away team goals. XGB is a great choice for this as it performs well in regression tasks and pairs well with the SHAP package which helps to explain each prediction by assigning marginal impact on the output to each input variable.

Below we can see the model performance in terms of accuracy and ROI:

![alt text](https://gyazo.com/86db4e1a5eaec7c8bfc20a0abb40b004.png)

Link to analysis: https://colab.research.google.com/drive/1Jkmy8gR8LIC6vV9RNsECd5gec3Qnbjfx?usp=sharing

All data taken from: https://www.football-data.co.uk/

We then set up a daily "download -> preprocess -> predict -> save" routine to refresh the data.

Deployment done with Heroku and Gunicorn.

## 3. The 'why?'

This web app is primarily for demonstration of data preprocessing, data modeling and web development. The secondary purpose is to use it..
