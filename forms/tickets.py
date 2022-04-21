from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class BuyTicketForm(FlaskForm):
    flight_id = IntegerField('№ рейса', validators=[DataRequired(), NumberRange(1)])
    row = IntegerField('Ряд', validators=[DataRequired(), NumberRange(1)])
    column = IntegerField('Место', validators=[DataRequired(), NumberRange(1)])
    submit = SubmitField('Готово')


class ReturnTicketForm(FlaskForm):
    id = IntegerField('№ билета', validators=[DataRequired(), NumberRange(1)])
    submit = SubmitField('Готово')
