#!/usr/bin/env python3

import pytest

from aiospamc.connections.tcp_connection import TcpConnection
from aiospamc.exceptions import AIOSpamcConnectionFailed


def test_instantiates_without_ssl(address):
    conn = TcpConnection(host=address[0], port=address[1])

    assert conn.host is address[0]
    assert conn.port is address[1]
    assert conn.ssl is None


def test_instantiates_with_ssl(address, mocker):
    ssl_stub = mocker.stub()
    conn = TcpConnection(host=address[0], port=address[1], ssl=ssl_stub)

    assert conn.host is address[0]
    assert conn.port is address[1]
    assert conn.ssl is ssl_stub


def test_repr(address):
    conn = TcpConnection(host=address[0], port=address[1])

    assert repr(conn) == 'TcpConnection(host={}, port={}, ssl={})'.format(
            repr(address[0]),
            repr(address[1]),
            repr(None)
    )


@pytest.mark.asyncio
async def test_open(address, open_connection):
    conn = TcpConnection(host=address[0], port=address[1])

    reader, writer = await conn.open()

    assert writer
    assert writer


@pytest.mark.asyncio
async def test_open_refused(address, connection_refused):
    conn = TcpConnection(host=address[0], port=address[1])

    with pytest.raises(AIOSpamcConnectionFailed):
        reader, writer = await conn.open()


@pytest.mark.asyncio
async def test_open_error(address, os_error):
    conn = TcpConnection(host=address[0], port=address[1])

    with pytest.raises(AIOSpamcConnectionFailed):
        reader, writer = await conn.open()


def test_connection_string(address):
    conn = TcpConnection(host=address[0], port=address[1])

    assert conn.connection_string == '{}:{}'.format(address[0], address[1])
