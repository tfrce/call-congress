import os
import sys
import subprocess

from flask.ext.script import Manager
from alembic import command
from alembic.config import Config
from flask.ext.assets import ManageAssets

from call_server.app import create_app
from call_server.extensions import assets, db, cache
from call_server import political_data
from call_server.user import User, USER_ADMIN, USER_ACTIVE

app = create_app()
app.db = db
manager = Manager(app)

alembic_config = Config(os.path.realpath(os.path.dirname(__name__)) + "/alembic.ini")
# let the config override the default db location in production
alembic_config.set_section_option('alembic', 'sqlalchemy.url',
                                  app.config.get('SQLALCHEMY_DATABASE_URI'))

manager.add_command("assets", ManageAssets())


def reset_assets():
    """Reset assets named bundles to {} before running command.
    This command should really be run with TestingConfig context"""
    print "resetting assets"
    assets._named_bundles = {}


@manager.command
def runserver(external=None):
    """Run web server for local development and debugging
        pass --external for external routing"""
    if external:
        app.config['SERVER_NAME'] = external
        app.config['STORE_DOMAIN'] = "http://" + external # needs to have scheme, so urlparse is fully absolute
        print "serving from %s" % app.config['SERVER_NAME']
    political_data.load_data(cache)

    host = (os.environ.get('APP_HOST') or '127.0.0.1')
    app.run(debug=True, use_reloader=True, host=host)


@manager.command
def loadpoliticaldata():
    """Load political data into persistent cache"""
    try:
        import gevent.monkey
        gevent.monkey.patch_thread()
    except ImportError:
        print "unable to apply gevent monkey.patch_thread"

    print "loading political data"
    with app.app_context():
        cache.clear()
        n = political_data.load_data(cache)
    print "loaded %d objects" % n
    print "done"
    if app.config.get('ENVIRONMENT') is "Heroku":
        print "don't worry about the KeyError"
        # http://stackoverflow.com/questions/8774958/keyerror-in-module-threading-after-a-successful-py-test-run/12639040#12639040

@manager.command
def alembic():
    """Run alembic migration command"""
    subprocess.call([".venv/bin/alembic", "init", "alembic"])


@manager.command
def migrate(direction):
    """Migrate db revision up or down"""
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
def createadminuser(username=None, password=None, email=None):
    """Create a new admin user, get password from user input or directly via command line"""

    # first, check to see if exact user already exists
    if username and email and password:
        if User.query.filter_by(name=username).count() == 1:
            print "username %s already exists" % username
            return True

    # else, getpass from raw input
    from getpass import getpass
    from call_server.user.constants import (USERNAME_LEN_MIN, USERNAME_LEN_MAX,
                                            PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)

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

    while email is None:
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
                 role_code=USER_ADMIN,
                 status_code=USER_ACTIVE)
    db.session.add(admin)
    db.session.commit()

    print "created admin user", admin.name


if __name__ == "__main__":
    manager.run()
