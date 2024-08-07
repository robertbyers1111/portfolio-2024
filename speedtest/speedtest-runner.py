#!/bin/env python3
"""
speedtest-runner.py

A Python script to spawn an instance of Ookla's speedtest CLI utility. Results are appended to an external file in
JSON format.
"""

import logging
import os
import subprocess as sp
from datetime import datetime
from loggingrmb import LoggingRmb
from subprocess import CalledProcessError

home = os.environ.get("HOME")
log_dir = f"{home}/var/log"
bin_dir = f"{home}/.local/bin"
speedtest_exe = f"{bin_dir}/speedtest"
output_basename = "speedtest.log"
output_file = f"{log_dir}/{output_basename}"


logger = LoggingRmb(name='speedtest', console_level=logging.INFO).setup()
os.makedirs(log_dir, exist_ok=True)


def doit() -> None:

    logger.info("Running speedtest CLI ({speedtest_exe})")
    logger.info(f"Output is appended to: {output_file}")

    t0 = datetime.now()

    proc = None
    try:
        proc = sp.run([speedtest_exe, "--format=json"], timeout=60, check=False, capture_output=True, encoding="utf-8")
    except CalledProcessError as ex:
        logger.warning(ex)

    t1 = datetime.now()

    if proc is None:
        logger.warning("proc is None")

    else:
        if proc.stderr != '':
            logger.warning("WARNING: non-empty stderr!...")
            for line in proc.stderr:
                logger.warning(line)

        if proc.stdout == '':
            logger.warning("WARNING: no output")

        num_lines = 0
        with open(output_file, "a") as f:
            for line in proc.stdout.split('\n'):
                if line.strip() != '':
                    f.write(f"{line.strip()}\n")
                    logger.debug(f"{line.strip()}")
                    num_lines += 1

        if num_lines == 0:
            logger.warning("WARNING: Empty output")

        if num_lines != 1:
            logger.warning(f"WARNING: Expected only 1 line of output, found {num_lines}")

    elapsed = t1 - t0
    elapsed_float = elapsed.seconds + elapsed.microseconds * 0.000001
    logger.info(f"speedtest finished in {elapsed_float:0.3f} seconds")


if __name__ == "__main__":
    doit()
