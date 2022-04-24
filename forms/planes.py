from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class AddPlaneForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    rows_num = IntegerField('Количество рядов', validators=[DataRequired(), NumberRange(1)])
    columns_num = IntegerField('Количество мест', validators=[DataRequired(), NumberRange(1)])
    flight_cost_per_1000_km = IntegerField('Стоимость полёта на 1000 км', validators=[DataRequired(), NumberRange(0)])
    average_speed = IntegerField('Средняя скорость полёта, км/ч', validators=[DataRequired(), NumberRange(1)])
    submit = SubmitField('Готово')


class DeletePlaneForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Готово')