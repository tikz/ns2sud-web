# -*- coding: utf-8 -*-

from app import app
from flask import render_template, session, request, redirect, url_for, abort, make_response

@app.route('/motd')
def index():
    a_langs = request.accept_languages
    language = None
    if 'es' in a_langs:
        language = 'es'
    elif 'pt' in a_langs:
        language = 'pt'
    else:
        language = 'en'
    return render_template('motd.html', lang=language)
