#!/usr/bin/env python3

import pytest
from asynctest import patch

from aiospamc import Client
from aiospamc.exceptions import BadResponse, AIOSpamcConnectionFailed
from aiospamc.responses import Response
from aiospamc.requests import Request


@pytest.mark.asyncio
@pytest.mark.usefixtures('connection_refused')
async def test_ping_connection_refused():
    client = Client()
    with pytest.raises(AIOSpamcConnectionFailed):
        response = await client.ping()


@pytest.mark.asyncio
@patch('aiospamc.client.Client.send')
async def test_ping_valid_request(mock_connection):
    client = Client()
    response = await client.ping()

    request = client.send.call_args[0][0]

    assert isinstance(request, Request)
    assert request.verb == 'PING'


@pytest.mark.asyncio
async def test_ping_valid_response(mock_connection):
    client = Client()
    response = await client.ping()

    assert isinstance(response, Response)


@pytest.mark.asyncio
async def test_ping_invalid_response(mock_connection, response_invalid):
    mock_connection.side_effect = [response_invalid]

    client = Client()
    with pytest.raises(BadResponse):
        response = await client.ping()
