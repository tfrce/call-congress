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
    CACHE_DEFAULT_TIMEOUT = 60*60*24*365*2  # there's no infinite timeout, so default to 2 year election cycle

    CSRF_ENABLED = False

    INSTALLED_ORG = os.environ.get('INSTALLED_ORG')
    SITENAME = os.environ.get('SITENAME', PROJECT)

    STORE_PROVIDER = 'flask_store.providers.local.LocalProvider'
    STORE_DOMAIN = 'http://localhost:5000' # requires url scheme for Flask-store.absolute_url to work

    TWILIO_CLIENT = twilio.rest.TwilioRestClient(
        os.environ.get('TWILIO_ACCOUNT_SID'),
        os.environ.get('TWILIO_AUTH_TOKEN'))
    TWILIO_PLAYBACK_APP = os.environ.get('TWILIO_PLAYBACK_APP')
    # limit on the length of the call
    TWILIO_TIME_LIMIT = os.environ.get('TWILIO_TIME_LIMIT', 60 * 60)  # one hour max
    # limit on the amount of time to ring before giving up
    TWILIO_TIMEOUT = os.environ.get('TWILIO_TIMEOUT', 60)  # seconds

    SECRET_KEY = os.environ.get('SECRET_KEY')

    GEOCODE_API_KEY = os.environ.get('GEOCODE_API_KEY')
    OPENSTATES_API_KEY = os.environ.get('OPENSTATES_API_KEY')

    LOG_PHONE_NUMBERS = True

    MAIL_SERVER = 'localhost'


class ProductionConfig(DefaultConfig):
    DEBUG = False

    ENVIRONMENT = "Production"

    SERVER_NAME = os.environ.get('SERVER_NAME')
    APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT', None)
    ADMIN_API_KEY = os.environ.get('ADMIN_API_KEY', None)

    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_KEY_PREFIX = 'call-power'

    LOG_PHONE_NUMBERS = os.environ.get('LOG_PHONE_NUMBERS', False)
    OUTPUT_LOG = os.environ.get('OUTPUT_LOG', False)

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = os.environ.get('MAIL_PORT', 25)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)

    SQLALCHEMY_POOL_SIZE = int(os.environ.get('SQLALCHEMY_POOL_SIZE', 5))
    SQLALCHEMY_POOL_RECYCLE = os.environ.get('SQLALCHEMY_POOL_RECYCLE', 60)  # default 1 hour
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

    STORE_PROVIDER = 'flask_store.providers.s3.S3Provider'
    # TODO, change to S3GeventProvider when we re-enable gevent
    STORE_PATH = 'uploads'
    STORE_S3_BUCKET = os.environ.get('STORE_S3_BUCKET')
    STORE_S3_REGION = os.environ.get('STORE_S3_REGION')
    STORE_S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    STORE_S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    STORE_DOMAIN = os.environ.get('STORE_DOMAIN')
    if not STORE_DOMAIN and STORE_S3_REGION:
        # set external store domain per AWS regions
        # http://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region
        # use path-style urls, in case bucket name is DNS incompatible (uses periods, or mixed case
        # http://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html
        if STORE_S3_REGION is 'us-east-1':
            STORE_DOMAIN = 'https://s3.amazonaws.com/%s/' % (STORE_S3_BUCKET)
        else:
            STORE_DOMAIN = 'https://s3-%s.amazonaws.com/%s/' % (STORE_S3_REGION, STORE_S3_BUCKET)


class HerokuConfig(ProductionConfig):
    # Heroku addons use a few different environment variable names

    ENVIRONMENT = "Heroku"

    # db via heroku postgres
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # cache via heroku-redis
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_KEY_PREFIX = 'call-power'

    # smtp via sendgrid
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USERNAME = os.environ.get('SENDGRID_USERNAME')
    MAIL_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'info@callpower.org')


class DevelopmentConfig(DefaultConfig):
    DEBUG = True
    DEBUG_INFO = False
    TESTING = False

    ENVIRONMENT = "Development"

    ADMIN_API_KEY = os.environ.get('ADMIN_API_KEY', 'ThisIsATestAdminAPIKey!')

    WTF_CSRF_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'NotARealSecretKey,YouShouldSetOneInYour.Env')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI',
        'sqlite:////%s/dev.db' % os.path.abspath(os.curdir))

    SERVER_NAME = 'localhost:5000'
    STORE_PATH = '%s/instance/uploads/' % os.path.abspath(os.curdir)
    STORE_DOMAIN = 'http://localhost:5000'

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
