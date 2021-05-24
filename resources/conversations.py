from flask_restful import Resource
from models.message import MessageModel
from models.user import UserModel
from schemas.message import MessageSchema
from flask_jwt_extended import jwt_required, get_jwt_identity


message_schema = MessageSchema()


class Conversations(Resource):

    @jwt_required
    def get(self):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:

            return {'conversations': [{'with': x.receiver,  'latest_message': message_schema.dump(MessageModel.get_latest_for_pair(x.receiver, login))} for x in MessageModel.find_conversation_addressees(login)]}
        else:
            return {"message": "User not found"}, 404

    @jwt_required
    def delete(self, otherlogin):

        login = get_jwt_identity()
        user = UserModel.find_by_username(login)
        if user:
            messages_to_delete = MessageModel.find_by_pair(login,otherlogin)
            if messages_to_delete:
                for message in messages_to_delete:
                    message.delete_from_db()

                return {'message': 'Conversation deleted'}, 200

        else:
            return {"message": "User not found"}, 404