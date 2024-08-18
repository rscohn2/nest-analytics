from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask_login import current_user, login_required
from plotly.subplots import make_subplots
from portal.nest import retrieve_nest
from portal.weather import retrieve_weather

from flask import Blueprint, request

dashboard_blueprint = Blueprint("dashboard", __name__)


zones = {
    "Outside": "blue",
    "Second Floor": "red",
    "Master Bedroom": "green",
    "First Floor": "purple",
}


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


def plot_combined(df):
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05
    )

    # Temperature Plot
    temperature_df_clean = df.dropna(subset=["Temperature"]).copy()
    temperature_df_clean["TempChange"] = (
        temperature_df_clean.groupby("Zone")["Temperature"].diff().abs()
    )
    temperature_df_filtered = temperature_df_clean.loc[
        temperature_df_clean["TempChange"] >= 0.25
    ].copy()
    for zone in temperature_df_filtered["Zone"].unique():
        zone_data = temperature_df_filtered[
            temperature_df_filtered["Zone"] == zone
        ]
        fig.add_trace(
            go.Scatter(
                x=zone_data["Time"],
                y=zone_data["Temperature"],
                mode="lines+markers",
                name=f"Temperature - {zone}",
                line=dict(color=zones[zone]),
            ),
            row=2,
            col=1,
        )

    # Humidity Plot
    humidity_df_clean = df.dropna(subset=["Humidity"]).copy()
    humidity_df_clean["HumidityChange"] = (
        humidity_df_clean.groupby("Zone")["Humidity"].diff().abs()
    )
    humidity_df_filtered = humidity_df_clean.loc[
        humidity_df_clean["HumidityChange"] >= 1
    ].copy()
    for zone in humidity_df_filtered["Zone"].unique():
        zone_data = humidity_df_filtered[humidity_df_filtered["Zone"] == zone]
        fig.add_trace(
            go.Scatter(
                x=zone_data["Time"],
                y=zone_data["Humidity"],
                mode="lines+markers",
                name=f"Humidity - {zone}",
                line=dict(color=zones[zone]),
            ),
            row=3,
            col=1,
        )

    # Cooling Time Plot
    cooling_df = df.copy()
    cooling_df.set_index("Time", inplace=True)
    daily_cooling = (
        cooling_df.groupby(["Zone", pd.Grouper(freq="D")])["Cooling Time"]
        .sum()
        .reset_index()
    )

    for zone in daily_cooling["Zone"].unique():
        print(f"Adding {zone}")
        zone_data = daily_cooling[daily_cooling["Zone"] == zone]
        fig.add_trace(
            go.Bar(
                x=zone_data["Time"],
                y=zone_data["Cooling Time"],
                name=f"Cooling Time - {zone}",
                marker_color=zones[zone],
                text=zone_data["Cooling Time"],
                textposition="auto",
                texttemplate="%{text:.1f}",  # Format text to one decimal place
            ),
            row=1,
            col=1,
        )

    # Add annotations and lines for each zone
    num_zones = len(zones)
    x_positions = [i / num_zones for i in range(num_zones)]
    anno_y = 1.05
    for i, (zone, color) in enumerate(zones.items()):
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=x_positions[i],
            y=anno_y,
            text=zone,
            showarrow=False,
            font=dict(color=color, size=14),
            xanchor="left",
        )
        fig.add_shape(
            type="line",
            xref="paper",
            yref="paper",
            x0=x_positions[i],
            y0=anno_y,
            x1=x_positions[i] + 0.04,
            y1=anno_y,
            line=dict(color=color, width=3),
        )

    # Update layout
    fig.update_layout(
        autosize=True, height=1000, showlegend=False, barmode="stack"
    )
    fig.update_xaxes(title_text="Time", row=3, col=1)
    fig.update_yaxes(
        title_text="Cooling Time (hours)", tickformat=".1f", row=1, col=1
    )
    fig.update_yaxes(title_text="Temperature (°F)", row=2, col=1)
    fig.update_yaxes(title_text="Humidity (%)", row=3, col=1)

    return fig.to_html(full_html=False, include_plotlyjs=False)


@dashboard_blueprint.route("/charts", methods=["GET"])
@login_required
def charts():
    # Get 'days' from query string, default to 7 if not specified
    days = int(request.args.get("days", 7))
    start_date = datetime.now() - timedelta(days=days)
    end_date = datetime.now()

    df = pd.DataFrame(fetch_events(current_user, start_date, end_date))

    return plot_combined(df)
