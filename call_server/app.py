#TODO, figure out how to load gevent monkey patch only in production
# try:
#     from gevent.monkey import patch_all
#     patch_all()
# except ImportError:
#     if not DEBUG:
#         print "unable to apply gevent monkey.patch_all"

from flask import Flask, g, request, session
from flask.ext.assets import Bundle

from .config import DefaultConfig
from .admin import admin
from .user import user
from .call import call
from .campaign import campaign
from .api import api

from extensions import cache, db, babel, assets, login_manager

DEFAULT_BLUEPRINTS = (
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
    configure_app(app, config)

    # init extensions once we have app context
    init_extensions(app)
    # then blueprints, for url/view routing
    register_blueprints(app, blueprints)

    # then extension specific configurations
    configure_babel(app)
    configure_login(app)
    configure_assets(app)

    app.logger.info('call_server started')
    return app


def configure_app(app, config=None):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)

    # http://flask.pocoo.org/docs/config/#instance-folders
    # app.config.from_pyfile('instance/app.cfg')

    if config:
        app.config.from_object(config)

    # Use instance folder instead of env variables to make deployment easier.
    #app.config.from_envvar('%s_APP_CONFIG' % DefaultConfig.PROJECT.upper(), silent=True)


def init_extensions(app):
    db.init_app(app)
    babel.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    assets.init_app(app)


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
    login_manager.login_view = "user.login"


def configure_assets(app):
    vendor_js = Bundle('bower_components/jquery/dist/jquery.js',
                       'bower_components/bootstrap/dist/js/bootstrap.min.js',
                       filters='rjsmin', output='static/js/vendor.js')
    assets.register('vendor_js', vendor_js)
