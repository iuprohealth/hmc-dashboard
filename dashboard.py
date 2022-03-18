# Copyright 2022 Alexander L. Hayes
# MIT License

import argparse
import json

from flask import Flask, render_template, request
import plotly
import plotly.graph_objects as go
from plotly import subplots
import pandas as pd
import numpy as np

app = Flask(__name__)

METADATA = pd.read_csv("user_metadata.csv")

DEFAULT_USER = "demo-user-1"
DEFAULT_VIEW = "sleep"


def get_users():
    """Get pairs of full user id's and user slugs."""

    # TODO(hayesall): @cache?

    return METADATA[["user_full", "user"]].to_numpy().tolist()


@app.route("/")
def index():
    data = load_user_from_csv(DEFAULT_USER, DEFAULT_VIEW)
    return render_template(
        "pages/user_overview.html",
        page_title="User Overview",
        users=get_users(),
        plot=data,
    )

@app.route("/compare-users/")
def compare_users():
    return render_template(
        "pages/compare_users.html",
        page_title="Compare Users",
        plot="null",
    )

@app.route("/summary-statistics/")
def data_summary_statistics():
    return render_template(
        "pages/data_summary_statistics.html",
        page_title="Data Summary Statistics",
        user_dataframe=METADATA.to_html(
            table_id="summaryTable",
            justify="left",
            columns=["user", "blood_oxygenation", "heart_rate", "sleep", "stress"],
            classes=["table", "table-striped", "table-hover"],
        ),
        plot=None,
    )

def plot_pair(type1, type2, view1, view2):

    view1_line_shape = "linear"
    view2_line_shape = "linear"

    if type1 == "sleep":
        view1_col = "level"
        view1_line_shape = "hv"
    elif type1 == "heart_rate":
        view1_col = "bpm"

    if type2 == "heart_rate":
        view2_col = "bpm"
    elif type2 == "blood_oxygenation":
        view2_col = "spo2"
    elif type2 == "stress":
        view2_col = "stress"

    fig = subplots.make_subplots(rows=2, shared_xaxes=True)
    fig.add_trace(go.Scatter(x=view1.timestamp, y=view1[view1_col], line_shape=view1_line_shape), row=1, col=1)
    fig.add_trace(go.Scatter(x=view2.timestamp, y=view2[view2_col], line_shape=view2_line_shape), row=2, col=1)

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route("/request_pair", methods=["GET", "POST"])
def request_pair():
    user = request.args["user"]
    view1 = request.args["view1"]
    view2 = request.args["view2"]

    df_view1 = pd.read_csv(f"data/{view1}/{user}.csv")
    df_view2 = pd.read_csv(f"data/{view2}/{user}.csv")

    return plot_pair(view1, view2, df_view1, df_view2)

@app.route("/sleep-bpm/")
def sleep_bpm():
    data = load_user_sleep_bpm(DEFAULT_USER)

    # Find the users with >0 sleep and bpm
    # TODO(hayesall): Caching, calculate this once.
    users = METADATA.loc[(METADATA.sleep > 0) & (METADATA.heart_rate > 0)][["user_full", "user"]].to_numpy().tolist()

    return render_template(
        "pages/sleep_bpm.html",
        page_title="Sleep + BPM",
        users=users,
        plot=data,
    )

def load_user_sleep_bpm(user):
    user_sleep = pd.read_csv(f"data/sleep/{user}.csv")
    user_bpm = pd.read_csv(f"data/heart_rate/{user}.csv")

    fig = subplots.make_subplots(rows=2, shared_xaxes=True)
    fig.add_trace(go.Scatter(x=user_sleep.timestamp, y=user_sleep.level, line_shape="hv"), row=1, col=1)
    fig.add_trace(go.Scatter(x=user_bpm.timestamp, y=user_bpm.bpm), row=2, col=1)

    return json.dumps(
        fig,
        cls=plotly.utils.PlotlyJSONEncoder,
    )

@app.route("/sleep-spo2/")
def sleep_spo2():

    users = METADATA.loc[(METADATA.sleep > 0) & (METADATA.blood_oxygenation > 0)][["user_full", "user"]].to_numpy().tolist()

    return render_template(
        "pages/sleep_spo2.html",
        page_title="Sleep + SpO2",
        users=users,
        plot="null",
    )

@app.route("/bpm-stress/")
def sleep_bpm_stress():

    users = METADATA.loc[(METADATA.heart_rate > 0) & (METADATA.stress > 0)][["user_full", "user"]].to_numpy().tolist()

    return render_template(
        "pages/bpm_stress.html",
        page_title="BPM + Stress",
        users=users,
        plot="null",
    )

@app.route("/licenses/")
def licenses():
    return render_template("pages/licenses.html", page_title="Open Source Licenses", plot=None)

@app.route("/update_view", methods=["GET", "POST"])
def update_view():
    user = request.args["user"]
    view = request.args["view"]
    graphJSON = load_user_from_csv(user, view)
    return graphJSON

def load_user_from_csv(user, view):

    df = pd.read_csv(f"data/{view}/{user}.csv")

    plot_line_shape_as = "linear"

    if view == "sleep":
        y_axis = "level"
        plot_line_shape_as = "hv"
    elif view == "blood_oxygenation":
        y_axis = "spo2"
    elif view == "stress":
        y_axis = "stress"
    else:
        # Heart Rate
        y_axis = "bpm"
        plot_line_shape_as = "linear"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df[y_axis], line_shape=plot_line_shape_as))

    if view == "sleep":
        fig.update_yaxes(
            ticktext=["REM", "deep sleep", "light sleep", "awake"],
            tickvals=[0, 1, 2, 3],
        )

    return json.dumps(
        fig,
        cls=plotly.utils.PlotlyJSONEncoder,
    )

if __name__ == "__main__":

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("-d", "--debug", action="store_true", help="Run server in debug mode.")
    PARSER.add_argument("--host", type=str, default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    PARSER.add_argument("--port", type=int, default=5000, help="Server port (default: 5000)")

    ARGS = PARSER.parse_args()

    app.run(debug=ARGS.debug, host=ARGS.host, port=ARGS.port)
