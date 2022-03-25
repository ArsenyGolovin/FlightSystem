from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class AddPlaneForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    rows_num = IntegerField('Количество рядов', validators=[DataRequired()])
    columns_num = IntegerField('Количество мест', validators=[DataRequired()])
    submit = SubmitField('Готово')
