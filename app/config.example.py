import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    NS2PLUS_MYSQL_HOST = ''
    NS2PLUS_MYSQL_USER = ''
    NS2PLUS_MYSQL_PASS = ''
    NS2PLUS_MYSQL_DB = 'wonitor_ns2plus'

    GAMESERVER_IP = ''
    GAMESERVER_PORT = 27016
    GAMESERVER_WEB_HOST = f'http://{GAMESERVER_IP}:8008'
    GAMESERVER_WEB_USER = ''
    GAMESERVER_WEB_PASS = ''

    LINK_PREFIX = 'web-'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'change'
    SECURITY_PASSWORD_SALT = 'change'
    SECURITY_USER_IDENTITY_ATTRIBUTES = 'username'
    OAUTH_CREDENTIALS = {
        'discord': {
            'id': '',
            'secret': ''
        }
    }
