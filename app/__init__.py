from flask import Flask, g, request
from flask_babel import Babel
from flask_caching import Cache
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_humanize import Humanize
from flask_minify import minify

from app.config import Config

app = Flask(__name__)

app.config.from_object(Config)
minify(app=app)

babel = Babel(app)

db = SQLAlchemy(app)
humanize = Humanize(app)
login_manager = LoginManager(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))

from app import views, models
