#!/usr/bin/env python3

'''Data structures used for function parameters.'''

from collections import namedtuple
from enum import IntEnum


class MessageClassOption(IntEnum):
    '''Option to be used for the MessageClass header.'''

    spam = 1
    ham = 2

RemoveOption = namedtuple('RemoveOption', ['local', 'remote'])
'''Option to be used in the DidRemove and Remove headers.

local : bool
    An action will be performed on the SPAMD service's local database.
remote : bool
    An action will be performed on the SPAMD service's remote database.
'''

SetOption = namedtuple('SetOption', ['local', 'remote'])
'''Option to be used in the DidSet and Set headers.

local : bool
    An action will be performed on the SPAMD service's local database.
remote : bool
    An action will be performed on the SPAMD service's remote database.
'''

_Action = namedtuple('Action', ['local', 'remote'])
'''Generic version of RemoveOption and SetOption.'''
