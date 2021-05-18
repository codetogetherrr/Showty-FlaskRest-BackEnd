from ma import ma
from models.follow import FollowModel


class FollowSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = FollowModel
        dump_only = ("follower_id",)
        exclude = ("follow_id",)
        load_instance = True

