from collector.scheduler import scheduler_blueprint
from common.secrets import get_key

from flask import Flask

app = Flask(__name__)
app.secret_key = get_key("collector")
app.register_blueprint(scheduler_blueprint, url_prefix="/scheduler")


@app.route("/")
def hello_world():
    return "Collector is running!"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
