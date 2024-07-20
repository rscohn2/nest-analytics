from urllib.parse import urlparse

import common.data_model
from common.data_model import load_user_by_username
from flask_login import login_user, logout_user
from portal.extensions import login_manager

from flask import Blueprint, flash, redirect, render_template, request, url_for

auth_blueprint = Blueprint("auth", __name__)


# Initializes flask_login.current_user
@login_manager.user_loader
def load_user(user_id):
    return common.data_model.load_user(user_id)


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
