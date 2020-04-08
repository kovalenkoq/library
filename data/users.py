import sqlalchemy as sa
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class Users(SqlAlchemyBase, SerializerMixin, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=True)
    email = sa.Column(sa.String, nullable=True)
    hashed_password = sa.Column(sa.String, nullable=True)

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

