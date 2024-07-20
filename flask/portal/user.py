from flask_login import login_user, logout_user

from flask import Blueprint, redirect, request, url_for

user_blueprint = Blueprint("user", __name__)


@user_blueprint.route("/login", methods=["GET", "POST"])
def login():
    # Authenticate the user
    # user = User.query.filter_by(username=request.form["username"]).first()
    # if user is not None and user.check_password(request.form["password"]):
    #    #login_user(user)
    #   return redirect(url_for("protected"))
    return "Invalid username or password"


@user_blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
