import os
from flask import Flask, request, jsonify
from flask_restful import Api
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token,jwt_refresh_token_required, create_refresh_token, get_jwt_identity, get_raw_jwt)
from datetime import timedelta
from werkzeug.security import check_password_hash
from resources.user import  User, UserConfirm, LoggedUser
from resources.user import UserFacebookRegisterLogin
from models.user import UserModel
from resources.user import Users
from resources.post import Post, Posts
from resources.feed import Feed
from resources.comment import Comment
from resources.comment import Comments
from resources.like import Like
from resources.like import Likes
from resources.follow import Follow
from resources.follow import Follows
from resources.hashtag import Hashtag, Hashtags
from resources.search import Search
from resources.search import SearchUser
from resources.subscribe import Subscribe, Subscriptions
from resources.message import Messages
from resources.message import UnreadMessages

from resources.conversations import Conversations



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = os.environ.get('JWT_SECRET_KEY', '')
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
api = Api(app)

jwt = JWTManager(app)
blacklist = set()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@app.route('/logout1', methods=['DELETE'])
@jwt_required
def logout1():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"message": "1st step of logging out successful"}), 200


@app.route('/logout2', methods=['DELETE'])
@jwt_refresh_token_required
def logout2():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"message": "Successfully logged out"}), 200


@jwt.expired_token_loader
def my_expired_token_callback():
    return jsonify({'message': 'The token has expired'}), 401


@app.route('/login', methods = ['POST'])
def login():
    login = request.json.get('login', None)
    password = request.json.get('password', None)
    user = UserModel.find_by_username(login)
    if user and check_password_hash(user.password, password):
        if user.activated:
            ret = {'access_token': create_access_token(identity=login, expires_delta=timedelta(seconds=int(os.environ.get('JWT_EXPIRATION_TIME', '')))),
                'refresh_token': create_refresh_token(identity=login)}
            return jsonify(ret), 200
        return jsonify({'message':'Account not active. Please activate via link sent to {}'.format(user.email)}), 400
    return jsonify({'message':'Login or password is not correct.'}), 404


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user, expires_delta=timedelta(seconds=int(os.environ.get('JWT_EXPIRATION_TIME', ''))),fresh=False)
    ret = {'access_token': new_token}
    return jsonify(ret), 200



api.add_resource(UserFacebookRegisterLogin, '/facebooklogin')
api.add_resource(UserConfirm, '/userconfirm/<int:user_id>')
api.add_resource(User, '/user', methods=['PUT', 'DELETE'], endpoint='getmodifydeleteuser')
api.add_resource(User, '/user/<user_login>', methods=['GET'], endpoint='getuser')
api.add_resource(User, '/user/register', methods=['POST'], endpoint='useregister')
api.add_resource(LoggedUser, '/loggeduser')
api.add_resource(Users, '/users')
api.add_resource(Post, '/post', methods=['GET', 'POST'], endpoint='creategetpost')
api.add_resource(Post, '/post/<post_id>', methods=['PUT', 'DELETE'], endpoint='modifydeletepost')
api.add_resource(Posts, '/posts/<user_login>/<int:page>', methods=['GET'], endpoint='getpageofposts')
api.add_resource(Posts, '/posts/<login>', methods=['POST'], endpoint='getnoofposts')
api.add_resource(Comment, '/comment/<int:comment_id>' , methods=['PUT', 'DELETE'], endpoint='modifydeletcomment')
api.add_resource(Comment, '/comment', methods=['POST'], endpoint='addcomment')
api.add_resource(Comment, '/comment/<post_id>', methods=['GET'], endpoint='getrecentcomment')
api.add_resource(Comments, '/comments/<post_id>')
api.add_resource(Like, '/like', methods=['POST'], endpoint='addlike')
api.add_resource(Like, '/like/<post_id>', methods=['GET'], endpoint='checklike')
api.add_resource(Likes, '/likes/<post_id>')
api.add_resource(Follow, '/follow', methods=['POST'], endpoint='addfollow')
api.add_resource(Follow, '/follow/<follower_login>/<followee_login>', methods=['GET'], endpoint='checkfollow')
api.add_resource(Follows, '/follows/<user_login>')
api.add_resource(Hashtags, '/hashtags')
api.add_resource(Hashtag, '/hashtag')
api.add_resource(Search, '/search')
api.add_resource(SearchUser, '/search_user')
api.add_resource(Subscribe, '/subscribe', methods=['POST'], endpoint='subscribe')
api.add_resource(Subscribe, '/subscribe/<hashtag>/<subscriber>', methods=['GET'], endpoint='checksubscription')
api.add_resource(Subscriptions, '/subscriptions/<hashtag>')
api.add_resource(Feed, '/feed/<int:page>/<int:per_page>')
api.add_resource(Messages, '/messages/<loginA>/<loginB>')
api.add_resource(UnreadMessages, '/unread_messages/<loginA>/<loginB>')
api.add_resource(Conversations, '/conversations', methods=['GET'], endpoint='getconversations')
api.add_resource(Conversations, '/conversation_with/<otherlogin>', methods=['DELETE'], endpoint='deleteconversation')


if __name__ == '__main__':
    from db import db
    from ma import ma

    db.init_app(app)
    ma.init_app(app)
    app.run(debug=True, threaded=True)
