from ma import ma
from models.subscribe import SubscribeModel


class SubscribeSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = SubscribeModel
        dump_only = ("subscription_id",)
        exclude = ("subscription_id",)
        load_instance = True
