from flask import Flask, render_template, url_for, request, redirect, session

app = Flask(__name__)
app.secret_key = 'SECRET KEY'

@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True, use_reloader=False)
