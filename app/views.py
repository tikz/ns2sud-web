import datetime
import logging
import random
import string

import numpy as np
import pandas as pd
import requests
import json
import os

from flask import render_template, request, redirect, url_for, flash, abort, jsonify, Response
from flask_login import login_user, logout_user, current_user
from requests.auth import HTTPDigestAuth
from valve.source import a2s
from valve.steam.id import SteamID
from humanize import naturaltime
from pywebpush import webpush, WebPushException

from app import app, db, models, ns2plus_queries, cache
from app.ns2plus_db import Database
from app.oauth import OAuthSignIn

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def make_cache_key(*args, **kwargs):
    return request.url


@cache.cached(timeout=10, key_prefix='gameserver_status')
def gameserver_status():
    try:
        gameserver_address = (
            app.config['GAMESERVER_IP'], app.config['GAMESERVER_PORT'])
        with a2s.ServerQuerier(gameserver_address, timeout=1) as server:
            info = server.info()
            gameserver = {
                'map': info.values['map'],
                'slots': f'{info.values["player_count"]}/{info.values["max_players"]}',
                'status': True
            }
    except:
        gameserver = {'status': False}

    return gameserver


def get_stats(endpoint, filter, limit, page):
    response = {}

    with Database() as db:
        if endpoint == "matches":
            query = ns2plus_queries.MATCHES
            filters = [f'{filter}%', f'%{filter}%']
        elif endpoint == "players":
            query = ns2plus_queries.PLAYERS
            filters = [f'%{filter}%']
        else:
            return abort(404)

        limits = [(page - 1) * limit, limit]

        data = db.execute(ns2plus_queries.limit(
            query), filters + limits).fetchall()
        total_count = db.execute(
            ns2plus_queries.count(query), filters).fetchone()

        # Specific parsing per endpoint
        if endpoint == "matches":
            for row in data:
                m, s = divmod(row['roundLength'], 60)
                h, m = divmod(m, 60)
                row['roundLength'] = "%d:%02d:%02d" % (
                    h, m, s) if h else "%02d:%02d" % (m, s)
                row['roundDateH'] = naturaltime(datetime.datetime.strptime(
                    row['roundDate'], '%Y-%m-%d %H:%M:%S'))
        if endpoint == "players":
            for row in data:
                m, s = divmod(row['timePlayed'], 60)
                h, m = divmod(m, 60)
                row['timePlayed'] = "%d:%02d:%02d" % (h, m, s)
                row['name_list'] = f'{row["name_list"][:15]}...'
                row['lastSeenH'] = naturaltime(datetime.datetime.strptime(
                    row['lastSeen'], '%Y-%m-%d %H:%M:%S'))

        response['result'] = data

    response['total_count'] = total_count
    response['limit'] = limit
    response['total_pages'] = 1 + total_count // limit
    response['page'] = page

    return response


@app.route('/')
def index():
    matches = get_stats('matches', '', 8, 1)['result']
    return render_template('index.html', gameserver=gameserver_status(),
                           last_matches=matches)


@app.route('/admin')
def admin():
    if 'admin' not in current_user.permissions:
        return abort(404)
    last_notifications = models.Notification.query.order_by(
        models.Notification.date.desc()).limit(10)
    n_subs = len(models.Subscriber.query.all())

    has_admin_access = [u.discord_tag for u in models.User.query.filter(
        models.User.permissions.like("%admin%")).all()]
    has_notification_access = [u.discord_tag for u in models.User.query.filter(
        models.User.permissions.like("%notifications%")).all()]
    return render_template('admin.html', last_notifications=last_notifications,
                           n_subs=n_subs, has_admin_access=has_admin_access,
                           has_notification_access=has_notification_access)


@app.route('/admin/send_notification', methods=['POST'])
def send_notification():
    if current_user.is_anonymous:
        return abort(404)

    title = request.form['title']
    link = request.form['link']
    message = request.form['message']

    subscribers = models.Subscriber.query.all()

    for subscriber in subscribers:
        try:
            webpush(
                subscription_info=subscriber.subscription_json,
                data=json.dumps(
                    {'title': title, 'message': message, 'link': link}),
                vapid_private_key=app.config['VAPID_PRIVATE_KEY'],
                vapid_claims={
                    "sub": "mailto:push@ns2sud.com"
                }
            )
        except:
            pass

    notification = models.Notification(
        user=current_user, title=title, message=message, link=link,
        date=datetime.datetime.now())
    db.session.add(notification)
    db.session.commit()

    return redirect(url_for('admin'))


