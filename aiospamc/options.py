#!/usr/bin/env python3

'''Data structures used for function parameters.'''

from enum import Enum, auto
from typing import NamedTuple


class MessageClassOption(Enum):
    '''Option to be used for the MessageClass header.'''

    spam = auto()
    ham = auto()


class ActionOption(NamedTuple):
    '''Option to be used in the DidRemove, DidSet, Set, and Remove headers.

    :param local: bool
        An action will be performed on the SPAMD service's local database.
    :param remote: bool
        An action will be performed on the SPAMD service's remote database.
    '''

    local: bool
    remote: bool
