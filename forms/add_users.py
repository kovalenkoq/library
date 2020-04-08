from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

class AddUserForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    hashed_password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')