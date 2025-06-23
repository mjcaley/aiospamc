import asyncio
import ssl
import sys
from pathlib import Path

import certifi
import pytest
from pytest_mock import MockerFixture

from aiospamc.connections import (
    ConnectionManager,
    ConnectionManagerBuilder,
    SSLContextBuilder,
    TcpConnectionManager,
    Timeout,
    UnixConnectionManager,
)
from aiospamc.exceptions import AIOSpamcConnectionFailed, ClientTimeoutException


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


def test_connection_manager_returns_logger():
    c = ConnectionManager("connection")

    assert c.logger is not None


async def test_connection_manager_request_sends_and_receives(mocker):
    test_input = b"request"
    expected = b"response"

    c = ConnectionManager("connection")
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


async def test_connection_manager_request_sends_without_eof(mocker):
    test_input = b"request"
    expected = b"response"

    c = ConnectionManager("connection")
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


async def test_connection_manager_timeout_total(mocker):
    async def sleep():
        await asyncio.sleep(5)

        return mocker.AsyncMock(spec=asyncio.StreamReader), mocker.AsyncMock(
            spec=asyncio.StreamWriter
        )

    c = ConnectionManager("connection", timeout=Timeout(total=0))
    c.open = mocker.AsyncMock(side_effect=sleep)

    with pytest.raises(asyncio.TimeoutError):
        await c.request(b"data")


async def test_connection_manager_timeout_connect(mocker):
    async def sleep():
        await asyncio.sleep(5)

        return mocker.AsyncMock(spec=asyncio.StreamReader), mocker.AsyncMock(
            spec=asyncio.StreamWriter
        )

    c = ConnectionManager("connection", timeout=Timeout(connection=0))
    c.open = mocker.AsyncMock(side_effect=sleep)

    with pytest.raises(ClientTimeoutException):
        await c.request(b"data")


async def test_connection_manager_timeout_read(mocker):
    async def sleep():
        await asyncio.sleep(5)
        return b"response"

    reader = mocker.AsyncMock(spec=asyncio.StreamReader)
    reader.read = mocker.AsyncMock(side_effect=sleep)

    c = ConnectionManager("connection", timeout=Timeout(response=0))
    c.open = mocker.AsyncMock(
        return_value=(reader, mocker.AsyncMock(spec=asyncio.StreamWriter))
    )

    with pytest.raises(ClientTimeoutException):
        await c.request(b"data")


async def test_connection_manager_open_raises_not_implemented():
    c = ConnectionManager("connection")

    with pytest.raises(NotImplementedError):
        await c.open()


def test_tcp_connection_manager_init(mocker, hostname, tcp_port):
    mock_ssl_context = mocker.Mock()
    t = TcpConnectionManager(hostname, tcp_port, mock_ssl_context)

    assert hostname == t.host
    assert tcp_port == t.port
    assert mock_ssl_context is t.ssl_context


async def test_tcp_connection_manager_open(mock_reader_writer, hostname, tcp_port):
    t = TcpConnectionManager(hostname, tcp_port)
    reader, writer = await t.open()

    assert mock_reader_writer[0] is reader
    assert mock_reader_writer[1] is writer


async def test_tcp_connection_manager_open_refused(
    mock_open_connection_refused, hostname, tcp_port
):
    t = TcpConnectionManager(hostname, tcp_port)

    with pytest.raises(AIOSpamcConnectionFailed):
        await t.open()


def test_tcp_connection_manager_connection_string(hostname, tcp_port):
    t = TcpConnectionManager(hostname, tcp_port)

    assert f"{hostname}:{tcp_port}" == t.connection_string


def test_unix_connection_manager_init(unix_socket):
    u = UnixConnectionManager(unix_socket)

    assert unix_socket == u.path


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
async def test_unix_connection_manager_open(mock_open_unix_connection, unix_socket):
    u = UnixConnectionManager(unix_socket)
    reader, writer = await u.open()

    assert mock_open_unix_connection[0] is reader
    assert mock_open_unix_connection[1] is writer


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
async def test_unix_connection_manager_open_refused(
    mock_open_unix_connection_refused, unix_socket
):
    u = UnixConnectionManager(unix_socket)

    with pytest.raises(AIOSpamcConnectionFailed):
        await u.open()


