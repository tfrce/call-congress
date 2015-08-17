from functools import wraps

from flask import abort
from flask.ext.login import current_user

from constants import USER_ADMIN


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role_code != USER_ADMIN:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
