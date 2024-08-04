import yaml
from flask_login import current_user, login_required

from flask import Blueprint, redirect, render_template, request, url_for

structures_blueprint = Blueprint("structures", __name__)


@structures_blueprint.route("/list")
@login_required
def list():
    yaml_data = yaml.dump(current_user.structures, default_flow_style=False)
    print("Structures\n", yaml_data)
    return render_template(
        "structures_list.html", structures=current_user.structures
    )


@structures_blueprint.route("/current")
@login_required
def current():
    return render_template(
        "structures_current.html", structure=current_user.current_structure
    )


@structures_blueprint.route("/edit")
@login_required
def edit():
    return render_template(
        "structures_edit.html", structure=current_user.current_structure
    )


@structures_blueprint.route("/save", methods=["POST"])
@login_required
def save():
    structure = current_user.current_structure
    structure.address = request.form["address"]
    structure.latitude = request.form["latitude"]
    structure.longitude = request.form["longitude"]
    structure.save()
    return redirect(url_for("structures.current"))
