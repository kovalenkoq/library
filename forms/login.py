from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField

class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    hashed_password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')