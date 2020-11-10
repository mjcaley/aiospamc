#!/usr/bin/env python3

import pytest

from aiospamc.frontend import request, check, headers, process, ping, report, report_if_spam, symbols, tell, Client
from aiospamc.options import ActionOption, MessageClassOption
from aiospamc.responses import Response


@pytest.fixture
def mock_request(mocker):
    yield mocker.patch("aiospamc.frontend.request")


@pytest.fixture
def mock_client_dependency(mocker):
    ssl_factory = mocker.Mock()
    connection_factory = mocker.Mock()
    connection_factory.return_value.request = mocker.AsyncMock()
    parser_factory = mocker.Mock()
    parser_factory.return_value.parse.return_value = {}

    return Client(ssl_factory, connection_factory, parser_factory)


@pytest.mark.asyncio
async def test_request_verify_passed_to_ssl_factory(mocker, spam, mock_client_dependency):
    verify_mock = mocker.Mock()
    await request(
        "CHECK",
        spam,
        verify=verify_mock,
        client=mock_client_dependency
    )

    assert verify_mock == mock_client_dependency.ssl_context_factory.call_args.args[0]


@pytest.mark.asyncio
async def test_request_connection_factory_args_passed(mocker, spam, mock_client_dependency):
    path_mock = mocker.Mock()
    timeout_mock = mocker.Mock()
    await request(
        "CHECK",
        spam,
        socket_path=path_mock,
        timeout=timeout_mock,
        client=mock_client_dependency
    )

    assert "localhost" == mock_client_dependency.connection_factory.call_args.args[0]
    assert 783 == mock_client_dependency.connection_factory.call_args.args[1]
    assert path_mock == mock_client_dependency.connection_factory.call_args.args[2]
    assert timeout_mock == mock_client_dependency.connection_factory.call_args.args[3]
    assert mock_client_dependency.ssl_context_factory.return_value == mock_client_dependency.connection_factory.call_args.args[4]


@pytest.mark.asyncio
async def test_request_parser_cls_instantiated(spam, mock_client_dependency):
    await request(
        "CHECK",
        spam,
        verify=True,
        client=mock_client_dependency
    )

    assert mock_client_dependency.parser_factory.is_called


@pytest.mark.asyncio
async def test_request_parsed_response_is_returned(spam, mock_client_dependency):
    result = await request(
        "CHECK",
        spam,
        verify=True,
        client=mock_client_dependency
    )

    assert isinstance(result, Response)


@pytest.mark.asyncio
async def test_request_passes_user_arg(spam, mock_client_dependency):
    result = await request(
        "CHECK",
        spam,
        user = "username",
        client=mock_client_dependency
    )

    assert b"\r\nUser: username\r\n" in mock_client_dependency.connection_factory.return_value.request.call_args.args[0]


@pytest.mark.asyncio
async def test_request_passes_compress_arg(spam, mock_client_dependency):
    await request(
        "CHECK",
        spam,
        compress = True,
        client=mock_client_dependency
    )

    assert b"\r\nCompress: zlib\r\n" in mock_client_dependency.connection_factory.return_value.request.call_args.args[0]


@pytest.mark.asyncio
async def test_check_default_args_passed(mock_request, spam, mocker):
    socket_path_mock = mocker.Mock()
    timeout_mock = mocker.Mock()
    verify_mock = mocker.Mock()
    user_mock = mocker.Mock()
    compress_mock = mocker.Mock()
    await check(
        spam,
        socket_path=socket_path_mock,
        timeout=timeout_mock,
        verify=verify_mock,
        user=user_mock,
        compress=compress_mock,
    )

    assert "CHECK" == mock_request.await_args.args[0]
    assert "localhost" == mock_request.await_args.kwargs["host"]
    assert 783 == mock_request.await_args.kwargs["port"]
    assert socket_path_mock is mock_request.await_args.kwargs["socket_path"]
    assert timeout_mock is mock_request.await_args.kwargs["timeout"]
    assert verify_mock is mock_request.await_args.kwargs["verify"]
    assert user_mock is mock_request.await_args.kwargs["user"]
    assert compress_mock is mock_request.await_args.kwargs["compress"]


