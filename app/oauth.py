import json

from flask import current_app, url_for, request, redirect
from rauth import OAuth2Service


class OAuthSignIn(object):
    providers = None

    def __init__(self):
        self.provider_name = 'discord'
        credentials = current_app.config['OAUTH_CREDENTIALS']['discord']
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']
        self.service = OAuth2Service(
            name='discord',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://discordapp.com/api/oauth2/authorize',
            access_token_url='https://discordapp.com/api/oauth2/token',
            base_url='https://discordapp.com/api/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='identify',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None, None

        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )

        user = oauth_session.get('users/@me').json()
        avatar = f'https://cdn.discordapp.com/avatars/{user["id"]}/{user["avatar"]}.png'
        return user['id'], user["username"] + '#' + user['discriminator'], avatar, user['locale']

    def get_callback_url(self):
        return url_for('oauth_callback', _external=True)
