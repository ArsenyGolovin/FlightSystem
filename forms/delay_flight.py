from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, TimeField
from wtforms.validators import DataRequired, NumberRange


class DelayFlightForm(FlaskForm):
    flight_id = IntegerField('Номер рейса', validators=[DataRequired(), NumberRange(1)])
    time = TimeField('Время', validators=[DataRequired()])
    submit = SubmitField('Готово')
