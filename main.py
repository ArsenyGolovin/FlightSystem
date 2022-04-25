import datetime
import logging
import sqlite3
from math import sin, cos, atan2, pi

import requests
from flask import Flask, redirect
from flask import render_template, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from data import db_session, airports, planes, flights, statuses, tickets
from data.users import User, check_password_hash
from forms.flights import AddFlightForm, DelayFlightForm, CancelFlightForm
from forms.planes import AddPlaneForm, DeletePlaneForm
from forms.tickets import BuyTicketForm, ReturnTicketForm
from forms.user import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
con = sqlite3.connect('db/flights.db', check_same_thread=False)
cur = con.cursor()
login_manager = LoginManager()
login_manager.init_app(app)
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', level=0)

YANDEX_GEOCODER_APIKEY = "40d1649f-0493-4b70-98ba-98533de7710b"
CREATING_FLIGHT_TD = datetime.timedelta(hours=2)


def calculate_earth_distance(lat1: float, long1: float, lat2: float, long2: float) -> float:
    EARTH_RADIUS = 6372795
    sin_lat1, sin_lat2 = sin(lat1 * pi / 180), sin(lat2 * pi / 180)
    cos_lat1, cos_lat2 = cos(lat1 * pi / 180), cos(lat2 * pi / 180)
    sin_delta, cos_delta = sin(long2 * pi / 180 - long1 * pi / 180), cos(long2 * pi / 180 - long1 * pi / 180)
    x = sin_lat1 * sin_lat2 + cos_lat1 * cos_lat2 * cos_delta
    y = ((cos_lat2 * sin_delta) ** 2 + (cos_lat1 * sin_lat2 - sin_lat1 * cos_lat2 * cos_delta) ** 2) ** .5
    print(atan2(y, x) * EARTH_RADIUS)
    return round(atan2(y, x) * EARTH_RADIUS / 1000)


def update_flights_status():
    ZERO_TD = datetime.timedelta(minutes=0)
    BOARDING_TD = datetime.timedelta(minutes=40)
    db_sess = db_session.create_session()
    now = datetime.datetime.now()
    status_query = db_sess.query(statuses.Status)
    for flight, status in db_sess.query(flights.Flight, statuses.Status).filter(
            flights.Flight.status_id == statuses.Status.id).all():
        if status.name in ('Отменён', 'Завершён'):
            continue
        if flight.dest_datetime < now:
            flight.status_id = status_query.filter(statuses.Status.name == 'Завершён').first().id
        elif ZERO_TD < flight.dept_datetime - now < BOARDING_TD:
            flight.status_id = status_query.filter(statuses.Status.name == 'Посадка').first().id
    db_sess.commit()


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
        if not check_password_hash(user.hashed_password, form.password.data):
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
    return render_template('manager_airports.html', table=db_session.create_session().query(airports.Airport))


@app.route('/client/airports')
def client_airports():
    return render_template('client_airports.html', table=db_session.create_session().query(airports.Airport))


@app.route('/manager/planes')
def manager_planes():
    return render_template('manager_planes.html', table=db_session.create_session().query(planes.Plane))


@app.route('/manager/add_plane', methods=['GET', 'POST'])
def manager_add_plane():
    form = AddPlaneForm()
    if form.validate_on_submit():
        name = form.name.data
        db_sess = db_session.create_session()
        if db_sess.query(planes.Plane).filter(planes.Plane.name == form.name.data).first():
            logging.warning(f'Самолёты: самолёт {form.name.data} уже в базе данных')
            return render_template('manager_add_plane.html', form=form,
                                   message=f'Самолёт {form.name.data} уже в списке')
        plane = planes.Plane()
        plane.name = name
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


@app.route('/manager/flights', methods=['GET', 'POST'])
def manager_flights():
    db_sess = db_session.create_session()
    update_flights_status()
    return render_template('manager_flights.html',
                           dept_airports=db_sess.query(airports.Airport)
                           .join(flights.Flight, flights.Flight.dept_airport_id == airports.Airport.id),
                           dest_airports=db_sess.query(airports.Airport)
                           .join(flights.Flight, flights.Flight.dest_airport_id == airports.Airport.id),
                           table=db_sess.query(flights.Flight, planes.Plane, statuses.Status).filter(
                               flights.Flight.plane_id == planes.Plane.id,
                               flights.Flight.status_id == statuses.Status.id))


