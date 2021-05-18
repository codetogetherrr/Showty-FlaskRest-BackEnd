from ma import ma
from models.message import MessageModel


class MessageSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = MessageModel
        dump_only = ("sender", "receiver", "text", "sentAt", "id", "read", "url")
        load_instance = True

