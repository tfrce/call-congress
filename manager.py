import os
import sys
import subprocess

from flask.ext.script import Manager
from alembic import command
from alembic.config import Config
from flask.ext.assets import ManageAssets

from call_server.app import create_app
from call_server.config import DefaultConfig
from call_server.extensions import assets, db

from call_server.user import User, ADMIN, ACTIVE

app = create_app(config=DefaultConfig)
app.db = db
manager = Manager(app)

alembic_config = Config(os.path.realpath(os.path.dirname(__name__)) + "/alembic.ini")
# let the environment override the default db location in production
if os.environ.get('SQLALCHEMY_DATABASE_URI'):
    alembic_config.set_section_option('alembic', 'sqlalchemy.url',
                                      os.environ.get('SQLALCHEMY_DATABASE_URI'))

manager.add_command("assets", ManageAssets())


def reset_assets():
    """Reset assets named bundles to {} before running command.
    This command should really be run with TestingConfig context"""
    print "resetting assets"
    assets._named_bundles = {}


@manager.command
def run(server=None):
    """Run webserver for local development."""
    if server:
        app.config['SERVER_NAME'] = server
        app.config['STORE_DOMAIN'] = server
    app.run(debug=True, use_reloader=True, host=(os.environ.get('APP_HOST') or '127.0.0.1'))


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
    command.stamp(alembic_config, revision)


@manager.command
def createadminuser():
    from getpass import getpass
    from call_server.user.constants import (USERNAME_LEN_MIN, USERNAME_LEN_MAX,
                                            PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)

    username = None
    password = None

    while username is None:
        username = raw_input('Username: ')
        if len(username) < USERNAME_LEN_MIN:
            print "username too short, must be at least", USERNAME_LEN_MIN, "characters"
            username = None
            continue
        if len(username) > USERNAME_LEN_MAX:
            print "username too long, must be less than", USERNAME_LEN_MIN, "characters"
            username = None
            continue
        if User.query.filter_by(name=username).count() > 0:
            print "username already exists"
            username = None
            continue

        email = raw_input('Email: ')
        # email validation necessary?

    while password is None:
        password = getpass('Password: ')
        password_confirm = getpass('Confirm: ')
        if password != password_confirm:
            print "passwords don't match"
            password = None
            continue
        if len(password) < PASSWORD_LEN_MIN:
            print "password too short, must be at least", PASSWORD_LEN_MIN, "characters"
            password = None
            continue
        if len(password) > PASSWORD_LEN_MAX:
            print "password too long, must be less than", PASSWORD_LEN_MAX, "characters"
            password = None
            continue

    admin = User(name=username,
                 email=email,
                 password=password,
                 role_code=ADMIN,
                 status_code=ACTIVE)
    db.session.add(admin)
    db.session.commit()

    print "created admin user", admin.name


if __name__ == "__main__":
    manager.run()