@pytest.mark.asyncio
async def test_check(mock_request, spam):
    result = await check(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_headers_default_args_passed(mock_request, spam, mocker):
    socket_path_mock = mocker.Mock()
    timeout_mock = mocker.Mock()
    verify_mock = mocker.Mock()
    user_mock = mocker.Mock()
    compress_mock = mocker.Mock()
    await headers(
        spam,
        socket_path=socket_path_mock,
        timeout=timeout_mock,
        verify=verify_mock,
        user=user_mock,
        compress=compress_mock,
    )

    assert "HEADERS" == mock_request.await_args.args[0]
    assert "localhost" == mock_request.await_args.kwargs["host"]
    assert 783 == mock_request.await_args.kwargs["port"]
    assert socket_path_mock is mock_request.await_args.kwargs["socket_path"]
    assert timeout_mock is mock_request.await_args.kwargs["timeout"]
    assert verify_mock is mock_request.await_args.kwargs["verify"]
    assert user_mock is mock_request.await_args.kwargs["user"]
    assert compress_mock is mock_request.await_args.kwargs["compress"]


@pytest.mark.asyncio
async def test_headers(mock_request, spam):
    result = await headers(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_ping_default_args_passed(mock_request):
    await ping()

    assert "PING" == mock_request.call_args.args[0]
    assert "localhost" == mock_request.call_args.kwargs["host"]
    assert 783 == mock_request.call_args.kwargs["port"]


@pytest.mark.asyncio
async def test_ping(mock_request):
    result = await ping()

    assert result is mock_request.return_value


@pytest.mark.asyncio
async def test_process_default_args_passed(mock_request, spam):
    await process(spam)

    assert "PROCESS" == mock_request.call_args.args[0]
    assert "localhost" == mock_request.call_args.kwargs["host"]
    assert 783 == mock_request.call_args.kwargs["port"]


@pytest.mark.asyncio
async def test_process(mock_request, spam):
    result = await process(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_report_default_args_passed(mock_request, spam):
    await report(spam)

    assert "REPORT" == mock_request.call_args.args[0]
    assert "localhost" == mock_request.call_args.kwargs["host"]
    assert 783 == mock_request.call_args.kwargs["port"]


@pytest.mark.asyncio
async def test_report(mock_request, spam):
    result = await report(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_report_if_spam_default_args_passed(mock_request, spam):
    await report_if_spam(spam)

    assert "REPORT_IFSPAM" == mock_request.call_args.args[0]
    assert "localhost" == mock_request.call_args.kwargs["host"]
    assert 783 == mock_request.call_args.kwargs["port"]


@pytest.mark.asyncio
async def test_report_if_spam(mock_request, spam):
    result = await report_if_spam(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_symbols_default_args_passed(mock_request, spam):
    await symbols(spam)

    assert "SYMBOLS" == mock_request.call_args.args[0]
    assert "localhost" == mock_request.call_args.kwargs["host"]
    assert 783 == mock_request.call_args.kwargs["port"]


@pytest.mark.asyncio
async def test_symbols(mock_request, spam):
    result = await symbols(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_tell_default_args_passed(mocker, mock_request, spam):
    await tell(spam, message_class=mocker.Mock())

    assert "TELL" == mock_request.call_args.args[0]
    assert "localhost" == mock_request.call_args.kwargs["host"]
    assert 783 == mock_request.call_args.kwargs["port"]
    assert "Set" not in mock_request.await_args.kwargs["headers"]
    assert "Remove" not in mock_request.await_args.kwargs["headers"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message_class,remove_action,set_action",
    [
        ["ham", "local,remote", "local,remote"],
        ["spam", "local,remote", "local,remote"],
        [MessageClassOption.ham, "local,remote", "local,remote"],
        [MessageClassOption.spam, "local,remote", "local,remote"],
        ["spam", ActionOption(local=True, remote=False), "local,remote"],
        ["spam", "local,remote", ActionOption(local=True, remote=False)],
    ],
)
async def test_tell(mock_request, spam, message_class, remove_action, set_action):
    result = await tell(
        spam,
        message_class=message_class,
        remove_action=remove_action,
        set_action=set_action,
    )

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]
    assert message_class == mock_request.await_args.kwargs["headers"]["Message-class"]
    assert remove_action == mock_request.await_args.kwargs["headers"]["Remove"]
    assert set_action == mock_request.await_args.kwargs["headers"]["Set"]
