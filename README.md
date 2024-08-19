# Robert Byers
### Python, Test Automation, SDET
- Linkedin: https://www.linkedin.com/in/bobbyers2018/

- Github: https://github.com/robertbyers1111/portfolio-2024
---
### [speedtest](https://github.com/robertbyers1111/portfolio-2024/tree/main/speedtest)

A Python project to assist in identifying weak Wi-Fi signals in different rooms of a house. The project consists of a data collection module (speedtest-runner.py) and a data visualization tool (plot-mbps.py)

The data collection tool may be run via cron (e.g., once every 10 minutes). A timeseries data set is maintained in JSON format. Ookla's speedtest CLI utility is spawned, with results appended to the JSON file.

The data visualization tool is a Plotly Dash app with an interactive plot allowing the user to customize which data are displayed, based on location (address and room).

Features of note
- Nested JSON modeling with Pydantic
- Python subprocess creation
- Plotly Dash plot with a callback decorator for interactive plot updates

---

### [notes app](https://github.com/robertbyers1111/portfolio-2024/tree/main/notes)

A multi-user note-taking app written in Python with an interactive interface and persistent database.

Features of note
- FastAPI
- sqlalchemy
- Supports both SQLite and PostgreSQL databases
---
### [tides](https://github.com/robertbyers1111/portfolio-2024/tree/main/tides)

A selenium-based application to navigate to a tide schedule site and retrieve the tide schedule for a particular location

Features of note
- Selenium
- pytest
- XPATH
- JSON
- argparse
- Generator functions
- Regular expressions (advanced)



