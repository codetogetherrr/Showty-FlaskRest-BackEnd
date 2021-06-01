from db import db
import re

from models.post import PostModel


class HashtagModel(db.Model):

    __tablename__ = 'hashtags'

    hashtag_id = db.Column(db.Integer,primary_key=True)
    hashtag = db.Column(db.String(80), nullable=False)
    post_id = db.Column(db.Integer, nullable=False)
    comment_id = db.Column(db.Integer)

    @classmethod
    def find_hashtags_in_text(cls, text):
        hashtags = re.findall(r"#(\w+)", text)
        return hashtags

    @classmethod
    def search_by_hashtag(cls, keyword):
        return cls.query.filter(HashtagModel.hashtag.like(keyword + "%")).distinct(cls.hashtag).all()

    @classmethod
    def get_items_with_hashtag(cls, hashtag):
        items = cls.query.filter_by(hashtag=hashtag).all()
        return items

    @classmethod
    def find_if_hashtag_exist(cls, hashtag):
        item = cls.query.filter_by(hashtag=hashtag).first()
        return item

    @classmethod
    def get_paginated_posts_for_hashtag(cls, hashtag, page):
        posts_with_hashtag = PostModel.query.join(cls, PostModel.post_id == cls.post_id).filter_by(hashtag=hashtag).order_by(PostModel.date.desc()).paginate(page=page, per_page=9, error_out=False)
        return posts_with_hashtag

    @classmethod
    def get_last_post_with_hashtag(cls, hashtag):
        last_post_with_hashtag = PostModel.query.join(cls, PostModel.post_id == cls.post_id).filter_by(hashtag=hashtag).order_by(PostModel.date.desc()).first()
        return last_post_with_hashtag

    @classmethod
    def get_hashtags_for_post(cls, post_id):
        items = cls.query.filter_by(post_id=post_id).all()
        return items

    @classmethod
    def find_only_for_post(cls, hashtag, post_id):
        hashtag = cls.query.filter_by(hashtag=hashtag, post_id=post_id, comment_id=None).first()
        return hashtag

    @classmethod
    def find_only_for_comment(cls, hashtag, post_id, comment_id):
        hashtag = cls.query.filter_by(hashtag=hashtag, post_id=post_id, comment_id=comment_id).first()
        return hashtag

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
