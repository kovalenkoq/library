from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField
from wtforms.validators import DataRequired

class AddBookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    genre = StringField('Жанр', validators=[DataRequired()])
    year = IntegerField('Год', validators=[DataRequired()])
    count = IntegerField('Количество', validators=[DataRequired()])
    submit = SubmitField('Войти')