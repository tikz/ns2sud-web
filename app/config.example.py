import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    VAPID_PUBLIC_KEY = ''
    VAPID_PRIVATE_KEY = ''

    NS2PLUS_MYSQL_HOST = ''
    NS2PLUS_MYSQL_USER = ''
    NS2PLUS_MYSQL_PASS = ''
    NS2PLUS_MYSQL_DB = ''

    GAMESERVER_IP = ''
    GAMESERVER_PORT = 27016
    GAMESERVER_WEB_HOST = f'http://{GAMESERVER_IP}:8008'
    GAMESERVER_WEB_USER = ''
    GAMESERVER_WEB_PASS = ''

    LINK_PREFIX = 'web-'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pass@host/db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'random_string'
    SECURITY_PASSWORD_SALT = 'random_string'
    SECURITY_USER_IDENTITY_ATTRIBUTES = 'username'
    OAUTH_CREDENTIALS = {
        'discord': {
            'id': '',
            'secret': ''
        }
    }
