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
    cooling_fig.update_yaxes(title_text="Cooling Time (minutes)")
    return cooling_fig.to_html(full_html=False, include_plotlyjs="cdn")


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
        full_html=False, include_plotlyjs="cdn"
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


@dashboard_blueprint.route("/main", methods=["GET", "POST"])
def dashboard():
    user = load_user(0)
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()

    df = pd.DataFrame(fetch_events(user, start_date, end_date))

    return render_template(
        "dashboard.html",
        temperature_fig=plot_temperature(df),
        humidity_fig=plot_humidity(df),
        cooling_time_fig=plot_cooling_time(df),
    )
