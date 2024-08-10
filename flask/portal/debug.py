import yaml
from flask_login import current_user, login_required

from flask import Blueprint, render_template

debug_blueprint = Blueprint("debug", __name__)


@debug_blueprint.route("/devices", methods=["GET"])
@login_required
def devices():
    return render_template(
        "yaml.html",
        title="Devices",
        yaml_data=yaml.dump(
            current_user.list_resource("devices"), default_flow_style=False
        ),
    )


@debug_blueprint.route("/structures", methods=["GET"])
@login_required
def structures():
    return render_template(
        "yaml.html",
        title="Structures",
        yaml_data=yaml.dump(
            current_user.list_resource("structures"), default_flow_style=False
        ),
    )


@debug_blueprint.route("/rooms", methods=["GET"])
@login_required
def rooms():
    return render_template(
        "yaml.html",
        title="Rooms",
        yaml_data=yaml.dump(
            current_user.list_resource(
                f"structures/{current_user.current_structure.id}/rooms"
            ),
            default_flow_style=False,
        ),
    )