def test_unix_connection_manager_connection_string(unix_socket):
    u = UnixConnectionManager(unix_socket)

    assert unix_socket == u.connection_string


def test_connection_manager_builder_builds_unix(unix_socket):
    timeout = Timeout()
    b = (
        ConnectionManagerBuilder()
        .with_unix_socket(unix_socket)
        .set_timeout(timeout)
        .build()
    )

    assert isinstance(b, UnixConnectionManager)
    assert unix_socket == b.path
    assert timeout == b.timeout


def test_connection_manager_builder_builds_tcp(hostname, tcp_port):
    timeout = Timeout()
    b = (
        ConnectionManagerBuilder()
        .with_tcp(hostname, tcp_port)
        .set_timeout(timeout)
        .build()
    )

    assert isinstance(b, TcpConnectionManager)
    assert hostname == b.host
    assert tcp_port == b.port
    assert timeout == b.timeout
    assert None is b.ssl_context


def test_connection_manager_builder_builds_tcp_with_ssl(hostname, tcp_port, mocker):
    ssl_context = mocker.Mock()
    b = (
        ConnectionManagerBuilder()
        .with_tcp(hostname, tcp_port)
        .add_ssl_context(ssl_context)
        .build()
    )

    assert isinstance(b, TcpConnectionManager)
    assert ssl_context == b.ssl_context


def test_ssl_context_builder_default(mocker: MockerFixture):
    default_spy = mocker.spy(ssl, "create_default_context")
    s = SSLContextBuilder().build()

    assert isinstance(s, ssl.SSLContext)
    assert True is default_spy.called


def test_ssl_context_builder_existing_context():
    context = ssl.create_default_context()
    s = SSLContextBuilder().with_context(context).build()

    assert context is s


def test_ssl_context_builder_dont_verify():
    s = SSLContextBuilder().dont_verify().build()

    assert False is s.check_hostname
    assert ssl.CERT_NONE is s.verify_mode


def test_ssl_context_builder_add_certifi(mocker: MockerFixture):
    s = SSLContextBuilder()
    certs_spy = mocker.spy(s._context, "load_verify_locations")
    s.add_default_ca().build()

    assert {"cafile": certifi.where()} == certs_spy.call_args.kwargs


def test_ssl_context_builder_add_cafile(mocker: MockerFixture, server_cert_path):
    s = SSLContextBuilder()
    certs_spy = mocker.spy(s._context, "load_verify_locations")
    s.add_ca_file(server_cert_path).build()

    assert {"cafile": server_cert_path} == certs_spy.call_args.kwargs


def test_ssl_context_builder_add_cadir(mocker: MockerFixture, server_cert_path):
    s = SSLContextBuilder()
    certs_spy = mocker.spy(s._context, "load_verify_locations")
    s.add_ca_dir(server_cert_path.parent).build()

    assert {"capath": server_cert_path.parent} == certs_spy.call_args.kwargs


def test_ssl_context_builder_add_ca_path_of_file(
    mocker: MockerFixture, server_cert_path
):
    s = SSLContextBuilder()
    certs_spy = mocker.spy(s._context, "load_verify_locations")
    s.add_ca(server_cert_path).build()

    assert {"cafile": server_cert_path} == certs_spy.call_args.kwargs


def test_ssl_context_builder_add_ca_path_of_dir(
    mocker: MockerFixture, server_cert_path
):
    s = SSLContextBuilder()
    certs_spy = mocker.spy(s._context, "load_verify_locations")
    s.add_ca(server_cert_path.parent).build()

    assert {"capath": server_cert_path.parent} == certs_spy.call_args.kwargs


def test_ssl_context_builder_add_ca_path_not_found():
    with pytest.raises(FileNotFoundError):
        SSLContextBuilder().add_ca(Path("fake")).build()


def test_ssl_context_builder_add_client_cert(
    mocker: MockerFixture,
    client_cert_path,
    client_key_path,
    client_private_key_password,
):
    builder = SSLContextBuilder()
    certs_spy = mocker.spy(builder._context, "load_cert_chain")

    def password_call():
        return client_private_key_password

    builder.add_client(client_cert_path, client_key_path, password_call).build()

    assert (
        client_cert_path,
        client_key_path,
        password_call,
    ) == certs_spy.call_args.args
