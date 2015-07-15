import os
from app import create_app
from config import ProductionConfig, HerokuConfig


def production_app(*args, **kwargs):
    if os.environ.get('HEROKU'):
        application = create_app(HerokuConfig)
    else:
        application = create_app(ProductionConfig)

    return application
