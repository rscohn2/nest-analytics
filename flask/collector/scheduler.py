import collector.collector as collector

from flask import Blueprint, abort, request

scheduler_blueprint = Blueprint("scheduler", __name__)


@scheduler_blueprint.route("/hourly", methods=["GET"])
def handle_hourly_tasks():
    # Check for App Engine Cron header
    print("handle_hourly_tasks")
    if "X-Appengine-Cron" not in request.headers:
        print("aborting")
        abort(403)  # Ensures only cron jobs can call this endpoint

    collector.hourly()
    return "Hourly tasks processed\n", 200


# Quick tests
if __name__ == "__main__":
    handle_hourly_tasks()
