# This needs to be before other imports
import portal.env_setup  # noqa: F401
import portal.globals as globals
from common.secrets import get_key
from flask_login import current_user
from portal.auth import auth_blueprint
from portal.dashboard import dashboard_blueprint
from portal.electric import electric_blueprint
from portal.extensions import login_manager

from flask import Flask

# initialize flask app and packages that depend on it
app = Flask(__name__)
app.secret_key = get_key("portal")

# init blueprints
app.register_blueprint(dashboard_blueprint, url_prefix="/dashboard")
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(electric_blueprint, url_prefix="/electric")

# init login manager
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# init oauth
globals.oauth.init_app(app)


@app.route("/")
def index():
    if current_user.is_authenticated:
        return f"Welcome {current_user.profile.email}!"
    else:
        return "Portal is running!"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
