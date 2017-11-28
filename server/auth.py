from functools import wraps
from flask import redirect, url_for


class Auth(object):

    login = ""

    @staticmethod
    def authenticated():
        return True

    @staticmethod
    def require(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not Auth.authenticated():
                return redirect(url_for(Auth.login))
            return f(*args, **kwargs)
        return wrapped
