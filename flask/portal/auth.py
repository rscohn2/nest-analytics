import common.data_model
from flask_login import login_user, logout_user
from portal.extensions import login_manager

from flask import Blueprint, redirect, request, url_for

auth_blueprint = Blueprint("auth", __name__)


# Initializes flask_login.current_user
@login_manager.user_loader
def load_user(user_id):
    return common.data_model.load_user(user_id)


def is_safe_url(target):
    return True


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    # Authenticate the user
    # get login name, password from form, map login name to user_id
    user_id = common.data_model.load_user("0")
    # todo: check password for user_id
    if True:
        print("User authenticated")
        login_user(user_id)
        next_url = request.args.get("next")
        if not is_safe_url(next_url):
            return redirect(url_for("index"))
        return redirect(next_url or url_for("index"))
    return "Invalid username or password"


@auth_blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
