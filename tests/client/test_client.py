#!/usr/bin/env python3

import pytest
from asynctest import CoroutineMock, Mock

from aiospamc import Client
from aiospamc.connections.tcp_connection import TcpConnectionManager
from aiospamc.connections.unix_connection import UnixConnectionManager
from aiospamc.exceptions import (BadResponse, ResponseException,
                                 UsageException, DataErrorException, NoInputException, NoUserException,
                                 NoHostException, UnavailableException, InternalSoftwareException, OSErrorException,
                                 OSFileException, CantCreateException, IOErrorException, TemporaryFailureException,
                                 ProtocolException, NoPermissionException, ConfigException, TimeoutException)
from aiospamc.responses import Response


def test_client_repr():
    client = Client(host='localhost')
    assert repr(client) == ('Client(socket_path=\'/var/run/spamassassin/spamd.sock\', '
                            'host=\'localhost\', '
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
async def test_send(stub_connection_manager, request_ping, response_pong):
    client = Client()
    client.connection = stub_connection_manager(return_value=response_pong)

    response = await client.send(request_ping)

    assert isinstance(response, Response)


@pytest.mark.asyncio
async def test_send_with_user(stub_connection_manager, response_with_body, spam, mocker):
    client = Client(host='localhost', user='testuser')
    client.connection = stub_connection_manager(return_value=response_with_body)
    send_spy = mocker.spy(client.connection.connection_stub, 'send')
    await client.check(spam)
    headers = send_spy.call_args[0][0].split(b'\r\n')[1:-1]
    has_user_header = [header.startswith(b'User') for header in headers]

    assert any(has_user_header)


@pytest.mark.asyncio
async def test_send_with_compress(stub_connection_manager, response_with_body, spam, mocker):
    client = Client(host='localhost', compress=True)
    client.connection = stub_connection_manager(return_value=response_with_body)
    send_spy = mocker.spy(client.connection.connection_stub, 'send')
    await client.check(spam)
    headers = send_spy.call_args[0][0].split(b'\r\n')[1:-1]
    has_compress_header = [header.startswith(b'Compress') for header in headers]

    assert any(has_compress_header)


@pytest.mark.asyncio
async def test_raises_usage_exception(stub_connection_manager, ex_usage, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_usage)

    with pytest.raises(UsageException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_data_err_exception(stub_connection_manager, ex_data_err, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_data_err)

    with pytest.raises(DataErrorException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_no_input_exception(stub_connection_manager, ex_no_input, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_no_input)

    with pytest.raises(NoInputException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_no_user_exception(stub_connection_manager, ex_no_user, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_no_user)

    with pytest.raises(NoUserException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_no_host_exception(stub_connection_manager, ex_no_host, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_no_host)

    with pytest.raises(NoHostException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_unavailable_exception(stub_connection_manager, ex_unavailable, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_unavailable)

    with pytest.raises(UnavailableException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_software_exception(stub_connection_manager, ex_software, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_software)

    with pytest.raises(InternalSoftwareException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_os_error_exception(stub_connection_manager, ex_os_err, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_os_err)

    with pytest.raises(OSErrorException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_os_file_exception(stub_connection_manager, ex_os_file, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_os_file)

    with pytest.raises(OSFileException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_cant_create_exception(stub_connection_manager, ex_cant_create, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_cant_create)

    with pytest.raises(CantCreateException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_io_error_exception(stub_connection_manager, ex_io_err, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_io_err)

    with pytest.raises(IOErrorException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_temp_fail_exception(stub_connection_manager, ex_temp_fail, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_protocol_exception(stub_connection_manager, ex_protocol, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_protocol)

    with pytest.raises(ProtocolException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_no_perm_exception(stub_connection_manager, ex_no_perm, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_no_perm)

    with pytest.raises(NoPermissionException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_config_exception(stub_connection_manager, ex_config, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_config)

    with pytest.raises(ConfigException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_raises_timeout_exception(stub_connection_manager, ex_timeout, spam):
    client = Client()
    client.connection = stub_connection_manager(return_value=ex_timeout)

    with pytest.raises(TimeoutException):
        await client.send(spam)


@pytest.mark.asyncio
async def test_bad_response_exception(stub_connection_manager, request_ping):
    c = Client()
    c.connection = stub_connection_manager(return_value=b'invalid')

    with pytest.raises(BadResponse):
        await c.send(request_ping)


@pytest.mark.asyncio
async def test_response_general_exception(stub_connection_manager, ex_undefined, request_ping):
    c = Client()
    c.connection = stub_connection_manager(return_value=ex_undefined)

    with pytest.raises(ResponseException):
        await c.send(request_ping)
