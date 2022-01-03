import pytest

from aiospamc.client import Client
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
    ServerTimeoutException,
    ResponseException,
)
from aiospamc.responses import Response


@pytest.mark.asyncio
async def test_request_sent_to_connection(mock_client_dependency, mocker, hostname):
    mock_req = mocker.MagicMock()
    await mock_client_dependency.request(mock_req, host=hostname)

    assert (
        bytes(mock_req)
        == mock_client_dependency.connection_factory().request.await_args[0][0]
    )


@pytest.mark.asyncio
async def test_request_response_sent_to_parser(
    mock_client_dependency, mocker, hostname
):
    mock_req = mocker.MagicMock()
    connection = mock_client_dependency.connection_factory()
    parser = mock_client_dependency.parser_factory()
    mocker.spy(parser, "parse")
    await mock_client_dependency.request(mock_req, host=hostname)

    response = connection.request.return_value
    assert response == parser.parse.call_args[0][0]


@pytest.mark.asyncio
async def test_request_returns_response(mock_client_dependency, mocker, hostname):
    mock_req = mocker.MagicMock()
    connection = mock_client_dependency.connection_factory()
    parser = mock_client_dependency.parser_factory()
    parse_spy = mocker.spy(parser, "parse")
    result = await mock_client_dependency.request(mock_req, host=hostname)
    expected = Response(**parse_spy.spy_return)

    assert expected == result


@pytest.mark.asyncio
async def test_request_raises_usage(mock_client_response, mocker, ex_usage, hostname):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_data_err(
    mock_client_response, mocker, ex_data_err, hostname
):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_no_input(
    mock_client_response, mocker, ex_no_input, hostname
):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_no_user(
    mock_client_response, mocker, ex_no_user, hostname
):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_no_host(
    mock_client_response, mocker, ex_no_host, hostname
):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_unavailable(
    mock_client_response, mocker, ex_unavailable, hostname
):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_software(
    mock_client_response, mocker, ex_software, hostname
):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_os_error(
    mock_client_response, mocker, ex_os_err, hostname
):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_os_file(
    mock_client_response, mocker, ex_os_file, hostname
):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_cant_create(
    mock_client_response, mocker, ex_cant_create, hostname
):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_io_error(
    mock_client_response, mocker, ex_io_err, hostname
):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_temporary_failure(
    mock_client_response, mocker, ex_temp_fail, hostname
):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_protocol(
    mock_client_response, mocker, ex_protocol, hostname
):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_no_permission(
    mock_client_response, mocker, ex_no_perm, hostname
):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_config(mock_client_response, mocker, ex_config, hostname):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_timeout(
    mock_client_response, mocker, ex_timeout, hostname
):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(ServerTimeoutException):
        await mock_client.request(mocker.MagicMock(), host=hostname)


@pytest.mark.asyncio
async def test_request_raises_undefined(
    mock_client_response, mocker, ex_undefined, hostname
):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await mock_client.request(mocker.MagicMock(), host=hostname)
