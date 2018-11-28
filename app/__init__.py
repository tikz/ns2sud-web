from flask import Flask
from flask_caching import Cache
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_humanize import Humanize

from app.config import Config

app = Flask(__name__)

app.config.from_object(Config)


db = SQLAlchemy(app)
humanize = Humanize(app)
login_manager = LoginManager(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))

from app import views, models
