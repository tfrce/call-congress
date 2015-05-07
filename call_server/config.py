import os
import twilio.rest


class DefaultConfig(object):
    DEBUG = True
    TESTING = False
    APP_NAME = "call_server"

    SQLALCHEMY_DATABASE_URI = 'sqlite:////%s/dev.db' % os.path.abspath(os.curdir)
    SQLALCHEMY_ECHO = False

    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    ACCEPT_LANGUAGES = {'en': 'English',
                        'es': 'Spansih'}

    CACHE_TYPE = 'simple'

    CSRF_ENABLED = False

    SITENAME = os.environ.get('SITENAME')

    TW_CLIENT = twilio.rest.TwilioRestClient(
        os.environ.get('TWILIO_DEV_ACCOUNT_SID'),
        os.environ.get('TWILIO_DEV_AUTH_TOKEN'))
    # limit on the length of the call
    TW_TIME_LIMIT = 60 * 20  # 4 minutes

    # limit on the amount of time to ring before giving up
    TW_TIMEOUT = 40  # seconds

    SECRET_KEY = 'NotARealSecretKey'

    SUNLIGHTLABS_KEY = os.environ.get('SUNLIGHTLABS_KEY')


class ProductionConfig(DefaultConfig):
    DEBUG = False

    APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT', None)

    CACHE_TYPE = 'memcached'

    TW_CLIENT = twilio.rest.TwilioRestClient(
        os.environ.get('TWILIO_ACCOUNT_SID'),
        os.environ.get('TWILIO_AUTH_TOKEN'))
    TW_NUMBER = os.environ.get('TWILIO_NUMBER')

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SENTRY_DSN = os.environ.get('SENTRY_DSN')

    SQLALCHEMY_POOL_RECYCLE = 60 * 60  # 1 hour
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')


class DevelopmentConfig(DefaultConfig):
    TESTING = False
    DEBUG = True
    DEBUG_INFO = False
    WTF_CSRF_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SERVER_NAME = 'localhost:5000'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'NotARealSecretKey,YouShouldSetOneInYour.Env')


class TestingConfig(DefaultConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # keep testing db in memory
    APPLICATION_ROOT = 'http://1cf55a5a.ngrok.com'
    TW_NUMBER = '5005550006'  # development number

    CACHE_TYPE = 'null'
    CACHE_NO_NULL_WARNING = True
