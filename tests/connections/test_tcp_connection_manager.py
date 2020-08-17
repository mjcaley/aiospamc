#!/usr/bin/env python3

import pytest

from aiospamc.connections.tcp_connection import TcpConnection, TcpConnectionManager


def test_instantiates(address):
    conn_man = TcpConnectionManager(host=address[0], port=address[1])

    assert conn_man.host is address[0]
    assert conn_man.port is address[1]


def test_instantiates_with_ssl(address, mocker):
    ssl_stub = mocker.stub()
    conn_man = TcpConnectionManager(host=address[0], port=address[1], ssl=ssl_stub)

    assert conn_man.host is address[0]
    assert conn_man.port is address[1]
    assert conn_man.ssl is ssl_stub


def test_repr(address):
    conn_man = TcpConnectionManager(address[0], address[1])

    assert repr(conn_man) == 'TcpConnectionManager(host={}, port={}, ssl=None)'.format(
        repr(address[0]),
        repr(address[1])
    )


@pytest.mark.asyncio
async def test_new_connection(address, open_connection):
    conn = TcpConnectionManager(address[0], address[1])

    async with conn.new_connection() as conn:
        assert isinstance(conn, TcpConnection)
