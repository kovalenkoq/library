from flask import jsonify
from data import db_session
from data.__all_models import Issue, Books
from flask_restful import abort, reqparse, Resource
import datetime

parser = reqparse.RequestParser()
parser.add_argument('book_id', required=True)
parser.add_argument('user_id', required=True)
# parser.add_argument('date_start', required=True)
# parser.add_argument('date_finish', required=True)


def abort_if_issue_not_found(issue_id):
    session = db_session.create_session()
    issue = session.query(Issue).get(issue_id)
    if not issue:
        abort(404, message=f"Issue {issue_id} not found")


class IssueResource(Resource):
    def get(self, issue_id):
        abort_if_issue_not_found(issue_id)
        session = db_session.create_session()
        issue = session.query(Issue).get(issue_id)
        return jsonify({'issue': issue.to_dict()})

    # def delete(self, user_id):
    #     abort_if_user_not_found(user_id)
    #     session = db_session.create_session()
    #     user = session.query(Users).get(user_id)
    #     session.delete(user)
    #     session.commit()
    #     return jsonify({'success': 'OK'})

    def put(self, issue_id):
        abort_if_issue_not_found(issue_id)
        # args = parser.parse_args()

        session = db_session.create_session()
        issue = session.query(Issue).get(issue_id)

        issue.date_finish = datetime.datetime.now()
        issue.book.inc_book()

        session.commit()
        return jsonify({'success': 'OK'})

class IssueListResource(Resource):
    def get(self):
        session = db_session.create_session()
        issue = session.query(Issue).all()
        return jsonify({'issue': [item.to_dict() for item in issue]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()

        book = session.query(Books).get(args['book_id'])
        if book.dec_book():
            issue = Issue(
                user_id=args['user_id'],
                book_id=args['book_id'])
            session.add(issue)
            session.commit()
            return jsonify({'success': 'OK'})

        return jsonify({'error': 'Not enough books'})





