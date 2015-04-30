# define flask extensions in separate file, to resolve import dependencies

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.cache import Cache
cache = Cache()

from flask.ext.login import LoginManager
login_manager = LoginManager()

from flask.ext.assets import Environment
assets = Environment()

from flask.ext.babel import Babel
babel = Babel()

from flask.ext.mail import Mail
mail = Mail()
