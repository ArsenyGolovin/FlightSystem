from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField
from wtforms.validators import DataRequired


class AddFlightForm(FlaskForm):
    dept_city = StringField('Город отправления', validators=[DataRequired()])
    dept_airport = StringField('Аэропорт отправления', validators=[DataRequired()])
    dest_city = StringField('Город назначения', validators=[DataRequired()])
    dest_airport = StringField('Аэропорт назначения', validators=[DataRequired()])
    plane = StringField('Самолёт', validators=[DataRequired()])
    dept_datetime = StringField('Дата и время отправления', validators=[DataRequired()])
    submit = SubmitField('Готово')
