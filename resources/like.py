from flask_restful import Resource
from flask import request
from models.user import UserModel
from models.like import LikeModel
from schemas.like import LikeSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError


like_schema = LikeSchema()


class Like(Resource):

    @jwt_required
    def get(self, post_id):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)

        if user:
            existing_like = LikeModel.find_by_user_id(login, post_id)

            if existing_like:

                return {"message": "unliked"}, 200
            else:

                return {"message": "liked"}, 201
        else:
            return {"message": "User not found"}, 404

    @jwt_required
    def post(self):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)

        if user:
            try:
                new_like = like_schema.load(request.get_json(), partial=True)
            except ValidationError as err:
                return err.messages, 400

            existing_like = LikeModel.find_by_user_id(login, new_like.post_id)
        
            if existing_like:
                existing_like.delete_from_db()

                return {'message': 'unliked'}, 200
            else:

                new_like.login = login

                new_like.save_to_db()
                return {"message": "liked"}, 201
        else:
            return {"message":"User not found"}, 404

        
class Likes(Resource):

    @jwt_required
    def get(self, post_id):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            return {'likes': [like_schema.dump(x) for x in LikeModel.find_by_post_id(post_id)]}

        else:
            return {"message":"User not found"}, 404

    @jwt_required
    def post(self, post_id):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            no_of_likes = LikeModel.count_likes(post_id)
            return {'likes_count': no_of_likes}
        else:
            return {"message": "User not found"}, 404
