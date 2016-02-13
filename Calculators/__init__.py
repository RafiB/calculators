#!/usr/bin/python

from flask import (
    Flask,
    g,
    render_template,
)

from flask.ext.sqlalchemy import SQLAlchemy

from werkzeug.contrib.fixers import ProxyFix


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /helpdesk;
        }

    :param app: the WSGI application
    '''
    def __init__(self, this_app):
        self.app = this_app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme

        server = environ.get('HTTP_X_FORWARDED_SERVER', '')
        if server:
            environ['HTTP_HOST'] = server

        return self.app(environ, start_response)

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config.from_object('Calculators.default_settings')
app.config.from_envvar('CALCULATORS_RELEVANCE_SETTINGS', silent=True)

db = SQLAlchemy(app)
app.db = db

# Get real remote IP, which is fiddled with by nginx's proxy-pass
app.wsgi_app = ProxyFix(app.wsgi_app)

# From http://flask.pocoo.org/snippets/35/
# I might love Peter Hansen
# This lets you run a flask app on some URL path other than / on a webserver.
app.wsgi_app = ReverseProxied(app.wsgi_app)


def do_register_views():
    from Calculators import views
    views.register_views()
do_register_views()


@app.errorhandler(404)
def page_not_found(e):
  ''' Custom 404 page. Muuuuch prettier. '''
  return render_template('404.html'), 404


@app.before_request
def define_form_addons():
    g.group_before = {
        'currency': '$'
    }

    g.group_after = {
        'percentage': '%',
        'kg': 'kg',
        'metres': 'm'
    }


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
    return instance


@app.before_first_request
def init_db():
    app.db.create_all()

    from Calculators.models import Calculator, Tag
    BMI_calc = get_or_create(app.db.session, Calculator, template='BMI.formula',
                             name='Body Mass Index')

    compound_interest_calc = get_or_create(app.db.session, Calculator,
                                           template='compound_interest.formula',
                                           name='Compound Interest')

    for t in ['health', 'weight', 'fat', 'body', 'mass', 'index', 'BMI']:
        tag = get_or_create(app.db.session, Tag, name=t)
        BMI_calc.tags.add(tag)

    for t in ['finance', 'money', 'compound', 'interest']:
        tag = get_or_create(app.db.session, Tag, name=t)
        compound_interest_calc.tags.add(tag)

    app.db.session.commit()
