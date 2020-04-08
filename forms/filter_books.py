from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, SelectField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired

class FilterBooksForm(FlaskForm):
    title = StringField('Поиск по названи')
    authors = SelectField('Поиск по автору', coerce=int)
    genre = SelectField('Поиск по жанру', coerce=int)
    year = SelectField('Поиск по году', coerce=int)

    submit = SubmitField('Применить')