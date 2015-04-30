import os
import twilio.rest


class DefaultConfig(object):
    DEBUG = True
    TESTING = False
    APP_NAME = "call_server"

    APPLICATION_ROOT = os.path.abspath(os.curdir)
    SQLALCHEMY_DATABASE_URI = 'sqlite:////%s/dev.db' % APPLICATION_ROOT
    SQLALCHEMY_ECHO = False

    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    ACCEPT_LANGUAGES = {'en': 'English',
                        'es': 'Spansih'}

    TW_CLIENT = twilio.rest.TwilioRestClient(
        os.environ.get('TWILIO_DEV_ACCOUNT_SID'),
        os.environ.get('TWILIO_DEV_AUTH_TOKEN'))
    # limit on the length of the call
    TW_TIME_LIMIT = 60 * 20  # 4 minutes

    # limit on the amount of time to ring before giving up
    TW_TIMEOUT = 40  # seconds

    SUNLIGHTLABS_KEY = os.environ.get('SUNLIGHTLABS_KEY')

    SECRET_KEY = 'AOUSBDAONPSOMDASIDUBSDOUABER)*#(R&(&@@#))'

    CACHE_TYPE = 'simple'


class ProductionConfig(DefaultConfig):
    DEBUG = False

    SENTRY_DSN = os.environ.get('SENTRY_DSN')

    SQLALCHEMY_POOL_RECYCLE = 60 * 60  # 1 hour
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

    APPLICATION_ROOT = os.environ.get('APPLICATION_ROOT')

    TW_CLIENT = twilio.rest.TwilioRestClient(
        os.environ.get('TWILIO_ACCOUNT_SID'),
        os.environ.get('TWILIO_AUTH_TOKEN'))
    TW_NUMBER = os.environ.get('TWILIO_NUMBER')

    SECRET_KEY = os.environ.get('SECRET_KEY')

    CACHE_TYPE = 'memcached'


class DevelopmentConfig(DefaultConfig):
    TESTING = False
    DEBUG = True
    DEBUG_INFO = os.environ.get('DEBUG_INFO')


class TestingConfig(DefaultConfig):
    TESTING = True
    APPLICATION_ROOT = ''
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # keep testing db in memory
    APPLICATION_ROOT = 'http://1cf55a5a.ngrok.com'
    TW_NUMBER = '5005550006'  # development number

    CACHE_TYPE = 'null'
    CACHE_NO_NULL_WARNING = True
