#!/usr/bin/env python3

import pytest

from aiospamc.connections import ConnectionManager


def test_instantiates():
    conn_man = ConnectionManager()

    assert 'conn_man' in locals()

def test_new_connection_not_implemented():
    conn_man = ConnectionManager()

    with pytest.raises(NotImplementedError):
        conn_man.new_connection()
