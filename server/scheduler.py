import collector
from flask import Blueprint

scheduler_blueprint = Blueprint("scheduler", __name__)


@scheduler_blueprint.route("/hourly", methods=["POST"])
def handle_hourly_tasks():
    collector.hourly()
    return "Hourly tasks processed\n", 200


# Quick tests
if __name__ == "__main__":
    handle_hourly_tasks()
