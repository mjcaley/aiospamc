#!/usr/bin/env python3

import asyncio

import pytest
from asynctest import patch, MagicMock

from aiospamc.connections.tcp_connection import TcpConnection, TcpConnectionManager
from aiospamc.exceptions import AIOSpamcConnectionFailed


LOCALHOST = '127.0.0.1'
PORT = '783'


class TestTcpConnectionManager:
    def test_instantiates(self):
        conn_man = TcpConnectionManager(host=LOCALHOST, port=PORT)

        assert 'conn_man' in locals()
        assert conn_man.host is LOCALHOST
        assert conn_man.port is PORT

    def test_instantiates_with_ssl(self):
        conn_man = TcpConnectionManager(host=LOCALHOST,
                                        port=PORT,
                                        ssl=True)

        assert 'conn_man' in locals()
        assert conn_man.host is LOCALHOST
        assert conn_man.port is PORT
        assert conn_man.ssl is True

    def test_instantiates_with_loop(self, event_loop):
        conn_man = TcpConnectionManager(host=LOCALHOST,
                                        port=PORT,
                                        loop=event_loop)

        assert conn_man.host is LOCALHOST
        assert conn_man.port is PORT
        assert conn_man.loop is event_loop

    def test_repr(self):
        conn_man = TcpConnectionManager(LOCALHOST, PORT)

        assert repr(conn_man) == 'TcpConnectionManager(host={}, port={}, ssl=False)'.format(
                repr(LOCALHOST),
                repr(PORT))

    @patch('asyncio.open_connection',
           return_value=(MagicMock(spec=asyncio.StreamReader),
                         MagicMock(spec=asyncio.StreamWriter)))
    @pytest.mark.asyncio
    async def test_new_connection(self, *args):
        conn = TcpConnectionManager(LOCALHOST, PORT)

        async with conn.new_connection() as conn:
            assert isinstance(conn, TcpConnection)


class TestTcpConnection:
    def test_instantiates_without_ssl(self):
        conn = TcpConnection(host=LOCALHOST,
                             port=PORT,
                             ssl=False)

        assert 'conn' in locals()
        assert conn.host is LOCALHOST
        assert conn.port is PORT
        assert conn.ssl is False

    def test_instantiates_with_ssl(self):
        conn = TcpConnection(host=LOCALHOST,
                             port=PORT,
                             ssl=True)

        assert 'conn' in locals()
        assert conn.host is LOCALHOST
        assert conn.port is PORT
        assert conn.ssl is True

    def test_instantiates_with_loop(self, event_loop):
        conn = TcpConnection(host=LOCALHOST,
                             port=PORT,
                             ssl=False,
                             loop=event_loop)

        assert 'conn' in locals()
        assert conn.host is LOCALHOST
        assert conn.port is PORT
        assert conn.loop is event_loop

    def test_repr(self):
        conn = TcpConnection(host=LOCALHOST,
                             port=PORT,
                             ssl=False)

        assert repr(conn) == 'TcpConnection(host={}, port={}, ssl={})'.format(
                repr(LOCALHOST),
                repr(PORT),
                False
        )

    @patch('asyncio.open_connection',
           return_value=(MagicMock(spec=asyncio.StreamReader),
                         MagicMock(spec=asyncio.StreamWriter)))
    @pytest.mark.asyncio
    async def test_open(self, *args):
        conn = TcpConnection(host=LOCALHOST,
                             port=PORT,
                             ssl=False)

        reader, writer = await conn.open()

        assert isinstance(reader, asyncio.StreamReader)
        assert isinstance(writer, asyncio.StreamWriter)

    @patch('asyncio.open_connection',
           side_effect=ConnectionError)
    @pytest.mark.asyncio
    async def test_open_refused(self, *args):
        conn = TcpConnection(host=LOCALHOST,
                             port=PORT,
                             ssl=False)

        with pytest.raises(AIOSpamcConnectionFailed):
            reader, writer = await conn.open()

    @patch('asyncio.open_connection',
           side_effect=OSError)
    @pytest.mark.asyncio
    async def test_open_error(self, *args):
        conn = TcpConnection(host=LOCALHOST,
                             port=PORT,
                             ssl=False)

        with pytest.raises(AIOSpamcConnectionFailed):
            reader, writer = await conn.open()

    def test_connection_string(self):
        conn = TcpConnection(host=LOCALHOST,
                             port=PORT,
                             ssl=False)

        assert conn.connection_string == '{}:{}'.format(LOCALHOST, PORT)
