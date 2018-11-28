import json

from flask_login import UserMixin

from app import db

if __name__ == "__main__":
    db.metadata.clear()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(255))
    discord_tag = db.Column(db.String(255))
    discord_avatar = db.Column(db.String(255))
    discord_locale = db.Column(db.String(20))
    created = db.Column(db.DateTime())
    ns2_id = db.Column(db.String(255))
    steam_id = db.Column(db.String(255))
    steam_url = db.Column(db.String(255))
    token = db.Column(db.String(255))
    token_used = db.Column(db.DateTime())


class Subscriber(db.Model):
    id = db.Column(db.Integer(), primary_key=True, default=None)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    endpoint = db.Column(db.String(255))
    keys = db.Column(db.String(255))
    user = db.relationship("User")

    @property
    def subscription_json(self):
        return {'endpoint': self.endpoint, 'keys': json.loads(self.keys)}


class Notification(db.Model):
    id = db.Column(db.Integer(), primary_key=True, default=None)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    title = db.Column(db.String(255))
    message = db.Column(db.String(255))
    link = db.Column(db.String(255))
    date = db.Column(db.DateTime())
    user = db.relationship("User")

    @property
    def subscription_json(self):
        return {'endpoint': self.endpoint, 'keys': json.loads(self.keys)}


if __name__ == "__main__":
    db.create_all()
