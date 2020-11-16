import asyncio
import ssl
import sys
from pathlib import Path

import pytest

from aiospamc.connections import (
    ConnectionManager,
    TcpConnectionManager,
    UnixConnectionManager,
    Timeout,
    new_connection,
    new_ssl_context,
)
from aiospamc.exceptions import AIOSpamcConnectionFailed, ClientTimeoutException

import certifi


@pytest.fixture
def tcp_address():
    return "localhost", 783


@pytest.fixture
def unix_socket():
    return "/var/run/spamassassin/spamd.sock"


@pytest.fixture
def mock_open_connection(mocker):
    reader, writer = mocker.AsyncMock(), mocker.AsyncMock()
    mocker.patch(
        "asyncio.open_connection", mocker.AsyncMock(return_value=(reader, writer))
    )

    yield reader, writer


@pytest.fixture
def mock_open_connection_refused(mocker):
    mocker.patch("asyncio.open_connection", side_effect=ConnectionRefusedError())

    yield


@pytest.fixture
def mock_open_connection_error(mocker):
    mocker.patch("asyncio.open_connection", side_effect=OSError())

    yield


@pytest.fixture
def mock_open_unix_connection(mocker):
    reader, writer = mocker.AsyncMock(), mocker.AsyncMock()
    mocker.patch(
        "asyncio.open_unix_connection", mocker.AsyncMock(return_value=(reader, writer))
    )

    yield reader, writer


@pytest.fixture
def mock_open_unix_connection_refused(mocker):
    mocker.patch("asyncio.open_unix_connection", side_effect=ConnectionRefusedError())

    yield


@pytest.fixture
def mock_open_unix_connection_error(mocker):
    mocker.patch("asyncio.open_unix_connection", side_effect=OSError())

    yield


@pytest.fixture
def mock_base_connection_string(mocker):
    mocker.patch(
        "aiospamc.connections.ConnectionManager.connection_string",
        return_value="<connection>",
    )
    yield


def test_connection_manager_returns_logger():
    c = ConnectionManager()

    assert c.logger is not None


@pytest.mark.asyncio
async def test_connection_manager_request_sends_and_receives(
    mocker, mock_base_connection_string
):
    test_input = b"request"
    expected = b"response"

    c = ConnectionManager()
    reader = mocker.AsyncMock(spec=asyncio.StreamReader)
    reader.read.return_value = expected
    writer = mocker.AsyncMock(spec=asyncio.StreamWriter)
    c.open = mocker.AsyncMock(return_value=(reader, writer))
    result = await c.request(test_input)

    assert expected == result
    writer.write.assert_called_with(test_input)
    writer.can_write_eof.assert_called()
    writer.write_eof.assert_called()
    writer.drain.assert_awaited()


@pytest.mark.asyncio
async def test_connection_manager_request_sends_without_eof(
    mocker, mock_base_connection_string
):
    test_input = b"request"
    expected = b"response"

    c = ConnectionManager()
    reader = mocker.AsyncMock(spec=asyncio.StreamReader)
    reader.read.return_value = expected
    writer = mocker.AsyncMock(spec=asyncio.StreamWriter)
    writer.can_write_eof.return_value = False
    c.open = mocker.AsyncMock(return_value=(reader, writer))
    result = await c.request(test_input)

    assert expected == result
    writer.write.assert_called_with(test_input)
    writer.can_write_eof.assert_called()
    writer.write_eof.assert_not_called()
    writer.drain.assert_awaited()


@pytest.mark.asyncio
async def test_connection_manager_timeout_total(mocker, mock_base_connection_string):
    async def sleep():
        await asyncio.sleep(5)

        return mocker.AsyncMock(spec=asyncio.StreamReader), mocker.AsyncMock(
            spec=asyncio.StreamWriter
        )

    c = ConnectionManager(timeout=Timeout(total=0))
    c.open = mocker.AsyncMock(side_effect=sleep)

    with pytest.raises(ClientTimeoutException):
        await c.request(b"data")


@pytest.mark.asyncio
async def test_connection_manager_timeout_connect(mocker, mock_base_connection_string):
    async def sleep():
        await asyncio.sleep(5)

        return mocker.AsyncMock(spec=asyncio.StreamReader), mocker.AsyncMock(
            spec=asyncio.StreamWriter
        )

    c = ConnectionManager(timeout=Timeout(connection=0))
    c.open = mocker.AsyncMock(side_effect=sleep)

    with pytest.raises(ClientTimeoutException):
        await c.request(b"data")


@pytest.mark.asyncio
async def test_connection_manager_timeout_read(mocker, mock_base_connection_string):
    async def sleep():
        await asyncio.sleep(5)
        return b"response"

    reader = mocker.AsyncMock(spec=asyncio.StreamReader)
    reader.read = mocker.AsyncMock(side_effect=sleep)

    c = ConnectionManager(timeout=Timeout(response=0))
    c.open = mocker.AsyncMock(
        return_value=(reader, mocker.AsyncMock(spec=asyncio.StreamWriter))
    )

    with pytest.raises(ClientTimeoutException):
        await c.request(b"data")


