from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from data_model import load_user
from flask import Blueprint, render_template
from ha_nest import retrieve_nest
from ha_weather import retrieve_weather

dashboard_blueprint = Blueprint("dashboard", __name__)


def fetch_events(user, start_date, end_date):
    events = retrieve_weather(user, start_date, end_date)
    events.extend(retrieve_nest(user, start_date, end_date))
    return events


@dashboard_blueprint.route("/main", methods=["GET", "POST"])
def dashboard():
    user = load_user(0)
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()

    df = pd.DataFrame(fetch_events(user, start_date, end_date))
    temperature_fig = px.line(
        df, x="Time", y="Temperature", color="Zone", markers=True
    )
    temperature_html = temperature_fig.to_html(
        full_html=False, include_plotlyjs="cdn"
    )
    return render_template("dashboard.html", temperature_fig=temperature_html)
