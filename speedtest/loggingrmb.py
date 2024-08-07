"""
loggingrmb.py

A module for instantiating a logging object with my preferred configuration.
"""

import logging
import os
import subprocess as sp
import typing
from subprocess import CalledProcessError
from datetime import datetime
from time import sleep
from pydantic import BaseModel, Field, ConfigDict


class LoggingRmb(BaseModel):
    model_config = ConfigDict(validate_default=True)

    name: str = Field(max_length=16, default='logging_rmb')
    console_level: int = Field(default=logging.WARNING)
    file_level: int = Field(default=logging.DEBUG)

    def setup(self) -> logging.Logger:

        logger_rmb = logging.getLogger()

        c_handler = logging.StreamHandler()
        c_formatter = logging.Formatter(
                 '[%(asctime)s %(filename)-16.16s:%(lineno)-3.3s %(levelname)-5.5s] %(message)s',
                 datefmt='%Y-%m%d-%H:%M:%S')
        c_handler.setFormatter(c_formatter)
        logger_rmb.addHandler(c_handler)

        f_handler = logging.FileHandler(f'{self.name}.log', mode='w')  # (default mode is 'a')
        f_formatter = logging.Formatter(
                 '[%(asctime)s %(filename)-16.16s:%(lineno)-3.3s %(levelname)-5.5s] %(message)s',
                 datefmt='%Y-%m%d-%H:%M:%S')
        f_handler.setFormatter(f_formatter)
        logger_rmb.addHandler(f_handler)

        logging.getLogger().setLevel(logging.DEBUG)
        c_handler.setLevel(self.console_level)
        f_handler.setLevel(self.file_level)

        return logger_rmb

