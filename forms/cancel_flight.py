from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class CancelFlightForm(FlaskForm):
    flight_id = IntegerField('Номер рейса', validators=[DataRequired(), NumberRange(1)])
    submit = SubmitField('Готово')