@app.route('/stats/match/<roundid>')
@cache.cached(timeout=300)
def match(roundid):
    roundid = int(roundid)
    if not roundid:
        return abort(404)

    data = {}
    with Database() as db:
        round_info = db.execute(ns2plus_queries.ROUND_INFO, roundid).fetchall()
        if not round_info:
            return abort(404)

        data.update(round_info[0])

        path = 'static/img/map_screenshots/'
        abs_path = os.path.join(os.path.dirname(__file__), path)
        for file in os.listdir(abs_path):
            if data['mapName'] in file:
                data['background'] = '/' + path + file
        if 'background' not in data:
            data['background'] = '/' + path + 'default.jpg'

    return render_template('match.html', data=data)


@app.route('/stats')
@cache.cached(timeout=30)
def stats():
    return render_template('stats.html')


@app.route('/stats/player/<steamid>')
@cache.cached(timeout=30)
def player(steamid):
    steamid = int(steamid)
    if not steamid:
        return abort(404)

    data = {}

    with Database() as db:
        player_stats = db.execute(
            ns2plus_queries.PLAYER_STATS, steamid).fetchall()
        if not player_stats:
            return abort(404)
        data.update(player_stats[0])

        player_other_names = db.execute(
            ns2plus_queries.PLAYER_OTHER_NAMES, steamid).fetchall()
        data['other_names'] = [x['playerName'] for x in player_other_names]

        player_weapon_acc = db.execute(
            ns2plus_queries.PLAYER_WEAPON_ACC, steamid).fetchall()
        data['weapon_acc'] = {x['weapon']: x['acc'] for x in player_weapon_acc}

        player_wins = pd.DataFrame(db.execute(
            ns2plus_queries.PLAYER_WINS, steamid).fetchall())

        data['steam_url'] = SteamID(
            int((data['steamId'] - 1) / 2), 1, 1, 0).community_url()

        # Winrate over time chart
        for team in (1, 2):
            df = player_wins[player_wins['teamNumber'] == team]
            shift = 30 - len(df) % 30
            df = df.groupby((np.arange(len(df)) + shift) //
                            30).agg({'win': ['sum', 'count'],
                                     'roundDate': ['last']})
            if len(df):
                df['winrate'] = df[('win', 'sum')] / df[('win', 'count')]
                data[f'team{team}_winrate'] = [
                    {'x': p[2], 'y': int(p[3] * 100)} for p in df.values]

        # Activity chart
        q = [(ns2plus_queries.PLAYER_ACTIVITY, 'activity', steamid),
             (ns2plus_queries.SERVER_ACTIVITY, 'server_activity', None)]
        for query, key, arg in q:
            if arg:
                q = db.execute(query, arg).fetchall()
            else:
                q = db.execute(query).fetchall()
            df = pd.DataFrame(q)
            df['Datetime'] = pd.to_datetime(df['roundDate'])
            df = df.set_index('Datetime')
            df = df.hoursPlayed.resample('W').sum()
            data[key] = [{'x': x.to_pydatetime().strftime('%Y-%m-%d %H:%M:%S'),
                          'y': '%.2f' % y}
                         for x, y in zip(list(df.index), list(df.values))]

        # Class time chart
        q = db.execute(ns2plus_queries.PLAYER_CLASSTIME, steamid).fetchall()
        data['classes'] = {c['class']: '%.2f' % c['classTime']
                           if c['classTime'] else 0 for c in q}
        lifeforms = ['Gorge', 'Lerk', 'Fade', 'Onos']
        lifeforms_time = [(l, float(data['classes'][l])) for l in lifeforms]
        data['lifeform'] = max(lifeforms_time, key=lambda x: x[1])[0]

    return render_template('player.html', data=data)


@app.route('/stats/global/json/kill_graph')
@cache.cached(timeout=300)
def kill_graph():
    with Database() as db:
        players = {}
        links_i = []
        links_v = []
        data = db.execute(ns2plus_queries.KILL_GRAPH).fetchall()
        for r in data:
            kfId = r['killerSteamId']
            vId = r['victimSteamId']
            kills = r['kills']
            if kfId not in players:
                players[kfId] = r['killerName']
            if vId not in players:
                players[vId] = r['victimName']

            if (kfId, vId) not in links_i and (vId, kfId) not in links_i:
                links_i.append((kfId, vId))
                links_v.append(kills)
            else:
                for pair in [(kfId, vId), (vId, kfId)]:
                    try:
                        i = links_i.index(pair)
                    except:
                        pass
                    else:
                        links_v[i] += kills
    response = {
        'nodes': [{'id': k, 'name': v} for k, v in players.items()],
        'links': [{'source': link[0], 'target':link[1], 'value':links_v[i]}
                  for i, link in enumerate(links_i)]

    }
    return jsonify(response)


@app.route('/stats/json/<endpoint>')
@cache.cached(timeout=30, key_prefix=make_cache_key)
def stats_json(endpoint):
    allowed_endpoints = ["matches", "players"]
    if endpoint not in allowed_endpoints:
        return abort(404)

    args = request.args
    filter = args.get('filter') if args.get('filter') else ''
    limit = int(args.get('limit')) if args.get('limit') else 10
    page = int(args.get('page')) if args.get('page') else 1

    response = get_stats(endpoint, filter, limit, page)

    return jsonify(response)


