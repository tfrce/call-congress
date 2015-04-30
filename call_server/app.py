try:
    from gevent.monkey import patch_all
    patch_all()
except ImportError:
    print "unable to apply gevent monkey.patch_all"

from flask import Flask
from flask.ext.assets import Bundle

from .config import DefaultConfig
from .admin import admin
from .user import user
from .call import call
from .campaign import campaign
from .api import api

from extensions import cache, db, assets

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
    app.config.from_object('call_server.config.DefaultConfig')

    configure_extensions(app)
    configure_blueprints(app, blueprints)
    configure_assets(app)

    app.logger.info('call_server started')
    return app


def configure_extensions(app):
    db.init_app(app)
    cache.init_app(app)
    assets.init_app(app)


def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_assets(app):
    vendor_js = Bundle('bower_components/jquery/dist/jquery.js',
                       'bower_components/bootstrap/dist/js/bootstrap.min.js',
                       filters='rjsmin', output='static/js/vendor.js')
    assets.register('vendor_js', vendor_js)
