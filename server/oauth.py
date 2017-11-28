from flask import redirect, jsonify, request, session, url_for
from flask_oauthlib.client import OAuth
import requests

from .auth import Auth as auth


def add_oauth(app, options):
    oauth = OAuth()
    oauth_options = options.oauth_options()
    remote = oauth.remote_app(
        "Ad-stats",
        base_url="https://www.google.com/accounts/",
        consumer_key=oauth_options["google_client_id"],
        consumer_secret=oauth_options["google_secret_key"],
        request_token_params={"scope": "email"},
        request_token_url=None,
        access_token_method='POST',
        access_token_url="https://accounts.google.com/o/oauth2/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        content_type="application/json"
    )

    @app.route(oauth_options["callback_url"])
    @remote.authorized_handler
    def callback(resp):
        access_token = resp["access_token"]
        headers = {"Authorization": "OAuth %s" % access_token}
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers=headers).json()
        if oauth_options["hosted_domain"] is not None:
            if "hd" not in user_info \
                    or user_info["hd"] != oauth_options["hosted_domain"]:
                return redirect(url_for("login"))
        session["access_token"] = access_token, ""
        return redirect(url_for(app.default_url))

    @app.route("/login")
    def login():
        return remote.authorize(
            hd=oauth_options["hosted_domain"],
            callback=url_for("callback", _external=True),
            next=request.args.get('next') or request.referrer or None)

    @remote.tokengetter
    def get_token():
        session.get("access_token")

    def check_auth():
        if session.get("access_token", "") != "":
            return True
        return False

    auth.login = "login"
    auth.authenticated = check_auth
