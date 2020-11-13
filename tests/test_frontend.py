#!/usr/bin/env python3

import pytest

import aiospamc
from aiospamc.frontend import (
    request,
    check,
    headers,
    process,
    ping,
    report,
    report_if_spam,
    symbols,
    tell,
    Client,
)
from aiospamc.exceptions import (
    BadResponse,
    UsageException,
    DataErrorException,
    NoInputException,
    NoUserException,
    NoHostException,
    UnavailableException,
    InternalSoftwareException,
    OSErrorException,
    OSFileException,
    CantCreateException,
    IOErrorException,
    TemporaryFailureException,
    ProtocolException,
    NoPermissionException,
    ConfigException,
    TimeoutException,
    ResponseException,
)
from aiospamc.incremental_parser import ResponseParser
from aiospamc.options import ActionOption, MessageClassOption
from aiospamc.responses import Response


@pytest.fixture
def mock_client_dependency(mocker, response_ok):
    ssl_factory = mocker.Mock()
    connection_factory = mocker.Mock()
    connection_factory.return_value.request = mocker.AsyncMock(return_value=response_ok)
    parser_factory = mocker.Mock(return_value=ResponseParser())

    return Client(ssl_factory, connection_factory, parser_factory)


@pytest.fixture
def mock_client_response(mock_client_dependency):
    def inner(response):
        mock_client_dependency.connection_factory.return_value.request.return_value = (
            response
        )

        return mock_client_dependency

    return inner


@pytest.mark.asyncio
async def test_request_sent_to_connection(mock_client_dependency, mocker):
    mock_req = mocker.MagicMock()
    connection = mock_client_dependency.connection_factory()
    parser = mock_client_dependency.parser_factory()
    await request(mock_req, connection, parser)

    assert bytes(mock_req) == connection.request.await_args[0][0]


@pytest.mark.asyncio
async def test_request_response_sent_to_parser(mock_client_dependency, mocker):
    mock_req = mocker.MagicMock()
    connection = mock_client_dependency.connection_factory()
    parser = mock_client_dependency.parser_factory()
    mocker.spy(parser, "parse")
    await request(mock_req, connection, parser)

    response = connection.request.return_value
    assert response == parser.parse.call_args[0][0]


@pytest.mark.asyncio
async def test_request_returns_response(mock_client_dependency, mocker):
    mock_req = mocker.MagicMock()
    connection = mock_client_dependency.connection_factory()
    parser = mock_client_dependency.parser_factory()
    parse_spy = mocker.spy(parser, "parse")
    result = await request(mock_req, connection, parser)
    expected = Response(**parse_spy.spy_return)

    assert expected == result


@pytest.mark.asyncio
async def test_request_raises_bad_response(
    mock_client_response, response_invalid, mocker
):
    mock_client = mock_client_response(response_invalid)
    connection = mock_client.connection_factory()
    parser = mock_client.parser_factory()
    mock_req = mocker.MagicMock()

    with pytest.raises(BadResponse):
        await request(mock_req, connection, parser)


