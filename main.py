import logging

from flask import Flask, redirect
from flask import render_template
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from data import db_session
from data.users import User, check_password_hash
from forms.user import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', level=1)


@app.route('/')
@app.route('/index')
def index():
    return render_template('/index.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            logging.warning('Регистрация: Пароли не совпадают')
            return render_template('registration.html', title='Регистрация',
                                   form=form, message='Пароли не совпадают')

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            logging.warning(f'Регистрация: Почта {form.email.data} уже занята')
            return render_template('registration.html', title='Регистрация', form=form, message='Эта почта уже занята')
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.is_manager = form.user_type.data == 'manager'
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        logging.info(f'Регистрация: {form.name.data} {form.email.data} {form.user_type.data}')
        logging.info(f'Регистрация: Текущий пользователь - {current_user.email}')
        login_user(user)
        return redirect('/manager') if user.is_manager else redirect('/client')
    logging.warning(f'Регистрация: Форма не прошла валидацию: {form.errors}')
    return render_template('registration.html', title='Регистрация', form=form, message='Форма не прошла валидацию')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        if not (user := db_sess.query(User).filter(User.email == form.email.data).first()):
            logging.warning(f'Вход: Пользователь с почтой {form.email.data} не найден:')
            return render_template('login.html', title='Вход', form=form,
                                   message='Пользователь с этой почтой не найден')
        if check_password_hash(user.hashed_password, form.password.data):
            logging.warning('Вход: Неверный пароль')
            return render_template('login.html', title='Вход', form=form, message='Неверный пароль')
        login_user(user)
        logging.info(f'Вход: Текущий пользователь - {current_user.email}')
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
    logging.info(f'Выход: Пользователь - {current_user.email}')
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/flights.db")
    app.run(port=8080, host='127.0.0.1')
