import datetime

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
    users = put(f'http://127.0.0.1:5000/api/issue/{issue_id}').json()
    return redirect('/issue')


@app.route("/add_issue/<int:book_id>", methods=['GET', 'POST'])
@login_required
def set_issue(book_id):

    data = {'user_id': current_user.id, 'book_id': book_id}
    res = post('http://127.0.0.1:5000/api/issue', json=data)

    if res:
        return redirect('/books')

    return render_template("books.html", title='Книги', message='Произошла ошибка. Книга не выдана')


@app.route("/add_issue", methods=['GET', 'POST'])
@login_required
def add_issue():
    form = AddIssueForm()
    users = get('http://127.0.0.1:5000/api/users').json()['users']
    books = get('http://127.0.0.1:5000/api/books').json()['books']

    users = sorted([(user['id'], user['name']) for user in users], key=lambda x: x[1])
    books = sorted([(book['id'], f"{book['title']} | {book['author']} | {book['count']}") for book in books], key=lambda x: x[1])

    form.users.choices = users
    form.books.choices = books

    if form.validate_on_submit():
        data = {'user_id': form.users.data, 'book_id': form.books.data}
        res = post('http://127.0.0.1:5000/api/issue', json=data)
        if res:
            return redirect('/issue')

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

    # for d in data:
    #     if not d.date_finish:
    #         d.date_finish = datetime.datetime.time()
    #     print(d.date_finish)

    if hide_returned:
        data = list(filter(lambda x: not x.date_finish, data))

    # for i in range(len(data)):
    #     if not data[i].date_finish:
    #         data[i].date_finish = '-'

    data = sorted(data, key=lambda x: str(x.date_finish) if not x.date_finish else '', reverse=True)
    return render_template("issue.html", title='Выдача', issue=data, form=form)


@app.route("/delete_book/<int:book_id>", methods=['GET'])
@login_required
def delete_book(book_id):
    if request.method == 'GET':
        res = delete(f'http://127.0.0.1:5000/api/books/{book_id}')
        return redirect('/books')


@app.route("/edit_book/<int:book_id>", methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    form = AddBookForm()
    if request.method == 'GET':
        book = get(f'http://127.0.0.1:5000/api/books/{book_id}').json()['book']
        print(book)
        form.title.data = book['title']
        form.author.data = book['author']
        form.year.data = book['year']
        form.count.data = book['count']
        form.genre.data = book['genre']['name']
        return render_template("add_user.html", title='Изменить книгу', form=form)

    if form.validate_on_submit():
        session = db_session.create_session()
        genre = session.query(Genres).filter(Genres.name == form.genre.data).first()
        if not genre:
            session.add(Genres(name=form.genre.data))
            genre = session.query(Genres).filter(Genres.name == form.genre.data).first()
        session.commit()
        data = {
            'title': form.title.data,
            'author': form.author.data,
            'year': form.year.data,
            'count': form.count.data
        }
        data['genre_id'] = genre.id

        if put(f'http://127.0.0.1:5000/api/books/{book_id}', json=data):
            return redirect('/books')
        else:
            return render_template("add_book.html", title='Добавить читателя', form=form,
                                   message='Error')
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

        data = {
            'title': form.title.data,
            'author': form.author.data,
            'year': form.year.data,
            'count': form.count.data
        }
        data['genre_id'] = genre.id

        if post('http://127.0.0.1:5000/api/books', json=data):
            return redirect('/books')
        else:
            return render_template("add_book.html", title='Добавить читателя', form=form, message='Error')

    return render_template("add_book.html", title='Добавить книгу', form=form)


@app.route("/delete_user/<int:user_id>", methods=['GET'])
@login_required
def delete_user(user_id):
    if request.method == 'GET':
        res = delete(f'http://127.0.0.1:5000/api/users/{user_id}')
        return redirect('/users')


@app.route("/edit_user/<int:user_id>", methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    form = AddUserForm()
    if request.method == 'GET':
        user = get(f'http://127.0.0.1:5000/api/users/{user_id}').json()['user']
        form.name.data = user['name']
        form.email.data = user['email']
        form.hashed_password.data = ''
        return render_template("add_user.html", title='Добавить читателя', form=form)
    if form.validate_on_submit():
        data = {
            'name': form.name.data,
            'email': form.email.data,
            'hashed_password': form.hashed_password.data
        }
        if put(f'http://127.0.0.1:5000/api/users/{user_id}', json=data):
            return redirect('/users')
        else:
            return render_template("add_user.html", title='Добавить читателя', form=form,
                                   message='Error')
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
    form = AddUserForm()
    if form.validate_on_submit():
        data = {
            'name': form.name.data,
            'email': form.email.data,
            'hashed_password': form.hashed_password.data
        }
        if post('http://127.0.0.1:5000/api/users', json=data):
            return redirect('/login')
        else:
            return render_template("add_user.html", title='Добавить читателя', form=form, message='Error')

    return render_template("add_user.html", title='Добавить читателя', form=form)


@app.route("/users")
@login_required
def users():
    users = get('http://127.0.0.1:5000/api/users').json()
    return render_template("users.html", title='Читатели', users=users['users'])


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
    app.run()


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()