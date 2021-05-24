
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import UserModel
from models.hashtag import HashtagModel


class Search(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('keyword', required=True, type=str, help="You have to provide keyword")

    @jwt_required
    def post(self):
        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        args = self.parser.parse_args()
        if user:
            return [{"search_result": "#" + x.hashtag, "type" : "hashtag"} for x in HashtagModel.search_by_hashtag(args['keyword'])] + \
                   [{"search_result": x.login, "type" : "user"} for x in UserModel.search_by_username(args['keyword'])], 200
        else:
            return {"message": "User not found"}, 404


class SearchUser(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('keyword', required=True, type=str, help="You have to provide keyword")

    @jwt_required
    def post(self):
        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        args = self.parser.parse_args()
        if user:
            return [{"search_result": x.login, "type" : "user"} for x in UserModel.search_by_username(args['keyword'])], 200
        else:
            return {"message": "User not found"}, 404