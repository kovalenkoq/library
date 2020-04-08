import sqlalchemy as sa
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase

class Genres(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'genres'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=True, unique=True)


    def __repr__(self):
        return f'<Genre> {self.id} {self.name}'
