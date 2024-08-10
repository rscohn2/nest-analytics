import yaml
from flask_login import current_user, login_required

from flask import Blueprint, render_template

debug_blueprint = Blueprint("debug", __name__)


@debug_blueprint.route("/nest-devices", methods=["GET"])
@login_required
def nest_devices():
    return render_template(
        "yaml.html",
        title="Devices",
        yaml_data=yaml.dump(
            current_user.list_resource("devices"), default_flow_style=False
        ),
    )


@debug_blueprint.route("/nest-structures", methods=["GET"])
@login_required
def nest_structures():
    return render_template(
        "yaml.html",
        title="Structures",
        yaml_data=yaml.dump(
            current_user.list_resource("structures"), default_flow_style=False
        ),
    )


@debug_blueprint.route("/nest-rooms", methods=["GET"])
@login_required
def nest_rooms():
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


@debug_blueprint.route("/structure", methods=["GET"])
@login_required
def structure():
    for key in current_user.current_structure.aux["rooms"]:
        print(f"type: {type(key)} val {key}")
    return render_template(
        "yaml.html",
        title="Structure",
        yaml_data=yaml.dump(
            current_user.current_structure.__dict__, default_flow_style=False
        ),
    )
