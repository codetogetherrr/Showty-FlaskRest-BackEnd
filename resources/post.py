from flask_restful import Resource
from flask import request
from models.post import PostModel
from models.user import UserModel
from models.hashtag import HashtagModel
from models.comment import CommentModel
from schemas.post import PostSchema, PostUpdateSchema
from schemas.hashtag import HashtagSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.sql import func
from marshmallow import ValidationError

post_schema = PostSchema()
post_update_schema = PostUpdateSchema()
hashtag_schema = HashtagSchema()


class Post(Resource):

    @jwt_required
    def get(self):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            last_post = PostModel.get_last_post(login)
            return post_schema.dump(last_post)
        else:
            return {"message": "User not found"}, 404

    @jwt_required
    def post(self):
        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            try:
                post = post_schema.load(request.get_json())
            except ValidationError as err:
                return err.messages, 400

            post.login = login
            post.date = func.now()
            post.save_to_db()

            possible_hashtags = HashtagModel.find_hashtags_in_text(post.description)
            if possible_hashtags:
                for hashtag in possible_hashtags:
                    existing_hashtag = HashtagModel.find_only_for_post(hashtag, post.post_id)
                    if not existing_hashtag:
                        hashtag_data = {"post_id": post.post_id, "hashtag": hashtag}
                        new_hashtag = hashtag_schema.load(hashtag_data)
                        new_hashtag.save_to_db()
            return {"message": "Post added successfully."}, 201
        else:
            return {"message": "User not found"}, 404

    @jwt_required
    def put(self, post_id):
        post = PostModel.find_by_post_id(post_id)
        if post:

            if post.login == get_jwt_identity():
                try:
                    post_to_update = post_update_schema.load(request.get_json(), partial=True, instance=post)
                except ValidationError as err:
                    return err.messages, 400
                possible_hashtags = HashtagModel.find_hashtags_in_text(post_to_update.description)
                if possible_hashtags:
                    for hashtag in possible_hashtags:
                        existing_hashtag = HashtagModel.find_only_for_post(hashtag, post.post_id)
                        if not existing_hashtag:
                            hashtag_data = {"post_id": post.post_id , "hashtag": hashtag}
                            new_hashtag = hashtag_schema.load(hashtag_data)
                            new_hashtag.save_to_db()
                post_to_update.save_to_db()
                return {"message": "Post updated successfully."}, 200
        else:
            return {'message': 'It is not a post of logged in user'}, 404

    @jwt_required
    def delete(self, post_id):
        post_delete = PostModel.find_by_post_id(post_id)
        if post_delete.login == get_jwt_identity():

            comments_delete = CommentModel.find_by_post_id(post_delete.post_id)
            hashtags_delete = HashtagModel.get_hashtags_for_post(post_delete.post_id)

            if comments_delete:
                for comment in comments_delete:
                    comment.delete_from_db()
            if hashtags_delete:
                for hashtag in hashtags_delete:
                    hashtag.delete_from_db()

            post_delete.delete_from_db()
            return {'message': 'Post deleted'}, 200
        else:
            return {'message': 'It is not a post of user logged in.'}, 404


class Posts(Resource):

    @jwt_required
    def get(self, page, user_login):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            user_to_get_posts = UserModel.find_by_username(user_login)

            if user_to_get_posts:

                return {'posts_user': [post_schema.dump(x) for x in PostModel.get_paginated_posts(user_login, page).items]}
            else:
                return {"message": "User not found"}, 404

        else:
            return {"message": "User not found"}, 404

    @jwt_required
    def post(self, login):
        user = UserModel.find_by_username(login)
        if user:
            no_of_posts=PostModel.count_posts(login)
            return {'posts_count': no_of_posts}
        else:
            return {"message": "User not found"}, 404
