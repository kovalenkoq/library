from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, SelectField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired

class FilterIssueForm(FlaskForm):
    show_returned = BooleanField('Скрыть возвращенные', default=False)

    submit = SubmitField('Применить')