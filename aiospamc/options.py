#!/usr/bin/env python3

'''Data structures used for function parameters.'''

from collections import namedtuple
from enum import IntEnum


class MessageClassOption(IntEnum):
    '''Option to be used for the MessageClass header.'''

    spam = 1
    ham = 2

ActionOption = namedtuple('ActionOption', ['local', 'remote'])
'''Option to be used in the DidRemove, DidSet, Set, and Remove headers.

local : bool
    An action will be performed on the SPAMD service's local database.
remote : bool
    An action will be performed on the SPAMD service's remote database.
'''
