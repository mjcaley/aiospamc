#!/usr/bin/env python3

import asyncio

import pytest

from aiospamc.connections.unix_connection import UnixConnection
from aiospamc.exceptions import AIOSpamcConnectionFailed


def test_instantiates(unix_socket):
    conn = UnixConnection(unix_socket)

    assert conn.path is unix_socket


def test_instantiates_with_loop(unix_socket, event_loop):
    conn = UnixConnection(unix_socket, event_loop)

    assert conn.path is unix_socket
    assert conn.loop is event_loop


def test_repr(unix_socket):
    conn = UnixConnection(unix_socket)

    assert repr(conn) == 'UnixConnection(path={})'.format(
            repr(unix_socket)
    )


@pytest.mark.asyncio
async def test_open(unix_socket, open_unix_connection):
    conn = UnixConnection(unix_socket)

    reader, writer = await conn.open()

    assert reader
    assert writer


@pytest.mark.asyncio
async def test_open_refused(unix_socket, unix_connection_refused):
    conn = UnixConnection(unix_socket)

    with pytest.raises(AIOSpamcConnectionFailed):
        await conn.open()


@pytest.mark.asyncio
async def test_open_error(unix_socket, unix_os_error):
    conn = UnixConnection(unix_socket)

    with pytest.raises(AIOSpamcConnectionFailed):
        await conn.open()


def test_connection_string(unix_socket):
    conn = UnixConnection(unix_socket)

    assert conn.connection_string == unix_socket
