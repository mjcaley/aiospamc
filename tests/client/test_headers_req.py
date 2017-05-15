#!/usr/bin/env python3

import pytest
from asynctest import patch

from aiospamc import Client
from aiospamc.exceptions import BadResponse, AIOSpamcConnectionFailed
from aiospamc.responses import Response
from aiospamc.requests import Request


@pytest.mark.asyncio
@pytest.mark.usefixtures('connection_refused')
async def test_headers_req_connection_refused(spam):
    client = Client()
    with pytest.raises(AIOSpamcConnectionFailed):
        response = await client.headers(spam)


@pytest.mark.asyncio
@patch('aiospamc.client.Client.send')
async def test_headers_req_valid_request(mock_connection, spam):
    client = Client()
    response = await client.headers(spam)

    request = client.send.call_args[0][0]

    assert isinstance(request, Request)
    assert request.verb == 'HEADERS'
    assert request.body


@pytest.mark.asyncio
async def test_headers_req_valid_response(mock_connection, spam):
    client = Client()
    response = await client.headers(spam)

    assert isinstance(response, Response)


@pytest.mark.asyncio
async def test_headers_req_invalid_response(mock_connection, response_invalid, spam):
    mock_connection.side_effect = [response_invalid]

    client = Client()
    with pytest.raises(BadResponse):
        response = await client.headers(spam)
