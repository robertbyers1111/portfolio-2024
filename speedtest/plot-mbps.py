#!/usr/bin/env python3
"""
plot-mbps.py

A matplotlib-based application to plot timeseries data collected from the Oookla speedtest CLI. Input is in JSON, with
data validation and data modeling performed with Pydantic (see model.py). Output is in the form of a plot saved to a
graphics file.

The impetus of this program is to assist in identifying weak wifi signal strength in various locations of a building.
Annotations of the data are supported and allow calling-out of notable changes in throughput as the base system (a
laptop) is moved to different areas of the building.

Follows several principles from 'Clean Code' (R.C. Martin, 2008), including *not* documenting function and method
parameters (in favor of using appropriately descriptive method and parameter names with Python type hints).
"""

import json
import logging
import matplotlib.pyplot as plt
import pandas as pd
from pandas.core.frame import DataFrame
from model import MainObject
from typing import List
from pydantic import ValidationError
from loggingrmb import LoggingRmb
import matplotlib.patches as patches
import plotly.express as px

logger = LoggingRmb(name='plot-mbps', console_level=logging.INFO).setup()


input_json_file = "speedtest.json"
output_png_file = "speedtest.png"
plotly_output = "show"  # set to an image filename, or to "show" for an interactive plot


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
                logger.warning(f"Line {line_num}: JSON decode error: {e}")
                continue
            except ValidationError as e:
                logger.warning(f"Line {line_num}: Validation error: {e}")
                continue
            except Exception as e:
                logger.warning(f"Line {line_num}: Error: {e}")
                continue
            lines_read += 1

    logger.info(f"Lines input: {line_num}")
    logger.info(f"Lines processed: {lines_read}")

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
        })

    df = pd.DataFrame(df_prep)

    # Create a new column for time of day to use as x-axis
    df['time_of_day'] = df['timestamp'].dt.time

    # Melt the DataFrame to have a single 'speed' column and a 'type' column (download/upload)
    df_melted = df.melt(id_vars=['date', 'time_of_day'], value_vars=['download_mbps', 'upload_mbps'],
                        var_name='type', value_name='speed')

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        logger.info(df)

    fig = px.line(df_melted, x='time_of_day', y='speed', color='date', line_dash='type',
                  labels={'speed': 'Speed (Mbps)', 'time_of_day': 'Time of Day'},
                  title='Upload and Download Speeds by Day')

    fig.show()

    return df_melted


def do_callouts(df, ax, callouts):

    if callouts is not None:
        callout: object
        for callout in callouts:
            idx, text_value = callout
            annotate_date = df.index[idx]  # Choose a date to annotate
            ax.annotate(text_value,
                        xy=(annotate_date, df.loc[annotate_date, 'download_mbps']),
                        xytext=(annotate_date - pd.Timedelta(hours=8), df.loc[annotate_date, 'download_mbps'] - 100),
                        arrowprops=dict(facecolor='black', shrink=0.05),
                        )


def generate_plot(df: DataFrame, plotfile: str, callouts: List = None) -> None:

    df.set_index('timestamp', inplace=True)
    fig, ax1 = plt.subplots(figsize=(16, 9))
    ax2 = ax1.twinx()
    df[['download_mbps', 'upload_mbps']].plot(ax=ax1)
    df[['download_bandwidth_mbytesec', 'upload_bandwidth_mbytesec']].plot(ax=ax2, color=['red', 'green'], style='--')
    do_callouts(df, ax1, callouts)
    ax1.set_ylabel("Throughput (Mbps)")
    ax2.set_ylabel("Bandwidth (MBytes/sec)")
    ax1.legend_.remove()
    ax2.legend_.remove()
    ax1.set_facecolor('lightcyan')
    plt.title("Ookla Speedtest")
    plt.grid(True)
    fig.legend(loc='lower center', ncol=3)
    fig.set_facecolor('paleturquoise')
    fig.patch.set_linewidth(4)
    rect = patches.Rectangle((0, 0), 1, 1, linewidth=4, edgecolor='black', facecolor='none', transform=fig.transFigure)
    fig.patches.append(rect)

    plt.savefig(plotfile)


def generate_plotly_plot(df: DataFrame, plotfile: str) -> None:

    # Plot with Plotly Express, color by 'date' and line type by 'type'
    fig = px.line(df, x='time_of_day', y='speed', color='date', line_dash='type',
                  labels={'speed': 'Speed (Mbps)', 'time_of_day': 'Time of Day'},
                  title='Upload and Download Speeds by Day')

    fig.show() if plotfile == "show" else fig.write_image(plotfile)


if __name__ == "__main__":

    speedtest_data = read_jsonl_file(input_json_file)
    speedtest_dataframe = create_dataframe(speedtest_data)

    # generate_plot(speedtest_dataframe, output_png_file, [
    #     (40, 'to fam room'),
    #     (69, 'to fam room'),
    #     (135, 'to fam room'),
    #     (213, 'to fam room')
    # ])

    # generate_plotly_plot(speedtest_dataframe, plotly_output)
