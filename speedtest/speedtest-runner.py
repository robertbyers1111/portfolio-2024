#!/bin/env python3
"""
speedtest-runner.py

A Python script to spawn an instance of Ookla's speedtest CLI utility. Results are appended to an external file in
JSON format.
"""

import json
import logging
import os
import subprocess as sp
from datetime import datetime
from json.decoder import JSONDecodeError
from loggingrmb import LoggingRmb
from subprocess import CalledProcessError

home = os.environ.get("HOME")
log_dir = f"{home}/var/log"
bin_dir = f"{home}/.local/bin"
speedtest_exe = f"{bin_dir}/speedtest"
output_basename = "speedtest.log"
output_file = f"{log_dir}/{output_basename}"
sleep_val = 15


logger = LoggingRmb(name='speedtest', console_level=logging.INFO).setup()
os.makedirs(log_dir, exist_ok=True)


def line_contains_error(line: str) -> bool:
    """
    Checks an input line specifically for an error object (in JSON format). For example...

        "{'error': 'description'}"

    Looks only for the key name 'error' (i.e., 'error' in the description is not checked for)
    """

    try:
        line_json = json.loads(line)
    except JSONDecodeError:
        return False
    return True if 'error' in line_json.keys() else False


def run_speedtest() -> None:
    """
    Runs Ookla's speedtest CLI one time. If an error is detected the test is run again, up to a maximum number of retries.
    Output is in JSON and is appended to the output file.
    """

    logger.info("Running speedtest CLI ({speedtest_exe})")
    logger.info(f"Output is appended to: {output_file}")

    max_attempts = 5
    current_attempt = 0

    while current_attempt < max_attempts:

        current_attempt += 1

        if current_attempt > 1:
            logger.warning(f"This is attempt {current_attempt} of maximum {max_attempts}.")
            sleep(sleep_val)  # wait this many seconds before performing a retry

        try_again = False  # If certain errors are detected this is set to True to trigger a retry

        proc = None
        try:
            t0 = datetime.now()
            proc = sp.run([speedtest_exe, "--format=json"], timeout=60, check=False, capture_output=True, encoding="utf-8")
            t1 = datetime.now()
        except CalledProcessError as ex:
            logger.warning(ex)
            try_again = True

        if proc is None:
            logger.warning("proc is None")
            try_again = True

        else:
            if proc.stderr != '':
                logger.warning("WARNING: non-empty stderr!...")
                for line in proc.stderr:
                    logger.warning(line)
                try_again = True

            if proc.stdout == '':
                logger.warning("WARNING: no output")
                try_again = True

            num_lines = 0
            with open(output_file, "a") as f:
                for line in proc.stdout.split('\n'):
                    if line.strip() != '':
                        f.write(f"{line.strip()}\n")
                        logger.debug(f"{line.strip()}")
                        num_lines += 1
                        if line_contains_error(line):
                            try_again = True

            if num_lines == 0:
                logger.warning("WARNING: Empty output")
                try_again = True

            if num_lines != 1:
                logger.warning(f"WARNING: Expected only 1 line of output, found {num_lines}")
                try_again = True

            if not try_again:
                break

        elapsed = t1 - t0
        elapsed_float = elapsed.seconds + elapsed.microseconds * 0.000001
        logger.info(f"speedtest finished in {elapsed_float:0.3f} seconds")


if __name__ == "__main__":
    run_speedtest()
