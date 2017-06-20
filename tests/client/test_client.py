#!/usr/bin/env python3

from unittest.mock import patch, MagicMock

import pytest
from asynctest import CoroutineMock, Mock

from aiospamc import Client
from aiospamc.client import _add_user_header, _add_compress_header
from aiospamc.connections.tcp_connection import TcpConnectionManager
from aiospamc.connections.unix_connection import UnixConnectionManager
from aiospamc.exceptions import (BadResponse, ResponseException,
                                 UsageException, DataErrorException, NoInputException, NoUserException,
                                 NoHostException, UnavailableException, InternalSoftwareException, OSErrorException,
                                 OSFileException, CantCreateException, IOErrorException, TemporaryFailureException,
                                 ProtocolException, NoPermissionException, ConfigException, TimeoutException)
from aiospamc.headers import Compress, User
from aiospamc.responses import Response, Status


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


@patch('aiospamc.parser.Success')
def test_response_exception_ok(result):
    result.value.status_code = Status.EX_OK

    assert Client._raise_response_exception(result) is None


@pytest.mark.parametrize('test_input,expected', [
    (Status.EX_USAGE, UsageException),
    (Status.EX_DATAERR, DataErrorException),
    (Status.EX_NOINPUT, NoInputException),
    (Status.EX_NOUSER, NoUserException),
    (Status.EX_NOHOST, NoHostException),
    (Status.EX_UNAVAILABLE, UnavailableException),
    (Status.EX_SOFTWARE, InternalSoftwareException),
    (Status.EX_OSERR, OSErrorException),
    (Status.EX_OSFILE, OSFileException),
    (Status.EX_CANTCREAT, CantCreateException),
    (Status.EX_IOERR, IOErrorException),
    (Status.EX_TEMPFAIL, TemporaryFailureException),
    (Status.EX_PROTOCOL, ProtocolException),
    (Status.EX_NOPERM, NoPermissionException),
    (Status.EX_CONFIG, ConfigException),
    (Status.EX_TIMEOUT, TimeoutException),
    (999, ResponseException)
])
@patch('aiospamc.parser.Success')
def test_response_exception(result, test_input, expected):
    result.value.status_code = test_input

    with pytest.raises(expected):
        Client._raise_response_exception(result)


def test_response_exception_bad():
    result = MagicMock('aiospamc.parser.Failure')
    result.error = 'error'

    with pytest.raises(BadResponse):
        Client._raise_response_exception(result)
