from collector import collector_blueprint
from flask import Flask
from scheduler import scheduler_blueprint

app = Flask(__name__)

app.register_blueprint(collector_blueprint, url_prefix="/collector")
app.register_blueprint(scheduler_blueprint, url_prefix="/scheduler")


@app.route("/")
def hello_world():
    return "Hello, World!!"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
