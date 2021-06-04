from flask_restful import Resource
from flask import request
from models.comment import CommentModel
from models.hashtag import HashtagModel
from models.user import UserModel
from schemas.comment import CommentSchema, CommentUpdateSchema
from schemas.hashtag import HashtagSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.sql import func
from marshmallow import ValidationError

comment_schema = CommentSchema()
comment_update_schema = CommentUpdateSchema()
hashtag_schema = HashtagSchema()


class Comment(Resource):

    @jwt_required
    def get(self, post_id):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            last_comment = CommentModel.get_last_comment(post_id)
            return comment_schema.dump(last_comment)
        else:
            return {"message": "User not found"}, 404

    @jwt_required
    def post(self):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            try:
                new_comment = comment_schema.load(request.get_json())
            except ValidationError as err:
                return err.messages, 400
            new_comment.login = user.login
            new_comment.comment_date = func.now()
            new_comment.save_to_db()

            possible_hashtags = HashtagModel.find_hashtags_in_text(new_comment.comment)
            if possible_hashtags:
                for hashtag in possible_hashtags:
                    existing_hashtag = HashtagModel.find_only_for_comment(hashtag, new_comment.post_id,new_comment.comment_id)
                    if not existing_hashtag:
                        hashtag_data = {"post_id": new_comment.post_id, "hashtag": hashtag, "comment_id": new_comment.comment_id}
                        new_hashtag = hashtag_schema.load(hashtag_data)
                        new_hashtag.save_to_db()
            return {"message": "Comment added successfully."}, 201
        else:
            return {"message": "User not found"}, 404



    @jwt_required
    def put(self, comment_id):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)

        if user:
            existing_comment = CommentModel.find_by_comment_id(comment_id)
            if existing_comment:
                if existing_comment.login == user.login:
                    try:
                        comment_to_update = comment_update_schema.load(request.get_json(), partial=True, instance=existing_comment)
                    except ValidationError as err:
                        return err.messages, 400
                    possible_hashtags = HashtagModel.find_hashtags_in_text(existing_comment.comment)
                    if possible_hashtags:
                        for hashtag in possible_hashtags:
                            existing_hashtag = HashtagModel.find_only_for_comment(hashtag, existing_comment.post_id,existing_comment.comment_id)
                            if not existing_hashtag:
                                hashtag_data = {"post_id": existing_comment.post_id, "hashtag": hashtag, "comment_id": existing_comment.comment_id}
                                new_hashtag = hashtag_schema.load(hashtag_data)
                                new_hashtag.save_to_db()
                    comment_to_update.save_to_db()
                    return {"message": "Comment updated successfully."}, 200
                else:
                    return {'message': 'It is not a comment of user logged in.'}, 404
        else:
            return {"message": "User not found"}, 404


    @jwt_required
    def delete(self, comment_id):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)

        if user:
            comment_to_be_deleted = CommentModel.find_by_comment_id(comment_id)
            if comment_to_be_deleted:
                if comment_to_be_deleted.login == user.login:
                    comment_to_be_deleted.delete_from_db()
                    return {'message': 'Comment deleted'}, 200
                else:
                    return {'message': 'It is not a comment of user logged in.'}, 404
        else:
            return {"message": "User not found"}, 404


class Comments(Resource):


    @jwt_required
    def get(self, post_id):

        return {'comments': [comment_schema.dump(x) for x in CommentModel.find_by_post_id(post_id)]}
