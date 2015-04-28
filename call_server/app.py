try:
    from gevent.monkey import patch_all
    patch_all()
except ImportError:
    print "unable to apply gevent monkey.patch_all"

from flask import Flask

from .config import Config
from .admin import admin
from .user import user
from .call import call
from .campaign import campaign
from .api import api

from extensions import cache, db


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
        app_name = Config.PROJECT_NAME
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name)
    app.config.from_object('config.ConfigProduction')

    configure_extensions(app)
    configure_blueprints(app)

    app.logger.info('application started')
    return app


def configure_extensions(app):
    db.init_app(app)
    cache.init_app(app)


def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
