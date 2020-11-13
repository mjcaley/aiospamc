#!/usr/bin/env python3

"""Data structures used for function parameters."""

from enum import Enum
from typing import NamedTuple


class MessageClassOption(Enum):
    """Option to be used for the MessageClass header."""

    spam = "spam"
    ham = "ham"


class ActionOption(NamedTuple):
    """Option to be used in the DidRemove, DidSet, Set, and Remove headers.

    :param local: An action will be performed on the SPAMD service's local database.
    :param remote: An action will be performed on the SPAMD service's remote database.
    """

    local: bool
    remote: bool
