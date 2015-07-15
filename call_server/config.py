import os
import twilio.rest


class DefaultConfig(object):
    PROJECT = 'CallPower'
    DEBUG = False
    TESTING = False
    ENVIRONMENT = "Default"

    APP_NAME = "call_server"
    APPLICATION_ROOT = None  # the path where the application is configured

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI',
        'sqlite:////%s/dev.db' % os.path.abspath(os.curdir))
    SQLALCHEMY_ECHO = False

    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    ACCEPT_LANGUAGES = {'en': 'English',
                        'es': 'Spanish'}

    CACHE_TYPE = 'simple'
    CACHE_THRESHOLD = 100000  # because we're caching political data
    CACHE_DEFAULT_TIMEOUT = 60*60*24*365  # there's no infinite timeout, so default to a year

    CSRF_ENABLED = False

    INSTALLED_ORG = os.environ.get('INSTALLED_ORG')
    SITENAME = os.environ.get('SITENAME')

    STORE_PROVIDER = 'flask_store.providers.local.LocalProvider'

    TWILIO_CLIENT = twilio.rest.TwilioRestClient(
        os.environ.get('TWILIO_ACCOUNT_SID'),
        os.environ.get('TWILIO_AUTH_TOKEN'))
    # limit on the length of the call
    TWILIO_TIME_LIMIT = 60 * 20  # 4 minutes

    # limit on the amount of time to ring before giving up
    TWILIO_TIMEOUT = 40  # seconds

    SECRET_KEY = os.environ.get('SECRET_KEY')

    SUNLIGHT_API_KEY = os.environ.get('SUNLIGHT_API_KEY')

    LOG_PHONE_NUMBERS = True

    MAIL_SERVER = 'localhost'


class ProductionConfig(DefaultConfig):
    DEBUG = False

    ENVIRONMENT = "Production"

    SERVER_NAME = os.environ.get('SERVER_NAME')
    APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT', None)

    CACHE_TYPE = 'memcached'
    CACHE_MEMCACHED_SERVERS = os.environ.get('CACHE_MEMCACHED_SERVERS')
    CACHE_MEMCACHED_USERNAME = os.environ.get('CACHE_MEMCACHED_USERNAME')
    CACHE_MEMCACHED_PASSWORD = os.environ.get('CACHE_MEMCACHED_PASSWORD')
    CACHE_KEY_PREFIX = 'call-power'

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = os.environ.get('MAIL_PORT', 1025)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'info@callpower.org')

    SQLALCHEMY_POOL_RECYCLE = 60 * 60  # 1 hour
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

    STORE_PROVIDER = 'flask_store.providers.s3.S3Provider'
    # TODO, change to S3GeventProvider when we re-enable gevent
    STORE_PATH = 'uploads'
    STORE_S3_BUCKET = os.environ.get('STORE_S3_BUCKET')
    STORE_S3_REGION = os.environ.get('STORE_S3_REGION')
    STORE_S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    STORE_S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    STORE_DOMAIN = 'https://%s.s3-%s.amazonaws.com/' % (STORE_S3_BUCKET, STORE_S3_REGION)


class HerokuConfig(ProductionConfig):
    # Heroku addons use a few different environment variable names

    ENVIRONMENT = "Heroku"

    # db via heroku postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # memcache via memcachier
    CACHE_TYPE = 'memcached'
    CACHE_MEMCACHED_SERVERS = [os.environ.get('MEMCACHIER_SERVERS'),]
    #  flask-cache requires this to be a list
    CACHE_MEMCACHED_USERNAME = os.environ.get('MEMCACHIER_USERNAME')
    CACHE_MEMCACHED_PASSWORD = os.environ.get('MEMCACHIER_PASSWORD')

    # smtp via sendgrid
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587


class DevelopmentConfig(DefaultConfig):
    DEBUG = True
    DEBUG_INFO = False
    TESTING = False

    ENVIRONMENT = "Development"

    WTF_CSRF_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'NotARealSecretKey,YouShouldSetOneInYour.Env')

    SQLALCHEMY_DATABASE_URI = 'sqlite:////%s/dev.db' % os.path.abspath(os.curdir)

    SERVER_NAME = 'localhost:5000'
    STORE_PATH = '%s/instance/uploads/' % os.path.abspath(os.curdir)
    STORE_DOMAIN = SERVER_NAME

    MAIL_DEBUG = True
    MAIL_PORT = 1025
    MAIL_DEFAULT_SENDER = 'debug'


class TestingConfig(DefaultConfig):
    ENVIRONMENT = "Testing"

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # keep testing db in memory
    CACHE_TYPE = 'null'
    CACHE_NO_NULL_WARNING = True
