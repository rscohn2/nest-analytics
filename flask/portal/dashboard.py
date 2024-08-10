from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from flask_login import current_user, login_required
from portal.nest import retrieve_nest
from portal.weather import retrieve_weather

from flask import Blueprint, render_template, request

dashboard_blueprint = Blueprint("dashboard", __name__)


def fetch_events(user, start_date, end_date):
    structure_id = user.current_structure.id
    events = retrieve_weather(structure_id, start_date, end_date)
    events.extend(retrieve_nest(structure_id, start_date, end_date))
    return events


def plot_cooling_time(df):
    cooling_df = df.copy()
    cooling_df.set_index("Time", inplace=True)
    # Group by day and sum 'Cooling Time'
    daily_cooling = (
        cooling_df.groupby(["Zone", pd.Grouper(freq="D")])["Cooling Time"]
        .sum()
        .reset_index()
    )
    # Plot
    cooling_fig = px.bar(
        daily_cooling, x="Time", y="Cooling Time", color="Zone", text_auto=True
    )
    cooling_fig.update_layout(barmode="stack")
    cooling_fig.update_xaxes(title_text="Day", dtick="D1")
    cooling_fig.update_yaxes(
        title_text="Cooling Time (hours)", tickformat=".2f"
    )
    return cooling_fig.to_html(full_html=False, include_plotlyjs=False)


def plot_temperature(df):
    # eliminate measurements with missing temperature
    df_clean = df.dropna(subset=["Temperature"]).copy()

    # Calculate the difference in temperature within the same zone
    df_clean["TempChange"] = (
        df_clean.groupby("Zone")["Temperature"].diff().abs()
    )

    # Filter out changes less than 0.25
    df_filtered = df_clean.loc[df_clean["TempChange"] >= 0.25].copy()

    # Continue with plotting or other operations on df_filtered

    temperature_fig = px.line(
        df_filtered, x="Time", y="Temperature", color="Zone", markers=True
    )
    temperature_html = temperature_fig.to_html(
        full_html=False, include_plotlyjs=False
    )
    return temperature_html


def plot_humidity(df):
    # eliminate measurements with missing humidity
    df_clean = df.dropna(subset=["Humidity"]).copy()

    # Filter out changes less than 0.25.
    # Calculate the difference in temperature within the same zone
    df_clean["HumidityChange"] = (
        df_clean.groupby("Zone")["Humidity"].diff().abs()
    )
    df_filtered = df_clean.loc[df_clean["HumidityChange"] >= 1].copy()

    fig = px.line(
        df_filtered, x="Time", y="Humidity", color="Zone", markers=True
    )
    html = fig.to_html(full_html=False, include_plotlyjs=False)
    return html


@dashboard_blueprint.route("/charts", methods=["GET"])
@login_required
def charts():
    # Get 'days' from query string, default to 7 if not specified
    days = int(request.args.get("days", 7))
    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now()

    df = pd.DataFrame(fetch_events(current_user, start_date, end_date))

    return render_template(
        "charts.html",
        temperature_fig=plot_temperature(df),
        humidity_fig=plot_humidity(df),
        # cooling_time_fig=plot_cooling_time(df),
    )
