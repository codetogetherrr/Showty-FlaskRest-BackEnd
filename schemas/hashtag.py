from ma import ma
from models.hashtag import HashtagModel


class HashtagSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = HashtagModel
        exclude = ("hashtag_id",)
        load_instance = True