@pytest.mark.asyncio
async def test_connection_manager_open_raises_not_implemented():
    c = ConnectionManager()

    with pytest.raises(NotImplementedError):
        await c.open()


def test_connection_manager_connection_string_raises_not_implemented():
    c = ConnectionManager()

    with pytest.raises(NotImplementedError):
        c.connection_string


def test_tcp_connection_manager_init(mocker, tcp_address):
    mock_ssl_context = mocker.Mock()
    t = TcpConnectionManager(tcp_address[0], tcp_address[1], mock_ssl_context)

    assert tcp_address[0] == t.host
    assert tcp_address[1] == t.port
    assert mock_ssl_context is t.ssl_context


@pytest.mark.asyncio
async def test_tcp_connection_manager_open(mock_open_connection):
    t = TcpConnectionManager("localhost", 783)
    reader, writer = await t.open()

    assert mock_open_connection[0] is reader
    assert mock_open_connection[1] is writer


@pytest.mark.asyncio
async def test_tcp_connection_manager_open_refused(mock_open_connection_refused):
    t = TcpConnectionManager("localhost", 783)

    with pytest.raises(AIOSpamcConnectionFailed):
        await t.open()


@pytest.mark.asyncio
async def test_tcp_connection_manager_open_refused(mock_open_connection_error):
    t = TcpConnectionManager("localhost", 783)

    with pytest.raises(AIOSpamcConnectionFailed):
        await t.open()


def test_tcp_connection_manager_connection_string(tcp_address):
    t = TcpConnectionManager(tcp_address[0], tcp_address[1])

    assert f"{tcp_address[0]}:{tcp_address[1]}" == t.connection_string


def test_unix_connection_manager_init():
    u = UnixConnectionManager("spamd.sock")

    assert "spamd.sock" == u.path


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.asyncio
async def test_unix_connection_manager_open(mock_open_unix_connection):
    u = UnixConnectionManager("spamd.sock")
    reader, writer = await u.open()

    assert mock_open_unix_connection[0] is reader
    assert mock_open_unix_connection[1] is writer


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.asyncio
async def test_unix_connection_manager_open_refused(mock_open_unix_connection_refused):
    u = UnixConnectionManager("spamd.sock")

    with pytest.raises(AIOSpamcConnectionFailed):
        await u.open()


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.asyncio
async def test_unix_connection_manager_open_refused(mock_open_unix_connection_error):
    u = UnixConnectionManager("spamd.sock")

    with pytest.raises(AIOSpamcConnectionFailed):
        await u.open()


def test_unix_connection_manager_connection_string(unix_socket):
    u = UnixConnectionManager(unix_socket)

    assert unix_socket == u.connection_string


def test_ssl_context_from_none():
    result = new_ssl_context(None)

    assert result is None


def test_ssl_context_from_true(mocker):
    s = mocker.spy(ssl, "create_default_context")
    new_ssl_context(True)

    assert s.call_args.kwargs["cafile"] == certifi.where()


def test_ssl_context_from_false(mocker):
    mocker.spy(ssl, "create_default_context")
    s = new_ssl_context(False)

    assert ssl.create_default_context.call_args.kwargs["cafile"] == certifi.where()
    assert s.check_hostname is False
    assert s.verify_mode == ssl.CERT_NONE


def test_ssl_context_from_dir(mocker, tmp_path):
    mocker.spy(ssl, "create_default_context")
    temp = Path(str(tmp_path))
    s = new_ssl_context(temp)

    assert ssl.create_default_context.call_args.kwargs["capath"] == str(temp)


def test_ssl_context_from_file(mocker, tmp_path):
    mocker.spy(ssl, "create_default_context")
    file = tmp_path / "certs.pem"
    with open(str(file), "wb") as dest:
        with open(certifi.where(), "rb") as source:
            dest.writelines(source.readlines())
    s = new_ssl_context(str(file))

    assert ssl.create_default_context.call_args.kwargs["cafile"] == str(file)


def test_ssl_context_file_not_found(tmp_path):
    file = tmp_path / "nonexistent.pem"

    with pytest.raises(FileNotFoundError):
        new_ssl_context(str(file))


def test_new_connection_returns_unix_manager():
    result = new_connection(socket_path="test.sock")

    assert isinstance(result, UnixConnectionManager)


def test_new_connection_returns_tcp_manager():
    result = new_connection(host="localhost", port=783)

    assert isinstance(result, TcpConnectionManager)


def test_new_connection_returns_tcp_manager_with_ssl(mocker):
    result = new_connection(host="localhost", port=783, context=mocker.Mock())

    assert isinstance(result, TcpConnectionManager)


def test_new_connection_raises_on_missing_parameters():
    with pytest.raises(ValueError):
        new_connection()
