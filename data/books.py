import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase

class Books(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'books'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String, nullable=True)
    author = sa.Column(sa.String, nullable=True)
    genre_id = sa.Column(sa.Integer, sa.ForeignKey('genres.id'), nullable=True)
    year = sa.Column(sa.Integer, nullable=True)
    count = sa.Column(sa.Integer, nullable=True)
    genre = orm.relation('Genres')

    def __repr__(self):
        return f'<Book> {self.id} {self.title} {self.author} {self.count}'

    def dec_book(self):
        if self.count > 0:
            self.count -= 1
            return True
        else:
            return False

    def inc_book(self):
        self.count += 1

