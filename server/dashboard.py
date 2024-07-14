from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from data_model import load_user
from flask import Blueprint, render_template
from ha_weather import retrieve_weather

dashboard_blueprint = Blueprint("dashboard", __name__)


def fetch_data(user, start_date, end_date):
    weather_events = retrieve_weather(user, start_date, end_date)
    return weather_events


@dashboard_blueprint.route("/main", methods=["GET", "POST"])
def dashboard():
    user = load_user(0)
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()

    df = pd.DataFrame(fetch_data(user, start_date, end_date))
    temperature_fig = px.line(
        df, x="Time", y="Temperature", color="Zone", markers=True
    )
    temperature_html = temperature_fig.to_html(
        full_html=False, include_plotlyjs="cdn"
    )
    return render_template("dashboard.html", temperature_fig=temperature_html)
