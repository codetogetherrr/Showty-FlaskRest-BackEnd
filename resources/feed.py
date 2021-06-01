from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.hashtag import HashtagModel
from models.follow import  FollowModel
from models.user import UserModel
from models.post import PostModel
from models.subscribe import SubscribeModel


from schemas.post import PostSchema

post_schema = PostSchema()


class Feed(Resource):

    @jwt_required
    def get(self, page, per_page):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)

        if user:
            posts_of_followees = PostModel.query \
                .join(FollowModel, FollowModel.followee_login == PostModel.login) \
                .filter_by(follower_login=login)

            posts_of_hashtag = PostModel.query \
                .join(HashtagModel, PostModel.post_id == HashtagModel.post_id)\
                .join(SubscribeModel, SubscribeModel.hashtag == HashtagModel.hashtag) \
                .filter_by(subscriber=login) \

            posts_of_feed = posts_of_followees.union(posts_of_hashtag).order_by(PostModel.date.desc()).paginate(page=page, per_page=per_page, error_out=False)


            return {'posts_of_feed': [post_schema.dump(x) for x in posts_of_feed.items]}

        else:

            return {"message": "User not found"}, 404