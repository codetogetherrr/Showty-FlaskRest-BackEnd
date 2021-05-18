from ma import ma
from models.comment import CommentModel


class CommentSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = CommentModel
        dump_only = ("comment_date", "comment_id", "login")
        load_instance = True



class CommentUpdateSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = CommentModel
        exclude = ("comment_date", "comment_id", "login", "post_id")
        load_instance = True