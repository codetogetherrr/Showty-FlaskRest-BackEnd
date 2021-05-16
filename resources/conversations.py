from flask_restful import Resource
from models.message import MessageModel
from schemas.message import MessageSchema


message_schema = MessageSchema()


class Conversations(Resource):
    def get(self, login):


        return {'conversations': [{'with': x.receiver,  'latest_message': message_schema.dump(MessageModel.get_latest_for_pair(x.receiver, login))} for x in MessageModel.find_conversation_addressees(login)]}