from flask import Flask, redirect
from flask import render_template
from loginform import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
@app.route('/index')
def index():
    return render_template("/index.html")


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = LoginForm()
    print(form.username)
    if form.validate_on_submit():# and form.password == form.password2:
        print(0)
        return redirect('/success')
    print(1)
    return render_template('/registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('/login.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')