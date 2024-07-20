from common.secrets import get_key
from portal.auth import auth_blueprint
from portal.dashboard import dashboard_blueprint
from portal.extensions import login_manager

from flask import Flask

app = Flask(__name__)
app.secret_key = get_key("portal")
app.register_blueprint(dashboard_blueprint, url_prefix="/dashboard")
app.register_blueprint(auth_blueprint, url_prefix="/auth")
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@app.route("/")
def index():
    return "Portal is running!"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
