"""
loggingrmb.py

A module for instantiating a logging object with my preferred configuration.
"""

import logging
import os
import re
import sys
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

        exe_file = os.path.basename(sys.argv[0])
        exe_base = re.sub(r'\.py$', '', exe_file)
        f_handler = logging.FileHandler(f'{exe_base}.log', mode='w')  # (default mode is 'a')
        f_formatter = logging.Formatter(
                 '[%(asctime)s %(filename)-16.16s:%(lineno)-3.3s %(levelname)-5.5s] %(message)s',
                 datefmt='%Y-%m%d-%H:%M:%S')
        f_handler.setFormatter(f_formatter)

        if len(logger_rmb.handlers) == 0:
            logger_rmb.addHandler(c_handler)
            logger_rmb.addHandler(f_handler)

        logging.getLogger().setLevel(logging.DEBUG)
        c_handler.setLevel(self.console_level)
        f_handler.setLevel(self.file_level)

        return logger_rmb
