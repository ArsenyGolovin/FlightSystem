from flask import Flask
from flask import render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
@app.route('/index')
def index():
    return render_template("/index.html")


@app.route('/registration')
def registration():
    return render_template('/registration.html')


@app.route('/login')
def login():
    return render_template('/login.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')