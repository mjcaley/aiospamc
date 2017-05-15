#!/usr/bin/env python3

import asyncio

import pytest
from asynctest import patch, MagicMock

from aiospamc.connections.unix_connection import UnixConnection, UnixConnectionManager
from aiospamc.exceptions import AIOSpamcConnectionFailed


PATH = '/var/run/spamassassin/spamd.sock'


class TestUnixConnectionManager:
    def test_instantiates(self):
        conn_man = UnixConnectionManager(PATH)

        assert 'conn_man' in locals()
        assert conn_man.path is PATH

    def test_instantiates_with_loop(self, event_loop):
        conn_man = UnixConnectionManager(PATH, event_loop)

        assert conn_man.path is PATH
        assert conn_man.loop is event_loop

    def test_repr(self):
        conn_man = UnixConnectionManager(PATH)

        assert repr(conn_man) == 'UnixConnectionManager(path={})'.format(
                repr(PATH)
        )

    @patch('asyncio.open_unix_connection',
           return_value=(MagicMock(spec=asyncio.StreamReader),
                         MagicMock(spec=asyncio.StreamWriter)))
    @pytest.mark.asyncio
    async def test_new_connection(self, *args):
        conn = UnixConnectionManager(PATH)

        async with conn.new_connection() as conn:
            assert isinstance(conn, UnixConnection)


class TestUnixConnection:
    def test_instantiates(self):
        conn = UnixConnection(PATH)

        assert 'conn' in locals()
        assert conn.path is PATH

    def test_instantiates_with_loop(self, event_loop):
        conn = UnixConnection(PATH, event_loop)

        assert 'conn' in locals()
        assert conn.path is PATH
        assert conn.loop is event_loop

    def test_repr(self):
        conn = UnixConnection(PATH)

        assert repr(conn) == 'UnixConnection(path={})'.format(
                repr(PATH)
        )

    @patch('asyncio.open_unix_connection',
           return_value=(MagicMock(spec=asyncio.StreamReader),
                         MagicMock(spec=asyncio.StreamWriter)))
    @pytest.mark.asyncio
    async def test_open(self, *args):
        conn = UnixConnection(PATH)

        reader, writer = await conn.open()

        assert isinstance(reader, asyncio.StreamReader)
        assert isinstance(writer, asyncio.StreamWriter)

    @patch('asyncio.open_connection',
           side_effect=ConnectionError)
    @pytest.mark.asyncio
    async def test_open_refused(self, *args):
        conn = UnixConnection(PATH)

        with pytest.raises(AIOSpamcConnectionFailed):
            reader, writer = await conn.open()

    @patch('asyncio.open_connection',
           side_effect=OSError)
    @pytest.mark.asyncio
    async def test_open_error(self, *args):
        conn = UnixConnection(PATH)

        with pytest.raises(AIOSpamcConnectionFailed):
            reader, writer = await conn.open()

    def test_connection_string(self):
        conn = UnixConnection(PATH)

        assert conn.connection_string == PATH
