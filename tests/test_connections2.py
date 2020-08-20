from aiospamc.exceptions import AIOSpamcConnectionFailed
from aiospamc.connections import ConnectionManager, TcpConnectionManager, UnixConnectionManager

import asyncio
import pytest


@pytest.fixture
def tcp_address():
    return 'localhost', 783


@pytest.fixture
def unix_socket():
    return '/var/run/spamassassin/spamd.sock'


@pytest.fixture
def mock_open_connection(mocker):
    reader, writer = mocker.AsyncMock(), mocker.AsyncMock()
    mocker.patch(
        'asyncio.open_connection',
        mocker.AsyncMock(return_value=(reader, writer))
    )

    yield reader, writer


@pytest.fixture
def mock_open_connection_refused(mocker):
    mocker.patch(
        'asyncio.open_connection',
        side_effect=ConnectionRefusedError()
    )

    yield


@pytest.fixture
def mock_open_connection_error(mocker):
    mocker.patch(
        'asyncio.open_connection',
        side_effect=OSError()
    )

    yield


@pytest.fixture
def mock_open_unix_connection(mocker):
    reader, writer = mocker.AsyncMock(), mocker.AsyncMock()
    mocker.patch(
        'asyncio.open_unix_connection',
        mocker.AsyncMock(return_value=(reader, writer))
    )

    yield reader, writer


@pytest.fixture
def mock_open_unix_connection_refused(mocker):
    mocker.patch(
        'asyncio.open_unix_connection',
        side_effect=ConnectionRefusedError()
    )

    yield


@pytest.fixture
def mock_open_unix_connection_error(mocker):
    mocker.patch(
        'asyncio.open_unix_connection',
        side_effect=OSError()
    )

    yield


def test_connection_manager_returns_logger():
    c = ConnectionManager()

    assert c.logger is not None


@pytest.mark.asyncio
async def test_connection_manager_request_sends_and_receives(mocker):
    test_input = b'request'
    expected = b'response'

    c = ConnectionManager()
    reader = mocker.AsyncMock(spec=asyncio.StreamReader)
    writer = mocker.AsyncMock(spec=asyncio.StreamWriter)
    reader.read.return_value = expected
    c.open = mocker.AsyncMock(return_value=(reader, writer))
    result = await c.request(test_input)

    assert expected == result
    writer.write.assert_called_with(test_input)


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
    assert mock_ssl_context is t.ssl


@pytest.mark.asyncio
async def test_tcp_connection_manager_open(mock_open_connection):
    t = TcpConnectionManager('localhost', 783)
    reader, writer = await t.open()

    assert mock_open_connection[0] is reader
    assert mock_open_connection[1] is writer


@pytest.mark.asyncio
async def test_tcp_connection_manager_open_refused(mock_open_connection_refused):
    t = TcpConnectionManager('localhost', 783)

    with pytest.raises(AIOSpamcConnectionFailed):
        await t.open()


@pytest.mark.asyncio
async def test_tcp_connection_manager_open_refused(mock_open_connection_error):
    t = TcpConnectionManager('localhost', 783)

    with pytest.raises(AIOSpamcConnectionFailed):
        await t.open()


def test_tcp_connection_manager_connection_string(tcp_address):
    t = TcpConnectionManager(tcp_address[0], tcp_address[1])
    
    assert f'{tcp_address[0]}:{tcp_address[1]}' == t.connection_string


def test_unix_connection_manager_init(mocker):
    mock_ssl_context = mocker.Mock()
    u = UnixConnectionManager('spamd.sock', mock_ssl_context)

    assert 'spamd.sock' == u.path
    assert mock_ssl_context is u.ssl


@pytest.mark.asyncio
async def test_unix_connection_manager_open(mock_open_unix_connection):
    u = UnixConnectionManager('spamd.sock')
    reader, writer = await u.open()

    assert mock_open_unix_connection[0] is reader
    assert mock_open_unix_connection[1] is writer


@pytest.mark.asyncio
async def test_unix_connection_manager_open_refused(mock_open_unix_connection_refused):
    u = UnixConnectionManager('spamd.sock')

    with pytest.raises(AIOSpamcConnectionFailed):
        await u.open()


@pytest.mark.asyncio
async def test_unix_connection_manager_open_refused(mock_open_unix_connection_error):
    u = UnixConnectionManager('spamd.sock')

    with pytest.raises(AIOSpamcConnectionFailed):
        await u.open()


def test_unix_connection_manager_connection_string(unix_socket):
    u = UnixConnectionManager(unix_socket)

    assert unix_socket == u.connection_string
