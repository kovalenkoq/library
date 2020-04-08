from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired

class AddIssueForm(FlaskForm):
    users = SelectField('Читатели', validators=[DataRequired()], coerce=int)
    books = SelectField ('Книги', validators=[DataRequired()], coerce=int)

    submit = SubmitField('Выдать')