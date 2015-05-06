import os
import sys
import subprocess
from functools import wraps

from flask.ext.script import Manager
from alembic import command
from alembic.config import Config
from flask.ext.assets import ManageAssets

from call_server.app import create_app
from call_server.config import DevelopmentConfig
from call_server.extensions import assets, db

app = create_app(config=DevelopmentConfig)
app.db = db
manager = Manager(app)

alembic_config = Config(os.path.realpath(os.path.dirname(__name__)) + "/alembic.ini")

manager.add_command("assets", ManageAssets())


def reset_assets(func):
    """Reset assets named bundles to {} before running command.
    This command should really be run with TestingConfig context"""
    print "resetting assets"
    assets._named_bundles = {}


@manager.command
def run():
    """Run webserver for local development."""
    app.run(debug=True, use_reloader=True)


@manager.command
def alembic():
    """Run in local machine."""
    subprocess.call([".venv/bin/alembic", "init", "alembic"])


@manager.command
def migrate(direction):
    """Migrate db revision"""
    reset_assets()
    print "migrating %s database at %s" % (direction, app.db.engine.url)
    if direction == "up":
        command.upgrade(alembic_config, "head")
    elif direction == "down":
        command.downgrade(alembic_config, "-1")
    else:
        app.logger.error('invalid direction. (up/down)')
        sys.exit(-1)


@manager.command
def migration(message):
    """Create migration file"""
    reset_assets()
    command.revision(alembic_config, autogenerate=True, message=message)


@manager.command
def stamp(revision):
    """Fake a migration to a particular revision"""
    reset_assets()
    alembic_cfg = Config("alembic.ini")
    command.stamp(alembic_cfg, revision)

if __name__ == "__main__":
    manager.run()
