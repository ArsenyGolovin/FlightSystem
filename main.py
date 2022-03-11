from flask import Flask, redirect
from flask import render_template
from forms.user import *
from data import db_session
from data.users import User, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
@app.route('/index')
def index():
    return render_template("/index.html")


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    print(form.errors)
    print("Регистрация:", form.name.data, form.email.data, form.user_type.data)
    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            return render_template('registration.html', title='Регистрация',
                                   form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form, message="Эта почта уже занята")
        user = User(
            name=form.name.data,
            email=form.email.data,
            is_manager=(form.user_type.data == "manager")
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/manager') if user.is_manager else redirect('/client')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print("Вход:", form.email.data, form.password.data)
    if form.validate_on_submit():
        if not (f := db_sess.query(User).filter(User.email == form.email.data).first()):
            return render_template('login.html', title='Регистрация',
                                   form=form, message='Пользователь с этой почтой не найден')
        print(f)
        '''user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()'''
        return redirect('/manager') if user.is_manager else redirect('/client')
    return render_template('login.html', title='Вход', form=RegistrationForm())


if __name__ == '__main__':
    db_session.global_init("db/flights.db")
    app.run(port=8080, host='127.0.0.1')