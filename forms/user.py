from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class RegistrationForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(8)])
    password2 = PasswordField('Подтверждение пароля', validators=[DataRequired(), Length(8)])
    user_type = RadioField("Войти как:", choices=[("client", "Клиент"), ("manager", "Менеджер")],
                           validators=[DataRequired()])
    submit = SubmitField('Готово')


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Готово')
