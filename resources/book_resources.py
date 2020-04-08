from flask import jsonify
from data import db_session
from data.__all_models import Books
from flask_restful import abort, reqparse, Resource

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('author', required=True)
parser.add_argument('genre_id', required=True)
parser.add_argument('year', required=True)
parser.add_argument('count', required=True)


def abort_if_book_not_found(book_id):
    session = db_session.create_session()
    book = session.query(Books).get(book_id)
    if not book:
        abort(404, message=f"Book {book_id} not found")


class BooksResource(Resource):
    def get(self, book_id):
        abort_if_book_not_found(book_id)
        session = db_session.create_session()
        book = session.query(Books).get(book_id)
        return jsonify({'book': book.to_dict()})

    def delete(self, book_id):
        abort_if_book_not_found(book_id)
        session = db_session.create_session()
        book = session.query(Books).get(book_id)
        session.delete(book)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, book_id):
        abort_if_book_not_found(book_id)
        args = parser.parse_args()

        session = db_session.create_session()
        book = session.query(Books).get(book_id)

        book.title = args['title']
        book.author = args['author']
        book.genre_id = args['genre_id']
        book.year = args['year']
        book.count = args['count']

        session.commit()
        return jsonify({'success': 'OK'})

class BooksListResource(Resource):
    def get(self):
        session = db_session.create_session()
        books = session.query(Books).all()
        return jsonify({'books': [item.to_dict(only=('id', 'title', 'author', 'count')) for item in books]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        book = Books()
        book.title = args['title']
        book.author = args['author']
        book.genre_id = args['genre_id']
        book.year = args['year']
        book.count = args['count']
        session.add(book)
        session.commit()
        return jsonify({'success': 'OK'})