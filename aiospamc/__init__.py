#!/usr/bin/env python3

'''aiospamc package.

An asyncio-based library to communicate with SpamAssassin's SPAMD service.'''

from aiospamc.client import Client
from aiospamc.options import MessageClassOption, RemoveOption, SetOption

__all__ = ('Client',
           'MessageClassOption',
           'RemoveOption',
           'SetOption')

__author__ = 'Michael Caley'
__copyright__ = 'Copyright 2016, 2017 Michael Caley'
__license__ = 'MIT'
__version__ = '0.2.0'
__email__ = 'mjcaley@darkarctic.com'
