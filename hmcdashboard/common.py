# Copyright 2022 Alexander L. Hayes
# MIT License

from collections import namedtuple
import json

import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly import subplots


View = namedtuple("View", "readable attribute shape")

class Views:

    VIEWS = {
        "sleep": View("Sleep", "level", "hv"),
        "heart_rate": View("BPM", "bpm", "linear"),
        "blood_oxygenation": View("SpO2", "spo2", "linear"),
        "stress": View("Stress", "stress", "linear"),
    }

    @staticmethod
    def views():
        return list(Views.VIEWS.keys())

    @staticmethod
    def view_name(view):
        return Views.VIEWS[view].readable

    @staticmethod
    def view_attribute(view):
        return Views.VIEWS[view].attribute

    @staticmethod
    def fig_params(view):
        return {"line_shape": Views.VIEWS[view].shape, "mode": "lines"}

    @staticmethod
    def fig_update(view):
        if view == "sleep":
            return {
                "ticktext": ["REM", "deep sleep", "light sleep", "awake"],
                "tickvals": [0, 1, 2, 3],
            }
        return dict()


class Users:

    def __init__(self):
        self.METADATA = pd.read_csv("user_metadata.csv")

    @staticmethod
    def load_user_from_csv(user, view):

        assert view in Views.views()

        return pd.read_csv(f"data/{view}/{user}.csv")

    def get_users(self, view_pair: tuple = None):
        """
        Get user IDs (user_full) and short slugs (user).

        If a `view_pair` is specified, only return users where 1
        or more records exist.
        """

        if not view_pair:
            return self.METADATA[["user_full", "user"]].to_numpy().tolist()

        if len(view_pair) != 2:
            raise ValueError("get_users needs a pair of views, or None")

        assert len(view_pair) == 2
        assert view_pair[0] in Views.views()
        assert view_pair[1] in Views.views()

        _col0 = view_pair[0]
        _col1 = view_pair[1]

        return self.METADATA.loc[
            (self.METADATA[_col0] > 0) & (self.METADATA[_col1] > 0)
        ][["user_full", "user"]].to_numpy().tolist()



def plot_one(dataframe, column: str, readable_name: str, fig_params: dict, fig_update: dict):

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dataframe["timestamp"],
        y=dataframe[column],
        name=readable_name,
        **fig_params,
    ))

    if fig_update:
        fig.update_yaxes(**fig_update)

    return figure_to_json(fig)


def plot_two(dataframe1, dataframe2, view1, view2):

    fig = subplots.make_subplots(rows=2, shared_xaxes=True)

    # Which column should we be looking at?
    col1 = Views.view_attribute(view1)
    col2 = Views.view_attribute(view2)

    fig.add_trace(
        go.Scatter(
            x=dataframe1["timestamp"],
            y=dataframe1[col1],
            name=Views.view_name(view1),
            **Views.fig_params(view1),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=dataframe2["timestamp"],
            y=dataframe2[col2],
            name=Views.view_name(view2),
            **Views.fig_params(view2),
        ),
        row=2,
        col=1,
    )

    if view1 == "sleep":
        fig.update_layout(
            yaxis1=dict(
                ticktext=["REM", "deep sleep", "light sleep", "awake"],
                tickvals=[0, 1, 2, 3]
            )
        )

    return figure_to_json(fig)

def plot_comparison(dataframe1, dataframe2, view, usernames: tuple = None):

    if usernames is None:
        uname1, uname2 = "", ""
    else:
        uname1, uname2 = usernames

    fig = subplots.make_subplots(rows=2, shared_xaxes=True)

    col = Views.view_attribute(view)

    fig.add_trace(
        go.Scatter(
            x=dataframe1.timestamp,
            y=dataframe1[col],
            name=uname1 + " " + Views.view_name(view),
            **Views.fig_params(view),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=dataframe2.timestamp,
            y=dataframe2[col],
            name=uname2 + " " + Views.view_name(view),
            **Views.fig_params(view),
        ),
        row=2,
        col=1,
    )

    if view == "sleep":
        fig.update_layout(
            yaxis1=dict(
                ticktext=["REM", "deep sleep", "light sleep", "awake"],
                tickvals=[0, 1, 2, 3]
            ),
            yaxis2=dict(
                ticktext=["REM", "deep sleep", "light sleep", "awake"],
                tickvals=[0, 1, 2, 3]
            )

        )

    return figure_to_json(fig)

def figure_to_json(figure):
    return json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
