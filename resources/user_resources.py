from flask import jsonify
from data import db_session
from data.__all_models import Users
from flask_restful import abort, reqparse, Resource

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('hashed_password', required=True)
parser.add_argument('email', required=True)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(Users).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(Users).get(user_id)
        return jsonify({'user': user.to_dict(only=('id', 'name', 'email'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(Users).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        abort_if_user_not_found(user_id)
        args = parser.parse_args()

        session = db_session.create_session()
        user = session.query(Users).get(user_id)

        user.name = args['name']
        user.email = args['email']
        user.set_password(args['hashed_password'])

        session.commit()
        return jsonify({'success': 'OK'})

class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(Users).all()
        return jsonify({'users': [item.to_dict(only=('id', 'name', 'email')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = Users(
            name=args['name'],
            email=args['email'])
        user.set_password(args['hashed_password'])

        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})