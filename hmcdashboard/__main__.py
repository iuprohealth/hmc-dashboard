# Copyright 2022 Alexander L. Hayes
# MIT License

import argparse

from hmcdashboard.common import Users
from hmcdashboard.common import Views
from hmcdashboard.common import plot_one
from hmcdashboard.common import plot_two
from hmcdashboard.common import plot_comparison

from flask import Flask, render_template, request

app = Flask(__name__)
USERS = None
VIEWS = Views()

DEFAULT_USER = "demo-user-1"
DEFAULT_VIEW = "sleep"


@app.route("/")
def index():
    return render_template(
        "pages/user_overview.html",
        page_title="User Overview",
        users=USERS.get_users(),
        plot=plot_one_user(DEFAULT_USER, DEFAULT_VIEW),
    )

@app.route("/update_view", methods=["GET", "POST"])
def update_view():
    user = request.args["user"]
    view = request.args["view"]
    return plot_one_user(user, view)

def plot_one_user(user, view):
    return plot_one(
        USERS.load_user_from_csv(user, view),
        VIEWS.view_attribute(view),
        VIEWS.view_name(view),
        VIEWS.fig_params(view),
        VIEWS.fig_update(view),
    )

@app.route("/compare-users/")
def compare_users():
    return render_template(
        "pages/compare_users.html",
        page_title="Compare Users",
        users=USERS.get_users(),
        plot=plot_one_user(DEFAULT_USER, DEFAULT_VIEW),
    )

@app.route("/plot_user_comparison", methods=["GET", "POST"])
def plot_user_comparison():
    user1 = request.args["user1"]
    user2 = request.args["user2"]
    view = request.args["view"]

    if user1 == user2:
        return plot_one_user(user1, view)
    else:
        df1 = USERS.load_user_from_csv(user1, view)
        df2 = USERS.load_user_from_csv(user2, view)

        return plot_comparison(df1, df2, view, usernames=(user1[:7], user2[:7]))

@app.route("/summary-statistics/")
def data_summary_statistics():
    return render_template(
        "pages/data_summary_statistics.html",
        page_title="Data Summary Statistics",
        user_dataframe=USERS.METADATA.to_html(
            table_id="summaryTable",
            justify="left",
            columns=["user", "blood_oxygenation", "heart_rate", "sleep", "stress"],
            classes=["table", "table-striped", "table-hover"],
        ),
    )

@app.route("/request_pair", methods=["GET", "POST"])
def request_pair():
    user = request.args["user"]
    view1 = request.args["view1"]
    view2 = request.args["view2"]

    df_view1 = USERS.load_user_from_csv(user, view1)
    df_view2 = USERS.load_user_from_csv(user, view2)

    return plot_two(df_view1, df_view2, view1, view2)

@app.route("/sleep-bpm/")
def sleep_bpm():

    user_sleep = USERS.load_user_from_csv(DEFAULT_USER, "sleep")
    user_bpm = USERS.load_user_from_csv(DEFAULT_USER, "heart_rate")

    return render_template(
        "pages/sleep_bpm.html",
        page_title="Sleep + BPM",
        users=USERS.get_users(view_pair=("sleep", "heart_rate")),
        plot=plot_two(user_sleep, user_bpm, "sleep", "heart_rate"),
    )


@app.route("/sleep-spo2/")
def sleep_spo2():

    user_sleep = USERS.load_user_from_csv(DEFAULT_USER, "sleep")
    user_spo2 = USERS.load_user_from_csv(DEFAULT_USER, "blood_oxygenation")

    return render_template(
        "pages/sleep_spo2.html",
        page_title="Sleep + SpO2",
        users=USERS.get_users(view_pair=("sleep", "blood_oxygenation")),
        plot=plot_two(user_sleep, user_spo2, "sleep", "blood_oxygenation"),
    )

@app.route("/bpm-stress/")
def sleep_bpm_stress():

    users = USERS.get_users(view_pair=("heart_rate", "stress"))

    user_sleep = USERS.load_user_from_csv(DEFAULT_USER, "heart_rate")
    user_stress = USERS.load_user_from_csv(DEFAULT_USER, "stress")

    data = plot_two(user_sleep, user_stress, "heart_rate", "stress")

    return render_template(
        "pages/bpm_stress.html",
        page_title="BPM + Stress",
        users=users,
        plot=data,
    )

@app.route("/licenses/")
def licenses():
    return render_template("pages/licenses.html", page_title="Open Source Licenses", plot=None)



if __name__ == "__main__":

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("-d", "--debug", action="store_true", help="Run server in debug mode.")
    PARSER.add_argument("-p", "--data-path", type=str, default="data", help="Set a path to the data directory.")
    PARSER.add_argument("-m", "--metadata-file", type=str, default="user_metadata.csv", help="Metadata file.")
    PARSER.add_argument("--host", type=str, default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    PARSER.add_argument("--port", type=int, default=5000, help="Server port (default: 5000)")

    ARGS = PARSER.parse_args()

    USERS = Users(data_path=ARGS.data_path, metadata_file=ARGS.metadata_file)

    app.run(debug=ARGS.debug, host=ARGS.host, port=ARGS.port)
