from aiospamc.connections2 import ConnectionManager, TcpConnectionManager, UnixConnectionManager

import pytest


@pytest.fixture
def address():
    return 'localhost', 783


@pytest.fixture
def mock_open_connection(mocker):
    reader, writer = mocker.AsyncMock(), mocker.AsyncMock()
    open_conn = mocker.patch(
        'asyncio.open_connection',
        mocker.AsyncMock(return_value=(reader, writer))
    )

    yield reader, writer


def test_connection_manager_returns_logger():
    c = ConnectionManager()

    assert c.logger is not None


@pytest.mark.asyncio
async def test_connection_manager_request_sends_and_receives(mocker):
    test_input = b'request'
    expected = b'response'

    c = ConnectionManager()
    reader, writer = mocker.AsyncMock(), mocker.AsyncMock()
    reader.read.return_value = expected
    c.open = mocker.AsyncMock(return_value=(reader, writer))
    result = await c.request(test_input)

    assert expected == result
    writer.write.assert_called_with(test_input)
