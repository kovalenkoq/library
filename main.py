import datetime
import os

from flask import Flask, render_template, request, redirect
from flask_restful import reqparse, abort, Api, Resource
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from sqlalchemy import distinct

from data import db_session
from data.__all_models import *
from forms.__all_forms import *

from resources import user_resources
from resources import book_resources
from resources import issue_resources
from requests import get, post, put, delete

URL = 'http://ya-lyceum-library.herokuapp.com'
port = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

api = Api(app)
api.add_resource(user_resources.UsersListResource, '/api/users')
api.add_resource(user_resources.UsersResource, '/api/users/<int:user_id>')
api.add_resource(book_resources.BooksListResource, '/api/books')
api.add_resource(book_resources.BooksResource, '/api/books/<int:book_id>')
api.add_resource(issue_resources.IssueListResource, '/api/issue')
api.add_resource(issue_resources.IssueResource, '/api/issue/<int:issue_id>')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(Users).get(user_id)


@app.route("/return_issue/<int:issue_id>", methods=['GET'])
@login_required
def return_issue(issue_id):
    session = db_session.create_session()
    issue = session.query(Issue).get(issue_id)

    issue.date_finish = datetime.datetime.now()
    issue.book.inc_book()

    session.commit()
    return redirect('/issue')


@app.route("/add_issue/<int:book_id>", methods=['GET', 'POST'])
@login_required
def set_issue(book_id):
    session = db_session.create_session()

    book = session.query(Books).get(book_id)
    if book.dec_book():
        issue = Issue(
            user_id=current_user.id,
            book_id=book_id)
        session.add(issue)
        session.commit()
        return redirect('/books')

    return render_template("books.html", title='Книги', message='Произошла ошибка. Книга не выдана')


@app.route("/add_issue", methods=['GET', 'POST'])
@login_required
def add_issue():
    session = db_session.create_session()
    form = AddIssueForm()

    users = session.query(Users).all()
    books = session.query(Books).all()

    users = sorted([(user.id, user.name) for user in users], key=lambda x: x[1])
    books = sorted([(book.id, f"{book.title} | {book.author} | {book.count}") for book in books], key=lambda x: x[1])

    form.users.choices = users
    form.books.choices = books

    if form.validate_on_submit():

        book = session.query(Books).get(form.books.data)
        if book.dec_book():
            issue = Issue(
                user_id=form.users.data,
                book_id=form.books.data)
            session.add(issue)
            session.commit()
            return redirect('/issue')
        else:
            return render_template("add_issue.html", title='Добавить книгу', form=form, message='Not enough books')

    return render_template("add_issue.html", title='Добавить книгу', form=form)


@app.route("/issue", methods=['GET', 'POST'])
@login_required
def issue():
    form = FilterIssueForm()

    hide_returned = False
    if form.validate_on_submit():
        hide_returned = form.show_returned.data
    session = db_session.create_session()
    if current_user.id == 1:
        data = session.query(Issue).all()
    else:
        data = session.query(Issue).filter(Issue.user_id == current_user.id).all()

    if hide_returned:
        data = list(filter(lambda x: not x.date_finish, data))

    data = sorted(data, key=lambda x: str(x.date_finish) if not x.date_finish else '', reverse=True)
    return render_template("issue.html", title='Выдача', issue=data, form=form)


@app.route("/delete_book/<int:book_id>", methods=['GET'])
@login_required
def delete_book(book_id):
    if request.method == 'GET':
        session = db_session.create_session()
        book = session.query(Books).get(book_id)
        session.delete(book)
        session.commit()
        return redirect('/books')


