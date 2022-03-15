import argparse
import json
import time
from flask import Flask, render_template, request
import plotly
import plotly.graph_objs as go
import pandas as pd

app = Flask(__name__)


SLEEP_DELAY = 0
DEFAULT_USER = "demo-user-1"
DEFAULT_VIEW = "sleep"


@app.route("/")
def index():
    time.sleep(SLEEP_DELAY)
    data = load_user_from_csv(DEFAULT_USER, DEFAULT_VIEW)
    return render_template("base.html", plot=data)

@app.route("/sleep-bpm/")
def sleep_bpm():
    time.sleep(SLEEP_DELAY)
    data = load_user_from_csv(DEFAULT_USER, DEFAULT_VIEW)
    return render_template("base.html", plot=data)


@app.route("/update_view", methods=["GET", "POST"])
def update_view():
    user = request.args["user"]
    view = request.args["view"]

    time.sleep(SLEEP_DELAY)
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
