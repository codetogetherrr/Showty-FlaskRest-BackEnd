
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.hashtag import HashtagModel
from models.user import UserModel
from schemas.hashtag import HashtagSchema

from schemas.post import PostSchema


post_schema = PostSchema()
hashtag_schema = HashtagSchema()



class Hashtag(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('hashtag', required=True, type=str, help="You have to provide hashtag")

    @jwt_required
    def post(self):
        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        args = self.parser.parse_args()
        last_post_with_hashtag = HashtagModel.get_last_post_with_hashtag(args['hashtag'])
        if user:
            return post_schema.dump(last_post_with_hashtag)

        else:
            return {"message": "User not found"}, 404




class Hashtags(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('hashtag', required=True, type=str, help="You have to provide hashtag")
    parser.add_argument('page', required=True, type=int, help="You have to provide page of posts with hashtag")

    @jwt_required
    def post(self):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        args = self.parser.parse_args()
        if user:
            return {'posts_with_hashtag': [post_schema.dump(x) for x in HashtagModel.get_paginated_posts_for_hashtag(args['hashtag'], args['page']).items]}

        else:
            return {"message": "User not found" }, 404