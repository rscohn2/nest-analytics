from common.secrets import get_key
from flask_login import LoginManager
from portal.dashboard import dashboard_blueprint
from portal.user import user_blueprint

from flask import Flask

app = Flask(__name__)
app.secret_key = get_key("portal")
app.register_blueprint(dashboard_blueprint, url_prefix="/dashboard")
app.register_blueprint(user_blueprint, url_prefix="/user")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user.login"


@login_manager.user_loader
def load_user(user_id):
    # Return the User object given the user_id
    # Typically, you would query your database for the user here
    #  return User.get(user_id)
    pass


@app.route("/")
def hello_world():
    return "Portal is running!"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
