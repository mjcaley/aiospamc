"""aiospamc package.

An asyncio-based library to communicate with SpamAssassin's SPAMD service."""

from importlib.metadata import version

from loguru import logger

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
from .header_values import ActionOption, MessageClassOption

__author__ = "Michael Caley"
__copyright__ = "Copyright 2016-2025 Michael Caley"
__license__ = "MIT"
__version__ = version("aiospamc")
__email__ = "mjcaley@darkarctic.com"
__all__ = [
    "Timeout",
    "check",
    "headers",
    "ping",
    "process",
    "report",
    "report_if_spam",
    "symbols",
    "tell",
    "ActionOption",
    "MessageClassOption",
]

logger.disable(__package__)
