from flask_restful import Resource
from flask import request
from models.user import UserModel
from models.follow import FollowModel
from schemas.follow import FollowSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError


follow_schema = FollowSchema()


class Follow(Resource):

    @jwt_required
    def get(self, follower_login, followee_login):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)

        if user:
            user_to_check = UserModel.find_by_username(followee_login)
            if user_to_check:

                existing_follow = FollowModel.find_specific_follow(follower_login, followee_login)

                if existing_follow:

                    return {'message': 'user followed'}, 200
                else:

                    return {"message": "user unfollowed"}, 200
            else:
                return {"message": "User to follow not found"}, 404

        else:
            return {"message": "User not found"}, 404


    @jwt_required
    def post(self):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)

        if user:
            try:
                new_follow = follow_schema.load(request.get_json(), partial=True)
            except ValidationError as err:
                return err.messages, 400
            user_to_follow = UserModel.find_by_username(new_follow.followee_login)
            if user_to_follow:

                existing_follow = FollowModel.find_specific_follow(user.login, new_follow.followee_login)
        
                if existing_follow:

                    existing_follow.delete_from_db()

                    return {'message': 'user unfollowed'}, 200
                else:
                    new_follow.follower_login = user.login
                    new_follow.save_to_db()
                    return {"message": "user followed"}, 201
            else:
                return {"message": "User to follow not found"}, 404

        else:
            return {"message":"User not found"}, 404

class Follows(Resource):

    @jwt_required
    def get(self, user_login):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            return {'followers': [x.follower_login for x in FollowModel.find_followers_of_user(user_login)],
                    'followees': [x.followee_login for x in FollowModel.find_who_user_follows(user_login)]}
        else:
            return {"message": "User not found"}, 404

    @jwt_required
    def post(self, user_login):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            no_of_followers = FollowModel.count_followers_of_user(user_login)
            no_of_followees = FollowModel.count_followees_user_follows(user_login)

            return {'followers_count': no_of_followers, 'followees_count': no_of_followees}
        else:
            return {"message": "User not found"}, 404