#!/usr/bin/env python3

import pytest

from aiospamc.connections.unix_connection import UnixConnection, UnixConnectionManager


def test_instantiates(unix_socket):
    conn_man = UnixConnectionManager(unix_socket)

    assert conn_man.path is unix_socket


def test_instantiates_with_loop(unix_socket, event_loop):
    conn_man = UnixConnectionManager(unix_socket, event_loop)

    assert conn_man.path is unix_socket
    assert conn_man.loop is event_loop


def test_repr(unix_socket):
    conn_man = UnixConnectionManager(unix_socket)

    assert repr(conn_man) == 'UnixConnectionManager(path={})'.format(
        repr(unix_socket)
    )


@pytest.mark.asyncio
async def test_new_connection(open_unix_connection, unix_socket):
    conn = UnixConnectionManager(unix_socket)

    async with conn.new_connection() as conn:
        assert isinstance(conn, UnixConnection)
