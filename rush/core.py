# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, Response, redirect, url_for

from flask_heroku import Heroku
from flask_sslify import SSLify
from raven.contrib.flask import Sentry
from flask.ext.celery import Celery

from .data import table
from .cnam import phone, clean

app = Flask(__name__)

heroku = Heroku(app)
sentry = Sentry(app)
sslify = SSLify(app)
celery = Celery(app)

app.debug = True

@app.route('/')
def describe_api():
    """Returns a description of the API."""

    descr = {
        'resources': {
            '/numbers/:number': 'Returns data about the given number.',
            '/areas/:area': 'Returns data about a given area code.',
            '/areas/:area/:exchange': 'Returns data about a given exchange.',
            '/normalize?number=:number': 'Returns a normalized Phone number.'
        }
    }
    return jsonify(descr)


def update_number(number):
    namespace = 'numbers:{0}'.format(number)

    p, status = phone(number)
    if status == 200:
        table[namespace]['number'] = p['number']
        table[namespace]['cnam'] = p['cnam']
        table[namespace]['success'] = True



@app.route('/numbers/<number>')
def number_info(number):

    # Sanity check.
    if len(number) != 10:
        return 'Invalid length.', 400

    namespace = 'numbers:{0}'.format(number)
    t = table[namespace]
    if (not t.get('success')) or 'force' in request.args:
        t = update_number(number)
        j, s = phone(number)
        j['number'] = number
        j['success'] = False
        j['cnam'] = None
        return jsonify(number=j), s
        # return redirect(url_for('number_info', number=number))

    else:

        data = {
            'number': t['number'],
            'cnam': t['cnam'] or None
        }
        return jsonify(number=data)


def area_code():
    pass

def area_exchange():
    pass

@app.route('/normalize')
def normalize_number():
    number = clean(request.args.get('number'))

    if number:
        return redirect(url_for('number_info', number=number))
    else:
        return '', 404
