#!/usr/bin/env python3

"""aiospamc package.

An asyncio-based library to communicate with SpamAssassin's SPAMD service."""

from .connections import Timeout
from .frontend import (
    check,
    headers,
    ping,
    process,
    report,
    report_if_spam,
    symbols,
    tell,
)
from .options import ActionOption, MessageClassOption


__author__ = "Michael Caley"
__copyright__ = "Copyright 2016-2020 Michael Caley"
__license__ = "MIT"
__version__ = "0.7.0"
__email__ = "mjcaley@darkarctic.com"
