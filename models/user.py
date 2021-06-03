import os
from db import db
from flask import request, url_for
from requests import Response, post
from time import time
import jwt


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True)
    login=db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fullname = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True, nullable=False)
    telephone = db.Column(db.String(80))
    description = db.Column(db.String(150))
    gender = db.Column(db.String(10))
    image_id = db.Column(db.String(80))
    image_height = db.Column(db.Integer)
    image_width = db.Column(db.Integer)
    activated = db.Column(db.Boolean, default=False)


    @classmethod
    def list_all_logins(cls):
        logins = []
        users = cls.query.all()
        for user in users:
            logins.append(user.login)
        return logins
    @classmethod
    def find_by_username(cls, login):
        return cls.query.filter_by(login=login).first()

    @classmethod
    def search_by_username(cls, keyword):
        return cls.query.filter(UserModel.login.like(keyword + "%")).all()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def create_confirmation_token(self):
        return jwt.encode(
            {'user_confirmation': self.login, 'exp': time() + os.environ.get('JWT_CONFIRMING_EXPIRATION_TIME', '')},
            os.environ.get('JWT_CONFIRMING_SECRET_KEY', ''), algorithm='HS256')


    def send_conf_email(self) -> Response:

        token = self.create_confirmation_token
        link = request.url_root[0:-1] + url_for("confirm_user_registration", token=token)

        return post(
            f"{os.environ.get('MAILGUN_BASE_URL','')}/messages",
            auth=("api", f"{os.environ.get('MAILGUN_API_KEY','')}"),
            data={"from": f"{os.environ.get('MAILGUN_EMAIL','')}",
                "to": self.email,
                "subject": "Registration confirmation",
                "text": f"Please click the link to confirm your registration: {link}",
            },
        )
