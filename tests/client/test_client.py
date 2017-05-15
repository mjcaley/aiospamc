#!/usr/bin/env python3

import pytest
from asynctest import CoroutineMock, Mock

from aiospamc import Client
from aiospamc.client import _add_user_header, _add_compress_header
from aiospamc.connections.tcp_connection import TcpConnectionManager
from aiospamc.connections.unix_connection import UnixConnectionManager
from aiospamc.headers import Compress, User
from aiospamc.responses import Response


def test_client_repr():
    client = Client()
    assert repr(client) == ('Client(socket_path=\'/var/run/spamassassin/spamd.sock\', '
                            'host=None, '
                            'port=783, '
                            'user=None, '
                            'compress=False, '
                            'ssl=False)')


def test_tcp_manager():
    client = Client(host='127.0.0.1', port='783')

    assert isinstance(client.connection, TcpConnectionManager)


def test_unix_manager():
    client = Client(socket_path='/var/run/spamassassin/spamd.sock')

    assert isinstance(client.connection, UnixConnectionManager)


def test_value_error():
    with pytest.raises(ValueError):
        client = Client(host=None, socket_path=None)


@pytest.mark.asyncio
@pytest.mark.parametrize('compress,body,called,expected', [
    (None, None, False, None),
    (True, None, False, None),
    (True, 'Body', True, Compress),
])
async def test_compress_decorator(compress,
                                  body,
                                  called,
                                  expected):
    cls = Mock()
    request = Mock()
    cls.compress = compress
    cls.body = body
    cls.func = CoroutineMock()
    cls.func = _add_compress_header(cls.func)

    await cls.func(cls, request)

    assert request.add_header.called is called
    if request.add_header.call_args:
        assert isinstance(request.add_header.call_args[0][0], expected)


@pytest.mark.asyncio
@pytest.mark.parametrize('user,called,expected', [
    (None, False, None),
    ('username', True, User),
])
async def test_user_decorator(user,
                              called,
                              expected):
    cls = Mock()
    request = Mock()
    cls.user = user
    cls.func = CoroutineMock()
    cls.func = _add_user_header(cls.func)

    await cls.func(cls, request)

    assert request.add_header.called is called
    if request.add_header.call_args:
        assert isinstance(request.add_header.call_args[0][0], expected)


@pytest.mark.asyncio
async def test_send(mock_connection, request_ping, response_pong):
    mock_connection.side_effect = [response_pong, ]
    client = Client()

    response = await client.send(request_ping)

    assert isinstance(response, Response)


@pytest.mark.asyncio
async def test_send_tempfail(mock_connection, request_ping, response_pong, ex_temp_fail):
    mock_connection.side_effect = [ex_temp_fail, ex_temp_fail, response_pong]
    client = Client()
    client.sleep_len = 0.1

    response = await client.send(request_ping)

    assert isinstance(response, Response)