@app.route('/manager/delay_flight', methods=['GET', 'POST'])
def manager_delay_flight():
    update_flights_status()
    form = DelayFlightForm()
    if form.validate_on_submit():
        time = datetime.datetime.strptime(str(form.time.data), '%H:%M:%S')
        if datetime.datetime.now() < time + datetime.timedelta(minutes=15):
            logging.warning(f'Рейсы: Рейс можно задержать минимум на 15 минут')
            return render_template('manager_delay_flight.html', form=form,
                                   message=f'Рейс можно задержать минимум на 15 минут')

        db_sess = db_session.create_session()
        if not (flight := db_sess.query(flights.Flight).filter(flights.Flight.id == form.flight_id.data).first()):
            return render_template('manager_delay_flight.html', form=form,
                                   message=f'Рейс {form.flight_id.data} не найден')
        status = db_sess.query(statuses.Status).filter(flight.status_id == statuses.Status.id).first().name
        delta = datetime.timedelta(hours=time.hour, minutes=time.minute)
        if status in ('По плану', 'Задержан', 'Посадка'):
            flight.dept_datetime += delta
        if status in ('В пути', 'По плану', 'Задержан', 'Посадка'):
            flight.dest_datetime += delta
        else:
            return render_template('manager_delay_flight.html', form=form,
                                   message=f'Не удалось задержать рейс {form.flight_id.data}')
        flight.status_id = db_sess.query(statuses.Status).filter(statuses.Status.name == 'Задержан').first().id
        db_sess.commit()
        logging.info(f'Рейсы: Рейс {flight.id} задержан на {form.time.data}')
        return render_template('manager_delay_flight.html', form=form, message='Рейс задержан')
    logging.warning(f'Рейсы: Форма не прошла валидацию: {form.errors}')
    return render_template('manager_delay_flight.html', form=form, message='Форма не прошла валидацию')


