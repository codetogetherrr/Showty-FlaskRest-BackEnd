from ma import ma
from models.user import UserModel

class UserUpdateSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = UserModel
        load_only = ("password", "image_id", "image_width", "image_height", "activated")
        dump_only = ("activated",)
        exclude = ("password", "id", "email", "login")
        load_instance = True



class UserSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = UserModel
        load_only = ("password", )
        dump_only = ("activated",)
        exclude = ("id",)
        load_instance = True

