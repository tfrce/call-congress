#TODO, figure out how to load gevent monkey patch only in production
# try:
#     from gevent.monkey import patch_all
#     patch_all()
# except ImportError:
#     if not DEBUG:
#         print "unable to apply gevent monkey.patch_all"

import logging

from flask import Flask, g, request, session
from flask.ext.assets import Bundle

from utils import json_markup

from .config import DefaultConfig

from .site import site
from .admin import admin
from .user import User, user
from .call import call
from .campaign import campaign
from .api import api

from extensions import cache, db, babel, assets, login_manager, csrf

DEFAULT_BLUEPRINTS = (
    site,
    admin,
    user,
    call,
    campaign,
    api
)


def create_app(config=None, app_name=None, blueprints=None):
    """Create the main Flask app."""

    if app_name is None:
        app_name = DefaultConfig.APP_NAME
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name)
    # configure app from object or environment
    configure_app(app, config)
    # init extensions once we have app context
    init_extensions(app)
    # then blueprints, for url/view routing
    register_blueprints(app, blueprints)

    configure_logging(app)

    # then extension specific configurations
    configure_babel(app)
    configure_login(app)
    configure_assets(app)

    context_processors(app)

    app.logger.info('call_server started')
    app.logger.info('db at %s' % db.engine.url)
    return app


def configure_app(app, config=None):
    """Configure app by object, instance folders or environment variables"""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)
    if config:
        app.config.from_object(config)

    # http://flask.pocoo.org/docs/config/#instance-folders
    # app.config.from_pyfile('instance/app.cfg')

    # app.config.from_envvar('%s_APP_CONFIG' % DefaultConfig.PROJECT.upper(), silent=True)


def init_extensions(app):
    db.init_app(app)
    db.app = app

    assets.init_app(app)
    babel.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    if app.config.get('DEBUG'):
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)


def register_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_babel(app):
    @babel.localeselector
    def get_locale():
        #TODO, first check user config?
        g.accept_languages = app.config.get('ACCEPT_LANGUAGES')
        accept_languages = g.accept_languages.keys()
        browser_default = request.accept_languages.best_match(accept_languages)
        if 'language' in session:
            language = session['language']
            #current_app.logger.debug('lang from session: %s' % language)
            if not language in accept_languages:
                #clear it
                #current_app.logger.debug('invalid %s, clearing' % language)
                session['language'] = None
                language = browser_default
        else:
            language = browser_default
            #current_app.logger.debug('lang from browser: %s' % language)
        session['language'] = language  # save it to session

        #and to user model?
        return language


def configure_login(app):
    login_manager.login_view = 'user.login'
    login_manager.refresh_view = 'user.reauth'
    login_manager.session_protection = 'basic'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)


def configure_assets(app):
    vendor_js = Bundle('bower_components/jquery/dist/jquery.min.js',
                       'bower_components/bootstrap/dist/js/bootstrap.min.js',
                       'bower_components/underscore/underscore-min.js',
                       'bower_components/backbone/backbone.js',
                       filters='rjsmin', output='dist/js/vendor.js')
    assets.register('vendor_js', vendor_js)

    vendor_css = Bundle('bower_components/bootstrap/dist/css/bootstrap.css',
                        'bower_components/bootstrap/dist/css/bootstrap-theme.css',
                        filters='cssmin', output='dist/css/vendor.css')
    assets.register('vendor_css', vendor_css)

    site_js = Bundle('scripts/*.js',
                     filters='rjsmin', output='dist/css/site.js')
    assets.register('site_js', site_js)

    site_css = Bundle('styles/*.css',
                      filters='cssmin', output='dist/css/site.css')
    assets.register('site_css', site_css)
    app.logger.info('registered assets %s' % assets._named_bundles.keys())


def context_processors(app):
    # inject sitename into all templates
    @app.context_processor
    def inject_sitename():
        return dict(SITENAME=app.config.get('SITENAME', 'Call Power'))

    @app.context_processor
    def inject_sunlight_key():
        return dict(SUNLIGHT_API_KEY=app.config.get('SUNLIGHT_API_KEY', ''))

    # json filter
    app.jinja_env.filters['json'] = json_markup


def configure_logging(app):
    if app.config.get('DEBUG_INFO'):
        app.logger.setLevel(logging.INFO)
    elif app.config.get('DEBUG'):
        app.logger.setLevel(logging.WARNING)
    else:
        app.logger.setLevel(logging.ERROR)
