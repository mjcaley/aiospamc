import pytest

from aiospamc.client import Client
from aiospamc.responses import (
    CantCreateException,
    ConfigException,
    DataErrorException,
    InternalSoftwareException,
    IOErrorException,
    NoHostException,
    NoInputException,
    NoPermissionException,
    NoUserException,
    OSErrorException,
    OSFileException,
    ProtocolException,
    Response,
    ResponseException,
    ServerTimeoutException,
    TemporaryFailureException,
    UnavailableException,
    UsageException,
)


async def test_request_sent_to_connection(mock_client, mocker):
    mock_req = mocker.MagicMock()
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()
    await client.request(mock_req, connection, parser)

    assert bytes(mock_req) == client.connection_factory().request.await_args[0][0]


async def test_request_response_sent_to_parser(mock_client, mocker):
    mock_req = mocker.MagicMock()
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()
    mocker.spy(parser, "parse")
    await client.request(mock_req, connection, parser)

    response = connection.request.return_value
    assert response == parser.parse.call_args[0][0]


async def test_request_returns_response(mock_client, mocker):
    mock_req = mocker.MagicMock()
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()
    parse_spy = mocker.spy(parser, "parse")
    result = await client.request(mock_req, connection, parser)
    expected = Response(**parse_spy.spy_return)

    assert expected == result


async def test_request_raises_usage(mock_client_response, mocker, ex_usage):
    mock_client_response(ex_usage)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(UsageException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_data_err(mock_client_response, mocker, ex_data_err):
    mock_client_response(ex_data_err)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(DataErrorException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_no_input(mock_client_response, mocker, ex_no_input):
    mock_client_response(ex_no_input)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(NoInputException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_no_user(mock_client_response, mocker, ex_no_user):
    mock_client_response(ex_no_user)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(NoUserException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_no_host(mock_client_response, mocker, ex_no_host):
    mock_client_response(ex_no_host)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(NoHostException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_unavailable(mock_client_response, mocker, ex_unavailable):
    mock_client_response(ex_unavailable)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(UnavailableException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_software(mock_client_response, mocker, ex_software):
    mock_client_response(ex_software)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(InternalSoftwareException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_os_error(mock_client_response, mocker, ex_os_err):
    mock_client_response(ex_os_err)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(OSErrorException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_os_file(mock_client_response, mocker, ex_os_file):
    mock_client_response(ex_os_file)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(OSFileException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_cant_create(mock_client_response, mocker, ex_cant_create):
    mock_client_response(ex_cant_create)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(CantCreateException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_io_error(mock_client_response, mocker, ex_io_err):
    mock_client_response(ex_io_err)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(IOErrorException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_temporary_failure(
    mock_client_response, mocker, ex_temp_fail
):
    mock_client_response(ex_temp_fail)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(TemporaryFailureException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_protocol(mock_client_response, mocker, ex_protocol):
    mock_client_response(ex_protocol)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(ProtocolException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_no_permission(mock_client_response, mocker, ex_no_perm):
    mock_client_response(ex_no_perm)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(NoPermissionException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_config(mock_client_response, mocker, ex_config):
    mock_client_response(ex_config)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(ConfigException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_timeout(mock_client_response, mocker, ex_timeout):
    mock_client_response(ex_timeout)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(ServerTimeoutException):
        await client.request(mocker.MagicMock(), connection, parser)


async def test_request_raises_undefined(mock_client_response, mocker, ex_undefined):
    mock_client_response(ex_undefined)
    client = Client()
    connection = client.connection_factory()
    parser = client.parser_factory()

    with pytest.raises(ResponseException):
        await client.request(mocker.MagicMock(), connection, parser)
