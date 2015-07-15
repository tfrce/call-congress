import os
from app import create_app
from config import ProductionConfig, HerokuConfig


def production_app(*args, **kwargs):
    application = create_app(ProductionConfig)
    return application


def heroku_app(*args, **kwargs):
    application = create_app(HerokuConfig)
    return application
