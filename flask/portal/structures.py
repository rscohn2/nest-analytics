import yaml
from flask_login import current_user, login_required

from flask import Blueprint, render_template

structures_blueprint = Blueprint("structures", __name__)


@structures_blueprint.route("/list")
@login_required
def structures():
    yaml_data = yaml.dump(current_user.structures, default_flow_style=False)
    print("Structures\n", yaml_data)
    return render_template(
        "structures_list.html", structures=current_user.structures
    )
