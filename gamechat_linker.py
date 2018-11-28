import datetime
import logging
import random
import string

import requests
import time
from requests.auth import HTTPDigestAuth
from valve.steam.id import SteamID

from app import app, db, models

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logging.info('Gamechat linker started')
while True:
    auth = HTTPDigestAuth(
        app.config['GAMESERVER_WEB_USER'], app.config['GAMESERVER_WEB_PASS'])
    try:
        r = requests.get(
            app.config['GAMESERVER_WEB_HOST'] + '/?request=getchatlist', auth=auth).json()
    except:
        pass
    else:
        for msg in r:
            if app.config['LINK_PREFIX'] in msg['message']:
                token = msg['message'].strip()
                user = models.User.query.filter_by(token=token).first()
                if user:
                    if token == user.token:
                        user.ns2_id = msg['steamId']
                        user.steam_id = int((msg['steamId'] - 1) / 2)
                        user.steam_url = SteamID(
                            user.steam_id, 1, 1, 0).community_url()
                        user.token_used = datetime.datetime.now()

                        while True:
                            new_token = app.config['LINK_PREFIX'] + ''.join(
                                random.choices(string.ascii_lowercase + string.digits, k=5))
                            token_exists = models.User.query.filter_by(
                                token=new_token).first()
                            if not token_exists:
                                break
                        user.token = new_token

                        db.session.commit()
                        logging.info(f'User {user.discord_tag} used token {token}.'
                                     f' Updated steamId: {user.steam_id} (new token: {new_token})')

    time.sleep(5)
