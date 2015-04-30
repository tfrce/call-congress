import os
import subprocess
from functools import wraps

from flask.ext.script import Manager
from alembic import command
from alembic.config import Config
from flask.ext.assets import ManageAssets

from call_server.app import create_app
from call_server.extensions import assets

app = create_app()
manager = Manager(app)

alembic_config = Config(os.path.realpath(os.path.dirname(__name__)) + "/alembic.ini")

manager.add_command("assets", ManageAssets())


def reset_assets(func):
    @wraps(func)
    def func_wrapper(name):
        assets._named_bundles = {}
    return func_wrapper


@manager.command
def run():
    """Run webserver for local development."""
    app.run(debug=True, use_reloader=True)


@manager.command
def alembic():
    """Run in local machine."""
    subprocess.call([".venv/bin/alembic", "init", "alembic"])


@manager.command
@reset_assets
def migrate(direction):
    """Migrate db revision"""
    if direction == "up":
        command.upgrade(alembic_config, "head")
    elif direction == "down":
        command.downgrade(alembic_config, "-1")


@manager.command
@reset_assets
def migration(message):
    """Create migration file"""
    command.revision(alembic_config, autogenerate=True, message=message)


@manager.command
@reset_assets
def stamp(revision):
    """Fake a migration to a particular revision"""
    alembic_cfg = Config("alembic.ini")
    command.stamp(alembic_cfg, revision)

if __name__ == "__main__":
    manager.run()
