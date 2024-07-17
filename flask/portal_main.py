from portal.dashboard import dashboard_blueprint

from flask import Flask

app = Flask(__name__)
app.register_blueprint(dashboard_blueprint, url_prefix="/dashboard")


@app.route("/")
def hello_world():
    return "Portal is running!"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
