#!/usr/bin/env python3

import pytest

import aiospamc
from aiospamc.client import Client


@pytest.fixture
def mock_request(mocker):
    yield mocker.patch("aiospamc.request")


@pytest.fixture
def mock_connection_manager(mocker):
    conn_manager_mock = mocker.Mock()
    conn_manager_mock.return_value.request = mocker.AsyncMock()

    yield conn_manager_mock


@pytest.mark.asyncio
async def test_request_verify_passed_to_ssl_factory(
    mocker, spam, mock_connection_manager
):
    ssl_mock = mocker.Mock()
    verify_mock = mocker.Mock()
    await aiospamc.request(
        "CHECK",
        spam,
        verify=verify_mock,
        ssl_factory=ssl_mock,
        connection_factory=mock_connection_manager,
        parser_cls=mocker.Mock(),
    )

    assert verify_mock == ssl_mock.call_args.args[0]


@pytest.mark.asyncio
async def test_request_connection_factory_args_passed(
    mocker, spam, mock_connection_manager
):
    ssl_mock = mocker.Mock()
    path_mock = mocker.Mock()
    timeout_mock = mocker.Mock()
    await aiospamc.request(
        "CHECK",
        spam,
        socket_path=path_mock,
        timeout=timeout_mock,
        ssl_factory=ssl_mock,
        connection_factory=mock_connection_manager,
        parser_cls=mocker.Mock(),
    )

    assert "localhost" == mock_connection_manager.call_args.args[0]
    assert 783 == mock_connection_manager.call_args.args[1]
    assert path_mock == mock_connection_manager.call_args.args[2]
    assert timeout_mock == mock_connection_manager.call_args.args[3]
    assert ssl_mock.return_value == mock_connection_manager.call_args.args[4]


@pytest.mark.asyncio
async def test_request_parser_cls_instantiated(mocker, spam, mock_connection_manager):
    parser_mock = mocker.Mock()
    await aiospamc.request(
        "CHECK",
        spam,
        verify=True,
        ssl_factory=mocker.Mock(),
        connection_factory=mock_connection_manager,
        parser_cls=parser_mock,
    )

    assert parser_mock.is_called


@pytest.mark.asyncio
async def test_request_parsed_response_is_returned(
    mocker, spam, mock_connection_manager
):
    parser_mock = mocker.Mock()
    result = await aiospamc.request(
        "CHECK",
        spam,
        verify=True,
        ssl_factory=mocker.Mock(),
        connection_factory=mock_connection_manager,
        parser_cls=parser_mock,
    )

    assert result is parser_mock.return_value.parse.return_value


@pytest.mark.asyncio
async def test_request_passes_user_arg(mocker, spam, mock_connection_manager):
    result = await aiospamc.request(
        "CHECK",
        spam,
        user = "username",
        ssl_factory=mocker.Mock(),
        connection_factory=mock_connection_manager,
        parser_cls=mocker.Mock(),
    )

    assert b"\r\nUser: username\r\n" in mock_connection_manager.return_value.request.call_args.args[0]


@pytest.mark.asyncio
async def test_request_passes_compress_arg(mocker, spam, mock_connection_manager):
    await aiospamc.request(
        "CHECK",
        spam,
        compress = True,
        ssl_factory=mocker.Mock(),
        connection_factory=mock_connection_manager,
        parser_cls=mocker.Mock(),
    )

    assert b"\r\nCompress: zlib\r\n" in mock_connection_manager.return_value.request.call_args.args[0]


@pytest.mark.asyncio
async def test_check_default_args_passed(mock_request, spam, mocker):
    socket_path_mock = mocker.Mock()
    timeout_mock = mocker.Mock()
    verify_mock = mocker.Mock()
    user_mock = mocker.Mock()
    compress_mock = mocker.Mock()
    await aiospamc.check(
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
    result = await aiospamc.check(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_headers_default_args_passed(mock_request, spam, mocker):
    socket_path_mock = mocker.Mock()
    timeout_mock = mocker.Mock()
    verify_mock = mocker.Mock()
    user_mock = mocker.Mock()
    compress_mock = mocker.Mock()
    await aiospamc.headers(
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
    result = await aiospamc.headers(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_ping_default_args_passed(mocker, mock_request):
    await aiospamc.ping()

    assert "PING" == mock_request.call_args.args[0]
    assert "localhost" == mock_request.call_args.kwargs["host"]
    assert 783 == mock_request.call_args.kwargs["port"]


@pytest.mark.asyncio
async def test_ping(mock_request):
    result = await aiospamc.ping()

    assert result is mock_request.return_value


@pytest.mark.asyncio
async def test_process_default_args_passed(mock_request, spam):
    await aiospamc.process(spam)

    assert "PROCESS" == mock_request.call_args.args[0]
    assert "localhost" == mock_request.call_args.kwargs["host"]
    assert 783 == mock_request.call_args.kwargs["port"]


@pytest.mark.asyncio
async def test_process(mock_request, spam):
    result = await aiospamc.process(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_report_default_args_passed(mock_request, spam):
    await aiospamc.report(spam)

    assert "REPORT" == mock_request.call_args.args[0]
    assert "localhost" == mock_request.call_args.kwargs["host"]
    assert 783 == mock_request.call_args.kwargs["port"]


@pytest.mark.asyncio
async def test_report(mock_request, spam):
    result = await aiospamc.report(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_report_if_spam_default_args_passed(mock_request, spam):
    await aiospamc.report_if_spam(spam)

    assert "REPORT_IFSPAM" == mock_request.call_args.args[0]
    assert "localhost" == mock_request.call_args.kwargs["host"]
    assert 783 == mock_request.call_args.kwargs["port"]


@pytest.mark.asyncio
async def test_report_if_spam(mock_request, spam):
    result = await aiospamc.report_if_spam(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_symbols_default_args_passed(mock_request, spam):
    await aiospamc.symbols(spam)

    assert "SYMBOLS" == mock_request.call_args.args[0]
    assert "localhost" == mock_request.call_args.kwargs["host"]
    assert 783 == mock_request.call_args.kwargs["port"]


@pytest.mark.asyncio
async def test_symbols(mock_request, spam):
    result = await aiospamc.symbols(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_tell_default_args_passed(mocker, mock_request, spam):
    await aiospamc.tell(spam, message_class=mocker.Mock())

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
        [aiospamc.MessageClassOption.ham, "local,remote", "local,remote"],
        [aiospamc.MessageClassOption.spam, "local,remote", "local,remote"],
        ["spam", aiospamc.ActionOption(local=True, remote=False), "local,remote"],
        ["spam", "local,remote", aiospamc.ActionOption(local=True, remote=False)],
    ],
)
async def test_tell(mock_request, spam, message_class, remove_action, set_action):
    result = await aiospamc.tell(
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