@pytest.mark.asyncio
async def test_request_raises_usage(mock_client_response, mocker, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_data_err(mock_client_response, mocker, ex_data_err):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_no_input(mock_client_response, mocker, ex_no_input):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_no_user(mock_client_response, mocker, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_no_host(mock_client_response, mocker, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_unavailable(mock_client_response, mocker, ex_unavailable):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_software(mock_client_response, mocker, ex_software):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_os_error(mock_client_response, mocker, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_os_file(mock_client_response, mocker, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_cant_create(mock_client_response, mocker, ex_cant_create):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_io_error(mock_client_response, mocker, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_temporary_failure(
    mock_client_response, mocker, ex_temp_fail
):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_protocol(mock_client_response, mocker, ex_protocol):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_no_permission(mock_client_response, mocker, ex_no_perm):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_config(mock_client_response, mocker, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_timeout(mock_client_response, mocker, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(TimeoutException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_request_raises_undefined(mock_client_response, mocker, ex_undefined):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await request(
            mocker.MagicMock(),
            connection=mock_client.connection_factory(),
            parser=mock_client.parser_factory(),
        )


@pytest.mark.asyncio
async def test_check_request_with_default_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await check(spam, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "CHECK" == req.verb
    assert "User" not in req.headers
    assert "Compress" not in req.headers
    assert spam == req.body


@pytest.mark.asyncio
async def test_check_request_with_optional_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await check(spam, user="testuser", compress=True, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "CHECK" == req.verb
    assert "testuser" == req.headers["User"].name
    assert "zlib" == req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_check_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await check(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


@pytest.mark.asyncio
async def test_check_raises_usage(mock_client_response, mocker, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_data_err(mock_client_response, mocker, ex_data_err):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_no_input(mock_client_response, mocker, ex_no_input):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_no_user(mock_client_response, mocker, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_no_host(mock_client_response, mocker, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_unavailable(mock_client_response, mocker, ex_unavailable):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_software(mock_client_response, mocker, ex_software):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_os_error(mock_client_response, mocker, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_os_file(mock_client_response, mocker, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_cant_create(mock_client_response, mocker, ex_cant_create):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_io_error(mock_client_response, mocker, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_temporary_failure(
    mock_client_response, mocker, ex_temp_fail
):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_protocol(mock_client_response, mocker, ex_protocol):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_no_permission(mock_client_response, mocker, ex_no_perm):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_config(mock_client_response, mocker, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_timeout(mock_client_response, mocker, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(TimeoutException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_check_raises_undefined(mock_client_response, mocker, ex_undefined):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await check(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_request_with_default_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await headers(spam, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "HEADERS" == req.verb
    assert "User" not in req.headers
    assert "Compress" not in req.headers
    assert spam == req.body


@pytest.mark.asyncio
async def test_headers_request_with_optional_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await headers(spam, user="testuser", compress=True, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "HEADERS" == req.verb
    assert "testuser" == req.headers["User"].name
    assert "zlib" == req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_headers_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await headers(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


@pytest.mark.asyncio
async def test_headers_raises_usage(mock_client_response, mocker, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_data_err(mock_client_response, mocker, ex_data_err):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_no_input(mock_client_response, mocker, ex_no_input):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_no_user(mock_client_response, mocker, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_no_host(mock_client_response, mocker, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_unavailable(mock_client_response, mocker, ex_unavailable):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_software(mock_client_response, mocker, ex_software):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_os_error(mock_client_response, mocker, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_os_file(mock_client_response, mocker, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_cant_create(mock_client_response, mocker, ex_cant_create):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_io_error(mock_client_response, mocker, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_temporary_failure(
    mock_client_response, mocker, ex_temp_fail
):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_protocol(mock_client_response, mocker, ex_protocol):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_no_permission(mock_client_response, mocker, ex_no_perm):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_config(mock_client_response, mocker, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_timeout(mock_client_response, mocker, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(TimeoutException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_headers_raises_undefined(mock_client_response, mocker, ex_undefined):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await headers(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_ping_request_with_parameters(mock_client_dependency, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await ping(client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "PING" == req.verb
    assert "User" not in req.headers


@pytest.mark.asyncio
async def test_ping_returns_response(mock_client_dependency, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await ping(client=mock_client_dependency)

    assert req_spy.spy_return is result


@pytest.mark.asyncio
async def test_ping_raises_usage(mock_client_response, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_data_err(mock_client_response, ex_data_err):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_no_input(mock_client_response, ex_no_input):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_no_user(mock_client_response, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_no_host(mock_client_response, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_unavailable(mock_client_response, ex_unavailable):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_software(mock_client_response, ex_software):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_os_error(mock_client_response, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_os_file(mock_client_response, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_cant_create(mock_client_response, ex_cant_create):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_io_error(mock_client_response, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_temporary_failure(mock_client_response, ex_temp_fail):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_protocol(mock_client_response, ex_protocol):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_no_permission(mock_client_response, ex_no_perm):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_config(mock_client_response, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_timeout(mock_client_response, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(TimeoutException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_ping_raises_undefined(mock_client_response, ex_undefined):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await ping(client=mock_client)


@pytest.mark.asyncio
async def test_process_request_with_default_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await process(spam, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "PROCESS" == req.verb
    assert "User" not in req.headers
    assert "Compress" not in req.headers
    assert spam == req.body


@pytest.mark.asyncio
async def test_process_request_with_optional_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await process(spam, user="testuser", compress=True, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "PROCESS" == req.verb
    assert "testuser" == req.headers["User"].name
    assert "zlib" == req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_process_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await process(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


@pytest.mark.asyncio
async def test_process_raises_usage(mock_client_response, mocker, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_data_err(mock_client_response, mocker, ex_data_err):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_no_input(mock_client_response, mocker, ex_no_input):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_no_user(mock_client_response, mocker, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_no_host(mock_client_response, mocker, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_unavailable(mock_client_response, mocker, ex_unavailable):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_software(mock_client_response, mocker, ex_software):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_os_error(mock_client_response, mocker, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_os_file(mock_client_response, mocker, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_cant_create(mock_client_response, mocker, ex_cant_create):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_io_error(mock_client_response, mocker, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_temporary_failure(
    mock_client_response, mocker, ex_temp_fail
):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_protocol(mock_client_response, mocker, ex_protocol):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_no_permission(mock_client_response, mocker, ex_no_perm):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_config(mock_client_response, mocker, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_timeout(mock_client_response, mocker, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(TimeoutException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_process_raises_undefined(mock_client_response, mocker, ex_undefined):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await process(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_request_with_default_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await report(spam, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "REPORT" == req.verb
    assert "User" not in req.headers
    assert "Compress" not in req.headers
    assert spam == req.body


@pytest.mark.asyncio
async def test_report_request_with_optional_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await report(spam, user="testuser", compress=True, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "REPORT" == req.verb
    assert "testuser" == req.headers["User"].name
    assert "zlib" == req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_report_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await report(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


@pytest.mark.asyncio
async def test_report_raises_usage(mock_client_response, mocker, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_data_err(mock_client_response, mocker, ex_data_err):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_no_input(mock_client_response, mocker, ex_no_input):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_no_user(mock_client_response, mocker, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_no_host(mock_client_response, mocker, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_unavailable(mock_client_response, mocker, ex_unavailable):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_software(mock_client_response, mocker, ex_software):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_os_error(mock_client_response, mocker, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_os_file(mock_client_response, mocker, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_cant_create(mock_client_response, mocker, ex_cant_create):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_io_error(mock_client_response, mocker, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_temporary_failure(
    mock_client_response, mocker, ex_temp_fail
):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_protocol(mock_client_response, mocker, ex_protocol):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_no_permission(mock_client_response, mocker, ex_no_perm):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_config(mock_client_response, mocker, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_timeout(mock_client_response, mocker, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(TimeoutException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_raises_undefined(mock_client_response, mocker, ex_undefined):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await report(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_request_with_default_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await report_if_spam(spam, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "REPORT_IFSPAM" == req.verb
    assert "User" not in req.headers
    assert "Compress" not in req.headers
    assert spam == req.body


@pytest.mark.asyncio
async def test_report_if_spam_request_with_optional_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await report_if_spam(
        spam, user="testuser", compress=True, client=mock_client_dependency
    )
    req = req_spy.await_args[0][0]

    assert "REPORT_IFSPAM" == req.verb
    assert "testuser" == req.headers["User"].name
    assert "zlib" == req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_report_if_spam_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await report_if_spam(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


@pytest.mark.asyncio
async def test_report_if_spam_raises_usage(mock_client_response, mocker, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_data_err(
    mock_client_response, mocker, ex_data_err
):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_no_input(
    mock_client_response, mocker, ex_no_input
):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_no_user(mock_client_response, mocker, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_no_host(mock_client_response, mocker, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_unavailable(
    mock_client_response, mocker, ex_unavailable
):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_software(
    mock_client_response, mocker, ex_software
):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_os_error(mock_client_response, mocker, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_os_file(mock_client_response, mocker, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_cant_create(
    mock_client_response, mocker, ex_cant_create
):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_io_error(mock_client_response, mocker, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_temporary_failure(
    mock_client_response, mocker, ex_temp_fail
):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_protocol(
    mock_client_response, mocker, ex_protocol
):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_no_permission(
    mock_client_response, mocker, ex_no_perm
):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_config(mock_client_response, mocker, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_timeout(mock_client_response, mocker, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(TimeoutException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_report_if_spam_raises_undefined(
    mock_client_response, mocker, ex_undefined
):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await report_if_spam(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_request_with_default_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await symbols(spam, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "SYMBOLS" == req.verb
    assert "User" not in req.headers
    assert "Compress" not in req.headers
    assert spam == req.body


@pytest.mark.asyncio
async def test_symbols_request_with_optional_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await symbols(spam, user="testuser", compress=True, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "SYMBOLS" == req.verb
    assert "testuser" == req.headers["User"].name
    assert "zlib" == req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_symbols_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await symbols(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


@pytest.mark.asyncio
async def test_symbols_raises_usage(mock_client_response, mocker, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_data_err(mock_client_response, mocker, ex_data_err):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_no_input(mock_client_response, mocker, ex_no_input):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_no_user(mock_client_response, mocker, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_no_host(mock_client_response, mocker, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_unavailable(mock_client_response, mocker, ex_unavailable):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_software(mock_client_response, mocker, ex_software):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_os_error(mock_client_response, mocker, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_os_file(mock_client_response, mocker, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_cant_create(mock_client_response, mocker, ex_cant_create):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_io_error(mock_client_response, mocker, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_temporary_failure(
    mock_client_response, mocker, ex_temp_fail
):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_protocol(mock_client_response, mocker, ex_protocol):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_no_permission(mock_client_response, mocker, ex_no_perm):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_config(mock_client_response, mocker, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_timeout(mock_client_response, mocker, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(TimeoutException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_symbols_raises_undefined(mock_client_response, mocker, ex_undefined):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await symbols(
            mocker.MagicMock(),
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_request_with_default_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await tell(spam, MessageClassOption.spam, client=mock_client_dependency)
    req = req_spy.await_args[0][0]

    assert "TELL" == req.verb
    assert "User" not in req.headers
    assert "Compress" not in req.headers
    assert MessageClassOption.spam == req.headers["Message-class"].value
    assert spam == req.body


@pytest.mark.asyncio
async def test_tell_request_with_optional_parameters(
    mock_client_dependency, spam, mocker
):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    await tell(
        spam,
        MessageClassOption.spam,
        set_action=ActionOption(local=True, remote=True),
        remove_action=ActionOption(local=True, remote=True),
        user="testuser",
        compress=True,
        client=mock_client_dependency,
    )
    req = req_spy.await_args[0][0]

    assert "TELL" == req.verb
    assert "testuser" == req.headers["User"].name
    assert "zlib" == req.headers["Compress"].algorithm
    assert MessageClassOption.spam == req.headers["Message-class"].value
    assert ActionOption(local=True, remote=True) == req.headers["Set"].action
    assert ActionOption(local=True, remote=True) == req.headers["Remove"].action
    assert spam == req.body


@pytest.mark.asyncio
async def test_tell_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await tell(spam, MessageClassOption.spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


@pytest.mark.asyncio
async def test_tell_raises_usage(mock_client_response, mocker, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_data_err(mock_client_response, mocker, ex_data_err):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_no_input(mock_client_response, mocker, ex_no_input):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_no_user(mock_client_response, mocker, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_no_host(mock_client_response, mocker, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_unavailable(mock_client_response, mocker, ex_unavailable):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_software(mock_client_response, mocker, ex_software):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_os_error(mock_client_response, mocker, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_os_file(mock_client_response, mocker, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_cant_create(mock_client_response, mocker, ex_cant_create):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_io_error(mock_client_response, mocker, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_temporary_failure(
    mock_client_response, mocker, ex_temp_fail
):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_protocol(mock_client_response, mocker, ex_protocol):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_no_permission(mock_client_response, mocker, ex_no_perm):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_config(mock_client_response, mocker, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_timeout(mock_client_response, mocker, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(TimeoutException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )


@pytest.mark.asyncio
async def test_tell_raises_undefined(mock_client_response, mocker, ex_undefined):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
            client=mock_client,
        )
