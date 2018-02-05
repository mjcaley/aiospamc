#!/usr/bin/env python3

import pytest
from asynctest import patch

from aiospamc import Client
from aiospamc.exceptions import BadResponse, AIOSpamcConnectionFailed
from aiospamc.responses import Response
from aiospamc.requests import Request


@pytest.mark.asyncio
@pytest.mark.usefixtures('connection_refused')
async def test_check_connection_refused(unused_tcp_port, spam):
    client = Client(host='localhost', port=unused_tcp_port)
    with pytest.raises(AIOSpamcConnectionFailed):
        response = await client.check(spam)


@pytest.mark.asyncio
@patch('aiospamc.client.Client.send')
async def test_check_valid_request(mock_connection, spam):
    client = Client(host='localhost')
    response = await client.check(spam)

    request = client.send.call_args[0][0]

    assert isinstance(request, Request)
    assert request.verb == 'CHECK'
    assert request.body


@pytest.mark.asyncio
async def test_check_valid_response(mock_connection, spam):
    client = Client(host='localhost')
    response = await client.check(spam)

    assert isinstance(response, Response)


@pytest.mark.asyncio
async def test_check_invalid_response(spam, mock_connection, response_invalid):
    mock_connection.side_effect = [response_invalid]
    client = Client(host='localhost')
    with pytest.raises(BadResponse):
        response = await client.check(spam)
