#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Logger objects to give loggers to the rest of the package.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import logging

LOG_FORMAT = "%(asctime)s - %(name)s.%(funcName)s - %(message)s"


def get_logger(name, level=logging.INFO, fmt=LOG_FORMAT):
    """Return a logger object configured to print in stdout

    Args:
        name (str): Logger name
        level (int): Logging level (logging.INFO for instance)
        fmt (str): Logging format

    Returns:
        A logging.Logger object
    """
    # instantiate the logger object
    logger = logging.getLogger(name)

    # configure level
    logger.setLevel(level)

    # create console handler and configure its format
    ch = logging.StreamHandler()
    formatter = logging.Formatter(fmt)
    ch.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(ch)

    return logger
