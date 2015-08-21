from functools import wraps

from flask import current_app, abort, request
from flask.ext.login import current_user


def restless_api_auth(*args, **kwargs):
    """Restrict access to logged in user or valid admin api key
    Flask-Restless preprocessor"""
    if current_user.is_authenticated():
        return  # allow

    # check for system api key
    admin_key = current_app.config.get('ADMIN_API_KEY')
    if admin_key and request.args.get('api_key') == admin_key:
        return  # allow

    abort(401, 'Not Authenticated')


def api_key_or_auth_required(f):
    """Restrict access to logged in user or valid admin api key
    Flask view decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated():
            return f(*args, **kwargs)  # allow

        admin_key = current_app.config.get('ADMIN_API_KEY')
        if admin_key and request.args.get('api_key') == admin_key:
                return f(*args, **kwargs)

        abort(401, 'Not Authenticated')
    return decorated_function
