from flask import Flask, redirect
from flask import render_template
from forms.user import *
from data import db_session
from data.users import User, check_password_hash
from flask_login import LoginManager, login_required, login_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
@app.route('/index')
def index():
    return render_template("/index.html")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            print(f'Регистрация: Пароли не совпадают')
            return render_template('registration.html', title='Регистрация',
                                   form=form, message="Пароли не совпадают")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            print(f'Регистрация: Почта {form.email.data} уже занята')
            return render_template('registration.html', title='Регистрация',
                                   form=form, message="Эта почта уже занята")
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.is_manager = form.user_type.data == "manager"
        user.set_password(form.password.data)
        print("Регистрация:", form.name.data, form.email.data, form.user_type.data)
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        print("Регистрация:", form.name.data, form.email.data, form.user_type.data)
        print(current_user)
        return redirect('/manager') if user.is_manager else redirect('/client')
    print(f'Регистрация: Форма не прошла валидацию: {form.errors}')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        if not (user := db_sess.query(User).filter(User.email == form.email.data).first()):
            print(f'Вход: Пользователь с этой почтой не найден: {form.email.data}')
            return render_template('login.html', title='Вход',
                                   form=form, message='Пользователь с этой почтой не найден')
        if check_password_hash(user.hashed_password, form.password.data):
            print(f'Вход: Неверный пароль')
            return render_template('login.html', title='Вход',
                                   form=form, message='Неверный пароль')
        print("Вход:", form.email.data)
        print(user)
        login_user(user)
        return redirect('/manager') if user.is_manager else redirect('/client')
    return render_template('login.html', title='Вход', form=LoginForm())


@app.route('/client')
def client():
    return render_template('client.html')


@app.route('/manager')
def manager():
    return render_template('manager.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/flights.db")
    app.run(port=8080, host='127.0.0.1')