@app.route('/manager/add_flight', methods=['GET', 'POST'])
def manager_add_flight():
    update_flights_status()
    form = AddFlightForm()
    if form.validate_on_submit():
        dept_datetime = form.dept_datetime.data

        if form.dept_city.data == form.dest_city.data:
            return render_template('manager_add_flight.html', form=form,
                                   message=f'Аэропорты должны находиться в разных городах')

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
                                   message=f'Аэропорт {form.dest_city.data}, {form.dest_airport.data} не найден')

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
        plane = db_sess.query(planes.Plane).filter(planes.Plane.name == form.plane.data).first()
        flight.plane_id = plane.id

        distance = calculate_earth_distance(
            *(float(x) for x in requests
                .get(f'http://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_GEOCODER_APIKEY}&geocode='
                     f'{form.dept_city.data}, аэропорт {form.dept_airport.data}&format=json').json()["response"]
            ["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()),
            *(float(x) for x in requests
                .get(f'http://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_GEOCODER_APIKEY}&geocode='
                     f'{form.dest_city.data}, аэропорт {form.dest_airport.data}&format=json').json()["response"]
            ["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()))
        flight.dest_datetime = dept_datetime + datetime.timedelta(hours=distance / plane.average_speed)
        flight.price = plane.flight_cost_per_1000_km // 1000 * distance // plane.rows_num // plane.columns_num
        flight.status_id = db_sess.query(statuses.Status).filter(statuses.Status.name == 'По плану').first().id
        flight.dept_datetime = dept_datetime
        db_sess.add(flight)
        db_sess.commit()
        update_flights_status()
        logging.info(f'Рейсы: Рейс добавлен')
        return render_template('manager_add_flight.html', form=form, message='Рейс добавлен')
    logging.warning(f'Рейсы: Форма не прошла валидацию: {form.errors}')
    return render_template('manager_add_flight.html', form=form, message='Форма не прошла валидацию')


@app.route('/manager/cancel_flight', methods=['GET', 'POST'])
def manager_cancel_flight():
    form = CancelFlightForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not (flight := db_sess.query(flights.Flight).filter(flights.Flight.id == form.flight_id.data).first()):
            return render_template('manager_cancel_flight.html', form=form,
                                   message=f'Рейс {form.flight_id.data} не найден')
        flight.status_id = db_sess.query(statuses.Status).filter(statuses.Status.name == 'Отменён').first().id
        db_sess.commit()
        logging.info(f'Рейсы: Рейс {flight.id} отменён')
        return render_template('manager_cancel_flight.html', form=form, message='Рейс отменён')
    logging.warning(f'Рейсы: Форма не прошла валидацию: {form.errors}')
    return render_template('manager_cancel_flight.html', form=form, message='Форма не прошла валидацию')


@app.route('/manager/delete_plane', methods=['GET', 'POST'])
def manager_delete_plane():
    update_flights_status()
    form = DeletePlaneForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        name = form.name.data
        if not (p := db_sess.query(planes.Plane).filter(planes.Plane.name == name).first()):
            return render_template('manager_delete_plane.html', form=form,
                                   message=f'Самолёт {form.name.data} не найден')
        if db_sess.query(flights.Flight, planes.Plane).filter(flights.Flight.status_id not in (3, 6) and
                                                              flights.Flight.plane_id == p.id).first():
            return render_template('manager_delete_plane.html', form=form,
                                   message=f'Самолёт {form.name.data} ещё используется')
        db_sess.close()
        cur.execute(f'DELETE FROM Planes WHERE name = "{name}"')
        con.commit()
        '''db_sess.delete(planes.Plane).where(planes.Plane.name == name)
        db_sess.commit()'''
        return render_template('manager_delete_plane.html', form=form, message='Самолёт удалён')
    logging.warning(f'Билеты: Форма не прошла валидацию: {form.errors}')
    return render_template('manager_delete_plane.html', form=form, message='Форма не прошла валидацию')


@app.route('/client')
def client():
    return render_template('/client.html')


@app.route('/client/buy_ticket', methods=['GET', 'POST'])
def client_buy_ticket():
    update_flights_status()
    form = BuyTicketForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not (flight := db_sess.query(flights.Flight).filter(flights.Flight.id == form.flight_id.data).first()):
            return render_template('client_buy_ticket.html', form=form,
                                   message=f'Рейс {form.flight_id.data} не найден')
        if db_sess.query(statuses.Status).filter(statuses.Status.id == flight.status_id
                                                 ).first().name not in ('По плану', 'Задержан', 'Посадка'):
            return render_template('client_buy_ticket.html', form=form,
                                   message=f'Невозможно купить билет на выбранный рейс')
        if (row := form.row.data) > (p := db_sess.query(planes.Plane).filter(planes.Plane.id == flight.plane_id)
                .first()).rows_num or (column := form.column.data) > p.columns_num:
            return render_template('client_buy_ticket.html', form=form,
                                   message='Максимальное количество рядов: '
                                           f'{p.rows_num}, посадочных мест: {p.columns_num}')
        if db_sess.query(tickets.Ticket).filter(tickets.Ticket.row_num == row).filter(
                                                tickets.Ticket.column_num == column).first():
            return render_template('client_buy_ticket.html', form=form,
                                   message=f'Это место уже занято')
        ticket = tickets.Ticket()
        ticket.flight_id = form.flight_id.data
        ticket.row_num = row
        ticket.column_num = column
        ticket.user_id = current_user.id
        db_sess.add(ticket)
        db_sess.commit()
        return render_template('client_buy_ticket.html', form=form, message='Билет куплен')
    logging.warning(f'Билеты: Форма не прошла валидацию: {form.errors}')
    return render_template('client_buy_ticket.html', form=form, message='Форма не прошла валидацию')


@app.route('/client/return_ticket', methods=['GET', 'POST'])
def client_return_ticket():
    form = ReturnTicketForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not db_sess.query(tickets.Ticket).filter(tickets.Ticket.id == form.id.data).first():
            return render_template('client_return_ticket.html', form=form,
                                   message=f'Билет {form.id.data} не найден')
        if db_sess.query(tickets.Ticket).filter(tickets.Ticket.id == form.id.data).first().user_id != current_user.id:
            return render_template('client_return_ticket.html', form=form,
                                   message=f'Билет {form.id.data} принадлежит другому пользователю')
        db_sess.close()
        cur.execute(f'DELETE FROM Tickets WHERE id = {form.id.data}')
        con.commit()
        '''db_sess.delete(tickets.Ticket).where(tickets.Ticket.id == form.id.data)
        db_sess.commit()'''
        return render_template('client_return_ticket.html', form=form, message='Возврат оформлен')
    logging.warning(f'Билеты: Форма не прошла валидацию: {form.errors}')
    return render_template('client_return_ticket.html', form=form, message='Форма не прошла валидацию')


@app.route('/client/tickets')
def client_tickets():
    db_sess = db_session.create_session()
    return render_template('/client_tickets.html', tickets=db_session.create_session().query(tickets.Ticket)
                           .filter(tickets.Ticket.user_id == current_user.id),
                           dept_airports=db_sess.query(airports.Airport)
                           .join(flights.Flight, flights.Flight.dept_airport_id == airports.Airport.id),
                           dest_airports=db_sess.query(airports.Airport)
                           .join(flights.Flight, flights.Flight.dest_airport_id == airports.Airport.id),
                           fs=db_sess.query(flights.Flight), planes=db_sess.query(planes.Plane),
                           statuses=db_sess.query(statuses.Status), ff=flights.Flight)


@app.route('/client/flights')
def client_flights():
    update_flights_status()
    db_sess = db_session.create_session()
    update_flights_status()
    return render_template('client_flights.html',
                           dept_airports=db_sess.query(airports.Airport)
                           .join(flights.Flight, flights.Flight.dept_airport_id == airports.Airport.id),
                           dest_airports=db_sess.query(airports.Airport)
                           .join(flights.Flight, flights.Flight.dest_airport_id == airports.Airport.id),
                           table=db_sess.query(flights.Flight, planes.Plane, statuses.Status).filter(
                               flights.Flight.plane_id == planes.Plane.id,
                               flights.Flight.status_id == statuses.Status.id))


if __name__ == '__main__':
    db_session.global_init("db/flights.db")
    app.run(port=8080, host='127.0.0.1')
