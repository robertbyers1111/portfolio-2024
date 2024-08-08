### speedtest

A Python project to assist in identifying weak signals in different rooms of a house. A timeseries data set is maintained in JSON format. Ookla's speedtest CLI utility is spawned, with results appended to the JSON file. The data is then plotted as a timeseries (bandwidth and total throughput, both upload and download) using both matplotlib and plotly.

Features of note
- Nested JSON modeling with Pydantic
- Python subprocess creation
- matplotlib plotting with text annotations
- plotly interactive plot

