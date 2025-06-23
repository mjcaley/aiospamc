import pytest
from aiospamc.client import Client
from aiospamc.connections import ConnectionManagerBuilder
from aiospamc.exceptions import BadResponse
from aiospamc.requests import Request
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
from pytest_mock import MockerFixture


async def test_successful_response(fake_tcp_server):
    _, host, port = fake_tcp_server
    c = Client(ConnectionManagerBuilder().with_tcp(host, port).build())
    response = await c.request(Request("PING"))

    assert isinstance(response, Response)


async def test_successful_parse_error(fake_tcp_server, response_invalid):
    resp, host, port = fake_tcp_server
    resp.response = response_invalid
    c = Client(ConnectionManagerBuilder().with_tcp(host, port).build())

    with pytest.raises(BadResponse):
        await c.request(Request("PING"))


async def test_raise_for_status_called(fake_tcp_server, mocker: MockerFixture):
    raise_spy = mocker.spy(Response, "raise_for_status")
    _, host, port = fake_tcp_server
    c = Client(ConnectionManagerBuilder().with_tcp(host, port).build())
    response = await c.request(Request("PING"))

    assert isinstance(response, Response)
    assert raise_spy.called
