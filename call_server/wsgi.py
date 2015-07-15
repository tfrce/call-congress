from app import create_app


def production(*args, **kwargs):
    application = create_app()
    return application.run()
