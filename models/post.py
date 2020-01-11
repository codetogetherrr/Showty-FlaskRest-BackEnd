from db import db
from flask import jsonify
from flask_sqlalchemy import BaseQuery
from flask_paginate import Pagination

class PostModel(db.Model):

    __tablename__ = 'posts'

    post_id = db.Column(db.Integer,primary_key=True)
    image_id = db.Column(db.String(200), nullable=False)
    image_width = db.Column(db.Integer, nullable=False)
    image_height = db.Column(db.Integer, nullable=False)
    login = db.Column(db.String(80))
    description = db.Column(db.String(80))
    date = db.Column(db.DateTime)

    @classmethod
    def find_by_username(cls, login,page):
        user_list = cls.query.filter_by(login=login).order_by(PostModel.date.desc()).paginate(page=page, per_page=9, error_out=False)
        return user_list

    @classmethod
    def find_by_post_id(cls, post_id):
        return cls.query.filter_by(post_id=post_id).first()

    @classmethod
    def find_last_post_login_user(cls, login):
        login_user_post = cls.query.filter_by(login=login).order_by(PostModel.date.desc()).first()
        return login_user_post
    
    @classmethod
    def count_post_login(cls, login):
        count_post = cls.query.filter_by(login=login).count()
        return count_post
    
    def json(self):
        return {'post_id' : self.post_id,\
                'image_id': self.image_id,\
                'image_width': self.image_width,\
                'image_height': self.image_height,\
                'login' : self.login,\
                'description' : self.description,\
                'date': self.date
                }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
