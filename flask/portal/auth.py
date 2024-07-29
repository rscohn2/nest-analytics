from os import getenv
from urllib.parse import urlparse

import common.data_model
import portal.globals as globals
from authlib.integrations.flask_client import OAuth
from common.data_model import load_user_by_userinfo, load_user_by_username
from flask_login import current_user, login_required, login_user, logout_user
from portal.extensions import login_manager

from flask import Blueprint, flash, redirect, render_template, request, url_for

auth_blueprint = Blueprint("auth", __name__)


# Initializes flask_login.current_user
@login_manager.user_loader
def load_user(id):
    return common.data_model.load_user(id)


def is_safe_url(target, request):
    # Parse the target URL
    parsed_url = urlparse(target)

    # Check if the scheme is 'http' or 'https'
    if parsed_url.scheme not in ["http", "https"]:
        return False

    # Optional: Check if the target URL's domain matches the request's domain
    # This step might be skipped depending on your specific requirements
    if parsed_url.netloc != request.host:
        return False

    return True


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Authenticate the user
        username = request.form["username"]
        password = request.form["password"]

        user = load_user_by_username(username)
        if user and user.check_password(password):
            print("User authenticated")
            login_user(user)
            next_url = request.form.get("next_url")
            if not is_safe_url(next_url, request):
                return redirect(url_for("index"))
            return redirect(next_url or url_for("index"))
        else:
            flash("Invalid username or password")

    # if GET or credentials invalid, show the login form
    return render_template("login.html", next_url=request.args.get("next"))


@auth_blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


def update_nest_token(name, token, refresh_token=None, access_token=None):
    if refresh_token:
        print("Updating refresh token")
        current_user.update_profile("nest_token.refresh_token", refresh_token)
    elif access_token:
        print("Updating access token")
        current_user.update_profile("nest_token.access_token", access_token)
    else:
        return


nest_project_id = getenv("NEST_PROJECT_ID")
globals.oauth = OAuth(update_token=update_nest_token)
print(f"Setting oauth: {globals.oauth}")
globals.oauth.register(
    name="nest",
    client_id=getenv("NEST_OAUTH_CLIENT_ID"),
    client_secret=getenv("NEST_OAUTH_CLIENT_SECRET"),
    authorize_url=(
        "https://nestservices.google.com/partnerconnections/"
        f"{nest_project_id}/auth"
    ),
    access_token_url="https://www.googleapis.com/oauth2/v4/token",
    api_base_url=(
        "https://smartdevicemanagement.googleapis.com/v1/enterprises/"
        f"{nest_project_id}/"
    ),
    client_kwargs={
        "scope": "https://www.googleapis.com/auth/sdm.service",
        "prompt": "consent",
    },
)


@auth_blueprint.route("/nest_authorize")
@login_required
def nest_authorize():
    redirect_uri = url_for("auth.nest_callback", _external=True)
    print(f"Redirect {redirect_uri}")
    return globals.oauth.nest.authorize_redirect(
        redirect_uri, access_type="offline"
    )


@auth_blueprint.route("/nest_callback")
@login_required
def nest_callback():
    token = globals.oauth.nest.authorize_access_token()
    current_user.update_profile("nest_token", token)
    current_user.profile.nest_token = token
    print(f"Token {token}")

    # resp = oauth.nest.get("devices", token=token)
    # resp.raise_for_status()

    # Listing devices completes the registration process
    current_user.list_devices()
    return redirect(url_for("dashboard.devices"))


globals.oauth.register(
    name="google",
    client_id=getenv("GOOGLE_LOGIN_OAUTH_CLIENT_ID"),
    client_secret=getenv("GOOGLE_LOGIN_OAUTH_CLIENT_SECRET"),
    server_metadata_url=(
        "https://accounts.google.com/.well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid email profile",
    },
)


@auth_blueprint.route("/google_login")
def google_login():
    redirect_uri = url_for("auth.google_login_callback", _external=True)
    print(f"Redirect {redirect_uri}")
    return globals.oauth.google.authorize_redirect(redirect_uri)


@auth_blueprint.route("/google_login_callback")
def google_login_callback():
    token = globals.oauth.google.authorize_access_token()
    print(f"Token {token}")
    user = load_user_by_userinfo(token["userinfo"])
    if user.profile.email != getenv("HA_AUTHORIZED_USER"):
        return redirect("/")
    print(f"Authorized user: {getenv('HA_AUTHORIZED_USER')}")
    login_user(user)
    return redirect("/")
