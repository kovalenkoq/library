import sqlalchemy as sa
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
import datetime

class Issue(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'issue'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=True)
    book_id = sa.Column(sa.Integer, sa.ForeignKey('books.id'), nullable=True)
    date_start = sa.Column(sa.DateTime, default=datetime.datetime.now, nullable=True)
    date_finish = sa.Column(sa.DateTime, default=None)
    user = orm.relation('Users')
    book = orm.relation('Books')

    def __repr__(self):
        return f'<Issue> {self.id} {self.user.name} {self.book.title}'



