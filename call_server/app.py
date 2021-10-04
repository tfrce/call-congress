import os
import logging

from flask import Flask, g, request, session
from flask.ext.assets import Bundle

from utils import json_markup, OrderedDictYAMLLoader
import yaml

import config

from .site import site
from .admin import admin
from .user import User, user
from .call import call
from .campaign import campaign
from .api import api, configure_restless, restless_preprocessors

from extensions import cache, db, babel, assets, login_manager, csrf, mail, store, rest

DEFAULT_BLUEPRINTS = (
    site,
    admin,
    user,
    call,
    campaign,
    api,
)


def create_app(configuration=None, app_name=None, blueprints=None):
    """Create the main Flask app."""

    if app_name is None:
        app_name = config.DefaultConfig.APP_NAME
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name)
    # configure app from object or environment
    configure_app(app, configuration)
    # init extensions once we have app context
    init_extensions(app)
    # then blueprints, for url/view routing
    register_blueprints(app, blueprints)

    configure_logging(app)

    # then extension specific configurations
    configure_babel(app)
    configure_login(app)
    configure_assets(app)
    configure_restless(app)

    # finally instance specific configurations
    context_processors(app)
    instance_defaults(app)

    app.logger.info('Call Power started')
    return app


def configure_app(app, configuration=None):
    """Configure app by object, instance folders or environment variables"""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(config.DefaultConfig)
    if configuration:
        app.logger.info('Config: %s' % configuration)
        app.config.from_object(configuration)
    else:
        config_name = '%s_CONFIG' % config.DefaultConfig.PROJECT.upper()
        env_config = os.environ.get(config_name)
        if env_config:
            app.logger.info('Config: %s' % config_name)
            app.config.from_object(env_config)
    app.logger.info('Environment: %s' % app.config['ENVIRONMENT'])


def init_extensions(app):
    db.init_app(app)
    db.app = app
    db.metadata.naming_convention = {
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
    # set constraint naming convention to sensible default, per
    # http://docs.sqlalchemy.org/en/rel_0_9/core/constraints.html#configuring-constraint-naming-conventions

    assets.init_app(app)
    assets.app = app
    babel.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    store.init_app(app)
    rest.init_app(app, flask_sqlalchemy_db=db,
                  preprocessors=restless_preprocessors)
    rest.app = app

    if app.config.get('DEBUG'):
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)


def register_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_babel(app):
    @babel.localeselector
    def get_locale():
        # TODO, first check user config?
        g.accept_languages = app.config.get('ACCEPT_LANGUAGES')
        accept_languages = g.accept_languages.keys()
        browser_default = request.accept_languages.best_match(accept_languages)
        if 'language' in session:
            language = session['language']
            # current_app.logger.debug('lang from session: %s' % language)
            if language not in accept_languages:
                # clear it
                # current_app.logger.debug('invalid %s, clearing' % language)
                session['language'] = None
                language = browser_default
        else:
            language = browser_default
            # current_app.logger.debug('lang from browser: %s' % language)
        session['language'] = language  # save it to session

        # and to user model?
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
                       'bower_components/backbone-filtered-collection/backbone-filtered-collection.js',
                       'bower_components/html.sortable/dist/html.sortable.min.js',
                       'bower_components/bootstrap-datepicker/dist/js/bootstrap-datepicker.js',
                       filters='rjsmin', output='dist/js/vendor.js')
    assets.register('vendor_js', vendor_js)

    vendor_css = Bundle('bower_components/bootstrap/dist/css/bootstrap.css',
                        'bower_components/bootstrap/dist/css/bootstrap-theme.css',
                        'bower_components/bootstrap-datepicker/dist/css/bootstrap-datepicker.css',
                        filters='cssmin', output='dist/css/vendor.css')
    assets.register('vendor_css', vendor_css)

    audio_js = Bundle('bower_components/volume-meter/volume-meter.js',
                      'bower_components/audioRecord/src/audioRecord.js',
                      filters='rjsmin', output='dist/js/vendor_audio.js')
    assets.register('audio_js', audio_js)

    graph_js = Bundle('bower_components/highcharts/highcharts.js',
                      'bower_components/chartkick/chartkick.js',
                      filters='rjsmin', output='dist/js/graph.js')
    assets.register('graph_js', graph_js)

    site_js = Bundle('scripts/site.js', 'scripts/site/*.js',
                     output='dist/js/site.js')
    assets.register('site_js', site_js)

    site_css = Bundle('styles/*.css',
                      filters='cssmin', output='dist/css/site.css')
    assets.register('site_css', site_css)
    app.logger.info('registered assets %s' % assets._named_bundles.keys())


def context_processors(app):
    # inject sitename into all templates
    @app.context_processor
    def inject_sitename():
        return dict(SITENAME=app.config.get('SITENAME', 'CallPower'))

    @app.context_processor
    def inject_openstates_key():
        return dict(OPENSTATES_API_KEY=app.config.get('OPENSTATES_API_KEY', ''))

    # json filter
    app.jinja_env.filters['json'] = json_markup
    app.jinja_env.add_extension('call_server.jinja.SelectiveHTMLCompress')


def instance_defaults(app):
    with app.open_instance_resource('campaign_field_descriptions.yaml') as f:
        app.config.CAMPAIGN_FIELD_DESCRIPTIONS = yaml.load(f.read(), Loader=OrderedDictYAMLLoader)
    with app.open_instance_resource('campaign_msg_defaults.yaml') as f:
        app.config.CAMPAIGN_MESSAGE_DEFAULTS = yaml.load(f.read(), Loader=OrderedDictYAMLLoader)


def configure_logging(app):
    if app.config.get('DEBUG_INFO'):
        app.logger.setLevel(logging.INFO)
    elif app.config.get('DEBUG'):
        app.logger.setLevel(logging.WARNING)
    else:
        app.logger.setLevel(logging.ERROR)
    
    if app.config.get('OUTPUT_LOG'):
        app.logger.addHandler(logging.StreamHandler())
