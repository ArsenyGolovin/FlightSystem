from flask_wtf import FlaskForm
from wtforms import DateTimeField, IntegerField, TimeField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class AddFlightForm(FlaskForm):
    dept_city = StringField('Город отправления', validators=[DataRequired()])
    dept_airport = StringField('Аэропорт отправления', validators=[DataRequired()])
    dest_city = StringField('Город назначения', validators=[DataRequired()])
    dest_airport = StringField('Аэропорт назначения', validators=[DataRequired()])
    plane = StringField('Самолёт', validators=[DataRequired()])
    dept_datetime = DateTimeField('Дата и время отправления (ГГГГ-ММ-ДД ЧЧ:ММ)',
                                  validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    submit = SubmitField('Готово')


class DelayFlightForm(FlaskForm):
    flight_id = IntegerField('Номер рейса', validators=[DataRequired(), NumberRange(1)])
    time = TimeField('Время', validators=[DataRequired()])
    submit = SubmitField('Готово')


class CancelFlightForm(FlaskForm):
    flight_id = IntegerField('Номер рейса', validators=[DataRequired(), NumberRange(1)])
    submit = SubmitField('Готово')