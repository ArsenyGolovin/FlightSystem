from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email


class RegisterForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Подтверждение пароля', validators=[DataRequired()])
    user_type = RadioField("Войти как:", choices=[("client", "Клиент"), ("manager", "Менеджер")],
                           validators=[DataRequired()])
    submit = SubmitField('Готово')