
## Robert Byers
### QA Automation Engineer, SDET, Test Automation
------------

### tidesapp

tidesapp is an application that used Selenium to drive a browser to high tide data for a number of locations and reports the results to the user. Selenium was choses over a RESTful solution because this project is a demo of browser automation. See the *notes* app for a REST application.

Features of note

- Selenium
- pytest
- XPATH
- JSON
- argparse
- Regular expressions (advanced)
- Generator functions

This app has been tested in a linux environment.

I selected tideschart.com for retrieving tide data. It supports retrieval of weekly tide data for most US beaches via a simple URL formulation. For example, to retrieve the current week's tide data for Newburyport, MA, navigating a browser to the following URL is sufficient..

        https://www.tideschart.com/United-States/Massachusetts/Essex-County/Newburyport/

The app is launched from a command line with the following syntax..

`tidesapp -f file`

..where *file* is a JSON file containing a list of URLs. There is no specific limit on the number of URLs, tidesapp will query tide data from each.

The source code for the app itself is in the tides/tidesapp folder. The code for all pytests is in tides/tests.

|  Folder | File   | Description   |
| ------------ | ------------ | ------------ |
| tides/tidesapp   | tidesapp.py  | This is the main application source  |
| tides/tidesapp   | cli_utils.py  | Methods for parsing tidesapp's command line  |
| tides/tidesapp   | datetime_utils.py  | Methods for converting dates and times from the rendered DOM elements into python datetime constructs  |
| tides/tests  | tests_tidesapp.py  | pytest suite for the main application  |
| tides/tests  | tests_cli_utils.py  | pytest unit testing for the CLI utilities  |
| tides/tests  | tests_datetime_utils.py  | pytest unit testing for the datetime utilities  |
| tides/tests  | sample_input.json  | Persistent test input  |
| tides  | setup.cfg  | Sets *pythonpath*, etc.  |