@app.route("/edit_book/<int:book_id>", methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    form = AddBookForm()
    session = db_session.create_session()
    if request.method == 'GET':

        book = session.query(Books).get(book_id)
        form.title.data = book.title
        form.author.data = book.author
        form.year.data = book.year
        form.count.data = book.count
        form.genre.data = book.genre.name
        return render_template("add_user.html", title='Изменить книгу', form=form)

    if form.validate_on_submit():
        session = db_session.create_session()
        genre = session.query(Genres).filter(Genres.name == form.genre.data).first()
        if not genre:
            session.add(Genres(name=form.genre.data))
            genre = session.query(Genres).filter(Genres.name == form.genre.data).first()
        session.commit()

        book = session.query(Books).get(book_id)
        book.title = form.title.data
        book.author = form.author.data
        book.genre_id = genre.id
        book.year = form.year.data
        book.count = form.count.data
        session.commit()
        return redirect('/books')

    return render_template("add_book.html", title='Изменить книгу', form=form)


@app.route("/add_book", methods=['GET', 'POST'])
@login_required
def add_book():
    form = AddBookForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        genre = session.query(Genres).filter(Genres.name == form.genre.data).first()
        if not genre:
            session.add(Genres(name=form.genre.data))
            genre = session.query(Genres).filter(Genres.name == form.genre.data).first()
        session.commit()

        book = Books()
        book.title = form.title.data
        book.author = form.author.data
        book.genre_id = genre.id
        book.year = form.year.data
        book.count = form.count.data
        session.add(book)
        session.commit()

        return redirect('/books')

    return render_template("add_book.html", title='Добавить книгу', form=form)


@app.route("/delete_user/<int:user_id>", methods=['GET'])
@login_required
def delete_user(user_id):
    if request.method == 'GET':
        session = db_session.create_session()
        user = session.query(Users).get(user_id)
        session.delete(user)
        session.commit()

        return redirect('/users')


@app.route("/edit_user/<int:user_id>", methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    session = db_session.create_session()
    form = AddUserForm()
    if request.method == 'GET':
        # user = get(f'{URL}:{port}/api/users/{user_id}').json()['user']

        user = session.query(Users).get(user_id)
        if user:
            form.name.data = user.name
            form.email.data = user.email
            form.hashed_password.data = ''
            return render_template("add_user.html", title='Добавить читателя', form=form)
        else:
            return render_template("add_user.html", title='Добавить читателя', form=form,
                                   message='Error')

    if form.validate_on_submit():

        user = session.query(Users).get(user_id)

        user.name = form.name.data
        user.email = form.email.data
        user.set_password(form.hashed_password.data)

        session.commit()

        return redirect('/users')

        # if put(f'{URL}:{port}/api/users/{user_id}', json=data):
        #     return redirect('/users')
        # else:
        #     return render_template("add_user.html", title='Добавить читателя', form=form,
        #                            message='Error')
    return render_template("add_user.html", title='Добавить читателя', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(Users).filter(Users.email == form.email.data).first()
        if user and user.check_password(form.hashed_password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/issue")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    session = db_session.create_session()
    form = AddUserForm()
    if form.validate_on_submit():
        user = Users(
            name=form.name.data,
            email=form.email.data)
        user.set_password(form.hashed_password.data)
        session.add(user)
        session.commit()
        return redirect('/login')

    return render_template("add_user.html", title='Добавить читателя', form=form)


@app.route("/users")
@login_required
def users():
    # users = get(f'{URL}:{port}/api/users').json()
    session = db_session.create_session()
    users = session.query(Users).all()

    return render_template("users.html", title='Читатели', users=users)


@app.route("/books", methods=['GET', 'POST'])
def books():
    session = db_session.create_session()
    form = FilterBooksForm()

    genre = session.query(Genres).all()
    form.genre.choices = [(0, '')] + [(g.id, g.name) for g in genre]

    authors = session.query(Books.author).distinct().all()
    authors = [(0, '')] + [(i+1, authors[i][0]) for i in range(len(authors))]
    authors_dict = {k: v for k, v in authors}
    form.authors.choices = sorted(authors_dict.items(), key=lambda x: x[1])


    year = session.query(Books.year).distinct().all()
    year = [(0, '')] + [(i + 1, str(year[i][0])) for i in range(len(year))]
    year_dict = {k: v for k,v in year}
    form.year.choices = sorted(year_dict.items(), key=lambda x: x[1])

    genre = ''
    author = ''
    year = 0
    if form.validate_on_submit():
        genre = form.genre.data
        author = authors_dict[form.authors.data]
        year = year_dict[form.year.data]

    query = []
    if genre:
        query.append(Books.genre_id == genre)
    if author:
        query.append(Books.author == author)
    if year:
        query.append(Books.year == year)
    if form.title.data:
        query.append(Books.title.like(f'%{form.title.data}%'))

    print(query, genre, form.genre.data)
    books = session.query(Books).filter(*query).all()
    return render_template("books.html", title='Книги', books=books, form=form)


@app.route("/")
def index():
    return render_template("index.html")


def main():
    db_session.global_init("db/blogs.sqlite")
    app.run(host='0.0.0.0', port=port)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()