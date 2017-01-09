#!/usr/bin/env python3

import pytest

from aiospamc import Client


def test_client_repr():
    client = Client()
    assert repr(client) == ('Client(host=\'localhost\', '
                            'port=783, '
                            'user=\'None\', '
                            'compress=False, '
                            'ssl=False)')
