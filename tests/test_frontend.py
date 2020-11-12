#!/usr/bin/env python3

from aiospamc.exceptions import BadResponse
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
    assert "zlib" is req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_check_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await check(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


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
    assert "zlib" is req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_headers_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await headers(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


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
    assert "zlib" is req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_process_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await process(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


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
    assert "zlib" is req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_report_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await report(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


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
    assert "zlib" is req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_report_if_spam_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await report_if_spam(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


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
    assert "zlib" is req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.asyncio
async def test_symbols_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await symbols(spam, client=mock_client_dependency)

    assert req_spy.spy_return is result


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
    assert "zlib" is req.headers["Compress"].algorithm
    assert MessageClassOption.spam == req.headers["Message-class"].value
    assert ActionOption(local=True, remote=True) == req.headers["Set"].action
    assert ActionOption(local=True, remote=True) == req.headers["Remove"].action
    assert spam == req.body


@pytest.mark.asyncio
async def test_tell_returns_response(mock_client_dependency, spam, mocker):
    req_spy = mocker.spy(aiospamc.frontend, "request")
    result = await tell(spam, MessageClassOption.spam, client=mock_client_dependency)

    assert req_spy.spy_return is result
