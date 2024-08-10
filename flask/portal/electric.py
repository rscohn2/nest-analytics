from datetime import datetime

import pytz
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from google.cloud import firestore
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired

from flask import Blueprint, redirect, render_template, url_for

electric_blueprint = Blueprint("electric", __name__)

db = firestore.Client()


# Form class
class MeterDataForm(FlaskForm):
    eastern = pytz.timezone("America/New_York")
    datetime = StringField(
        "Date/Time",
        validators=[DataRequired()],
        default=datetime.now(eastern).strftime("%Y-%m-%d %H:%M"),
    )
    value = IntegerField("Value", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Route to display and process the form
@electric_blueprint.route("/add", methods=["GET", "POST"])
@login_required
def add():
    meter_data = db.collection("meter_data")
    form = MeterDataForm()
    if form.validate_on_submit():
        # Convert datetime to UNIX timestamp
        dt_str = form.datetime.data
        dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        entry = {
            "dt": datetime.timestamp(dt_obj),
            "value": form.value.data,
            "user_id": current_user.id,
            "structure_id": current_user.current_structure.id,
        }
        meter_data.add(entry)
        return redirect(url_for("electric.add"))
    last_items_ref = (
        meter_data.where(
            "structure_id", "==", current_user.current_structure.id
        )
        .order_by("dt", direction=firestore.Query.DESCENDING)
        .limit(5)
        .get()
    )
    values = [
        {
            "dt": datetime.fromtimestamp(entry.to_dict()["dt"]).strftime(
                "%Y-%m-%d %H:%M"
            ),
            "value": entry.to_dict()["value"],
        }
        for entry in last_items_ref
    ]

    last_value = values[0]["value"] if values else 0
    form.value.data = last_value

    return render_template("add_electric.html", form=form, values=values)