@app.route('/stats/global/json/matches_week')
@cache.cached(timeout=30)
def matches_week():
    with Database() as db:
        data = db.execute(ns2plus_queries.MATCHES_WEEK).fetchall()
        df = pd.DataFrame(data)
        df['Datetime'] = pd.to_datetime(df['roundDate'])
        df = df.set_index('Datetime')
        df = df.roundId.resample('W').count()
        response = [{'x': x.to_pydatetime().strftime('%Y-%m-%d %H:%M:%S'),
                     'y': int(y)}
                    for x, y in zip(list(df.index), list(df.values))]
        return jsonify(response)


@app.route('/stats/global/json/new_players')
@cache.cached(timeout=30)
def new_players():
    with Database() as db:
        data = db.execute(ns2plus_queries.NEW_PLAYERS).fetchall()
        df = pd.DataFrame(data)
        df['Datetime'] = pd.to_datetime(df['roundDate'])
        df = df.set_index('Datetime')
        df = df.steamId.resample('W').count()
        response = [{'x': x.to_pydatetime().strftime('%Y-%m-%d %H:%M:%S'),
                     'y': int(y)}
                    for x, y in zip(list(df.index), list(df.values))]
        return jsonify(response)


@app.route('/login')
def oauth_authorize():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn()
    return oauth.authorize()


@app.route('/user')
def user():
    if current_user.is_anonymous:
        return abort(404)

    with Database() as db:
        params = (current_user.discord_id, current_user.discord_tag,
                  current_user.discord_avatar, current_user.ns2_id)
        db.execute(ns2plus_queries.UPDATE_DISCORD_DATA, params)

    return render_template('user.html')


@app.route('/user/json/token_updated')
def token_changed():
    if current_user.is_anonymous:
        return abort(404)

    user = models.User.query.filter_by(id=current_user.id).first()
    try:
        timestamp = user.token_used.timestamp()
    except:
        timestamp = 0
    return jsonify({'token_updated': timestamp})


@app.route('/user/kick')
def kick():
    if current_user.is_anonymous:
        return abort(404)

    auth = HTTPDigestAuth(
        app.config['GAMESERVER_WEB_USER'], app.config['GAMESERVER_WEB_PASS'])
    try:
        params = {
            'request': 'json',
            'command': 'Send',
            'rcon': f'sv_kick {current_user.ns2_id} Crash (kick requested from web)'
        }
        requests.get(app.config['GAMESERVER_WEB_HOST'],
                     auth=auth, params=params).json()
    except Exception as e:
        logging.error(f"KICK Error: {repr(e)}")
        flash('An error has occurred.')
    else:
        flash('The kick command was sent to the server.')

    return redirect(url_for('index'))


@app.route('/login/callback')
def oauth_callback():
    oauth = OAuthSignIn()
    discord_id, discord_tag, discord_avatar, discord_locale = oauth.callback()
    if discord_id is None:
        flash('Discord authentication failed.')
        return redirect(url_for('index'))
    user = models.User.query.filter_by(discord_id=discord_id).first()

    if not user:
        while True:
            token = app.config['LINK_PREFIX'] + \
                ''.join(random.choices(
                    string.ascii_lowercase + string.digits, k=5))
            token_exists = models.User.query.filter_by(token=token).first()
            if not token_exists:
                break
        user = models.User(discord_id=discord_id, discord_tag=discord_tag,
                           discord_avatar=discord_avatar,
                           discord_locale=discord_locale,
                           created=datetime.datetime.now(), token=token)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/notifications/subscribe', methods=['POST', 'GET'])
def notifications_subscribe():
    if current_user.is_anonymous:
        return abort(404)

    data = request.get_json()
    if data:
        endpoint = data['endpoint']
        keys = data['keys']

        sub_exists = models.Subscriber.query.filter_by(
            endpoint=endpoint).first()

        if not sub_exists:
            print(current_user, endpoint, json.dumps(keys))
            sub = models.Subscriber(
                user=current_user, endpoint=endpoint, keys=json.dumps(keys))
            db.session.add(sub)
            db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})


@app.route('/notifications/unsubscribe', methods=['POST', 'GET'])
def notifications_unsubscribe():
    if current_user.is_anonymous:
        return abort(404)

    data = request.get_json()
    if data:
        endpoint = data['endpoint']

        sub = models.Subscriber.query.filter_by(
            endpoint=endpoint).first()

        if sub:
            db.session.delete(sub)
            db.session.commit()
            return jsonify({'success': True})
    return jsonify({'success': False})


# Static files that need root path
@app.route('/sw.js')
def sw():
    return app.send_static_file('js/sw.js')


@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')
