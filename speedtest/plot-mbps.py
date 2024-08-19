#!/usr/bin/env python3
"""
plot-mbps.py

A plotly application to plot timeseries data collected from the Ookla speedtest CLI. Input is in JSON, with data
validation and data modeling performed with Pydantic (see model.py). Output is opened in an interactive plotly chart or
saved to an image file (see variable 'plotly_output').

The impetus of this program is to assist in identifying weak Wi-Fi signal strength in various locations of a building.
Annotations of the data are supported and allow calling-out of notable changes in throughput as the base system (a
laptop) is moved to different areas of the building.

Follows several principles from 'Clean Code' (R.C. Martin, 2008), including *not* documenting function and method
parameters (in favor of using appropriately descriptive method and parameter names with Python type hints).
"""

import json
import logging
import pandas as pd
from pandas.core.frame import DataFrame
from model import MainObject
from typing import List
from pydantic import ValidationError
from loggingrmb import LoggingRmb
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

app = Dash(__name__)

logger = LoggingRmb(console_level=logging.INFO).setup()


input_json_file = "speedtest-example.json"
output_png_file = "speedtest.png"
plotly_output = "show"  # An image filename, or "show" for an interactive plot


def read_jsonl_file(file_path: str) -> List[MainObject]:
    line_num = 0
    lines_read = 0
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            line_num += 1
            try:
                json_data = json.loads(line)
                obj = MainObject(**json_data)
                data.append(obj)
            except json.JSONDecodeError as e:
                logger.debug(f"Line {line_num}: JSON decode error: {e}")
                continue
            except ValidationError as e:
                logger.debug(f"Line {line_num}: Validation error: {e}")
                continue
            except Exception as e:
                logger.debug(f"Line {line_num}: Error: {e}")
                continue
            lines_read += 1

    logger.info(f"Lines input: {line_num}")
    logger.info(f"Lines processed: {lines_read}")
    if line_num != lines_read:
        logger.info('(see log file for JSON, validation and other input errors)')

    return data


def create_dataframe(data_objects: List) -> DataFrame:

    df_prep = []
    for data_object in data_objects:

        # Don't display zero-valued data
        download_mbps = data_object.download.mbps if data_object.download.mbps > 0. else float('nan')
        upload_mbps = data_object.upload.mbps if data_object.upload.mbps > 0. else float('nan')
        download_bandwidth_mbytesec = data_object.download.bw_mbytesec if data_object.download.bw_mbytesec > 0. else float('nan')
        upload_bandwidth_mbytesec = data_object.upload.bw_mbytesec if data_object.upload.bw_mbytesec > 0. else float('nan')
        
        df_prep.append({
            "timestamp": data_object.timestamp_,
            "date": data_object.timestamp_.date(),
            "time": data_object.timestamp_.time(),
            "download_mbps": download_mbps,
            "upload_mbps": upload_mbps,
            "download_bandwidth_mbytesec": download_bandwidth_mbytesec,
            "upload_bandwidth_mbytesec": upload_bandwidth_mbytesec,
            "address": f'{data_object.address.address}_{data_object.address.room}'
        })

    df = pd.DataFrame(df_prep)

    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 200):
        logger.debug(df)

    return df


@app.callback(
    Output(component_id='graph', component_property='figure'),
    Input(component_id='addresses_checklist', component_property='value'),
    prevent_initial_call=True
)
def update_graph(enabled_addresses):
    print(f'{enabled_addresses:}')
    df_update = speedtest_dataframe[speedtest_dataframe['address'].isin(enabled_addresses)]
    fig_update = px.line(df_update, x='timestamp', y=['download_mbps', 'upload_mbps'], color='address')
    fig_update.update_xaxes(title_text=None)
    fig_update.update_yaxes(title_text='Speed (Mbps)')
    for i in range(1, len(fig_update['data']), 2):
        fig_update['data'][i].line.color = 'gray'
    return fig_update


if __name__ == "__main__":

    speedtest_data = read_jsonl_file(input_json_file)
    speedtest_dataframe = create_dataframe(speedtest_data)

    fig = px.line(speedtest_dataframe, x='timestamp', y=['download_mbps', 'upload_mbps'], color='address')
    fig.update_xaxes(title_text=None)
    fig.update_yaxes(title_text='Speed (Mbps)')

    # Force all upload_mpbs lines to be their own color, leaving only download_mbps line colors to be unique
    for i in range(1, len(fig['data']), 2):
        fig['data'][i].line.color = 'gray'

    # List of unique addresses in the dataframe (for the Dash checklist)
    addresses = sorted(list(set(speedtest_dataframe['address'])))

    app.layout = html.Div([
        html.Div(id="dash-title", children="Speedtest Results"),
        html.Hr(),
        dcc.Checklist(addresses, addresses, id='addresses_checklist'),
        html.Hr(),
        dcc.Graph(id="graph", figure=fig)
    ])

    app.run(debug=True)
