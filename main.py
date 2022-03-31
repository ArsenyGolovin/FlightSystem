import datetime
import logging

from flask import Flask, redirect
from flask import render_template
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from data import db_session, airports, planes, flights, statuses
from data.users import User, check_password_hash
from forms.add_flight import AddFlightForm
from forms.add_plane import AddPlaneForm
from forms.user import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', level=0)

CREATING_FLIGHT_TD = datetime.timedelta(hours=2)
BOARDING_TD = datetime.timedelta(minutes=40)


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
            return render_template('registration.html', form=form, message='Пароли не совпадают')

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            logging.warning(f'Регистрация: Почта {form.email.data} уже занята')
            return render_template('registration.html', form=form, message='Эта почта уже занята')

        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.is_manager = form.user_type.data == 'manager'
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        logging.info(f'Регистрация: {form.name.data} {form.email.data} {form.user_type.data}')
        logging.info(f'Регистрация: Текущий пользователь - {form.email.data}')
        login_user(user)
        return redirect('/manager') if user.is_manager else redirect('/client')
    logging.warning(f'Регистрация: Форма не прошла валидацию: {form.errors}')
    return render_template('registration.html', form=form, message='Форма не прошла валидацию')


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
            return render_template('login.html', form=form, message='Неверный пароль')
        login_user(user)
        logging.info(f'Вход: Текущий пользователь - {current_user.email}')
        return redirect('/manager') if user.is_manager else redirect('/client')
    logging.info(f'Вход: Форма не прошла валидацию: {form.errors}')
    return render_template('login.html', form=LoginForm(), message='Форма не прошла валидацию')


@app.route('/logout')
@login_required
def logout():
    logging.info(f'Выход: Пользователь - {current_user.email}')
    logout_user()
    return redirect("/")


@app.route('/manager')
def manager():
    return render_template('manager.html')


@app.route('/manager/airports')
def manager_airports():
    return render_template('airports.html', table=db_session.create_session().query(airports.Airport))


@app.route('/manager/planes')
def manager_planes():
    return render_template('manager_planes.html', table=db_session.create_session().query(planes.Plane))


@app.route('/manager/add_plane', methods=['GET', 'POST'])
def manager_add_plane():
    form = AddPlaneForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(planes.Plane).filter(planes.Plane.name == form.name.data).first():
            logging.warning(f'Самолёты: самолёт {form.name.data} уже в базе данных')
            return render_template('manager_add_plane.html', form=form,
                                   message=f'Самолёт {form.name.data} уже в списке')
        plane = planes.Plane()
        plane.name = form.name.data
        plane.rows_num = form.rows_num.data
        plane.columns_num = form.columns_num.data
        plane.flight_cost_per_1000_km = form.flight_cost_per_1000_km.data
        plane.average_speed = form.average_speed.data
        db_sess.add(plane)
        db_sess.commit()
        logging.info(f'Самолёты: Самолёт {form.name.data} добавлен в базу данных')
        return render_template(f'manager_planes.html', message=f'Самолёт {form.name.data} добавлен в список',
                               table=db_session.create_session().query(planes.Plane))
    logging.warning(f'Самолёты: Форма не прошла валидацию: {form.errors}')
    return render_template('manager_add_plane.html', form=form, message='Форма не прошла валидацию')


@app.route('/manager/flights')
def manager_flights():
    db_sess = db_session.create_session()
    return render_template('manager_flights.html', table1=db_sess.query(airports.Airport, flights.Flight),
                           table2=db_sess.query(flights.Flight, planes.Plane, statuses.Status).filter(
                               flights.Flight.plane_id == planes.Plane.id,
                               flights.Flight.status_id == statuses.Status.id))


@app.route('/manager/add_flight', methods=['GET', 'POST'])
def manager_add_flight():
    form = AddFlightForm()
    if form.validate_on_submit():
        dept_datetime = datetime.datetime.strptime(form.dept_datetime.data, '%d.%m.%Y %H:%M')
        if dept_datetime - datetime.datetime.now() < datetime.timedelta(hours=2):
            logging.warning(f'Рейсы: Рейс можно создать минимум за 2 часа до взлёта')
            return render_template('manager_add_flight.html', form=form,
                                   message='Рейс можно создать минимум за 2 часа до взлёта')

        db_sess = db_session.create_session()
        if not db_sess.query(airports.Airport).filter(airports.Airport.city == form.dept_city.data,
                                                      airports.Airport.name == form.dept_airport.data).first():
            logging.warning(f'Рейсы: Аэропорт {form.dept_city.data}, {form.dept_airport.data} не найден')
            return render_template('manager_add_flight.html', form=form,
                                   message=f'Аэропорт {form.dept_city.data}, {form.dept_airport.data} не найден')

        if not db_sess.query(airports.Airport).filter(airports.Airport.city == form.dest_city.data,
                                                      airports.Airport.name == form.dest_airport.data).first():
            logging.warning(f'Рейсы: Аэропорт {form.dest_city.data}, {form.dest_airport.data} не найден')
            return render_template('manager_add_flight.html', form=form,
                                   message=f'Аэропорт {form.dept_city.data}, {form.dept_airport.data} не найден')

        if not db_sess.query(planes.Plane).filter(planes.Plane.name == form.plane.data).first():
            logging.warning(f'Рейсы: Самолёт {form.plane.data} не найден')
            return render_template('manager_add_flight.html', form=form,
                                   message=f'Самолёт {form.plane.data} не найден')

        flight = flights.Flight()
        flight.dept_airport_id = db_sess.query(airports.Airport).filter(airports.Airport.city == form.dept_city.data,
                                                                        airports.Airport.name == form.dept_airport.data
                                                                        ).first().id
        flight.dest_airport_id = db_sess.query(airports.Airport).filter(airports.Airport.city == form.dest_city.data,
                                                                        airports.Airport.name == form.dest_airport.data
                                                                        ).first().id
        flight.plane_id = db_sess.query(planes.Plane).filter(planes.Plane.name == form.plane.data).first().id
        flight.dept_datetime = dept_datetime
        flight.dest_datetime = datetime.datetime.now() + datetime.timedelta(hours=3)
        flight.price = 0
        db_sess.add(flight)
        db_sess.commit()
        logging.info(f'Рейсы: Рейс добавлен')
        return render_template('manager_add_flight.html', form=form, message='Рейс добавлен')
    logging.warning(f'Рейсы: Форма не прошла валидацию: {form.errors}')
    return render_template('manager_add_flight.html', form=form, message='Форма не прошла валидацию')


@app.route('/client')
def client():
    return render_template('/client.html')


if __name__ == '__main__':
    db_session.global_init("db/flights.db")
    app.run(port=8080, host='127.0.0.1')
