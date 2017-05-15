#!/usr/bin/env python3

import pytest
from asynctest import patch

from aiospamc import Client
from aiospamc.exceptions import BadResponse, AIOSpamcConnectionFailed
from aiospamc.responses import Response
from aiospamc.requests import Request


@pytest.mark.asyncio
@pytest.mark.usefixtures('connection_refused')
async def test_process_connection_refused(spam):
    client = Client()
    with pytest.raises(AIOSpamcConnectionFailed):
        response = await client.process(spam)


@pytest.mark.asyncio
@patch('aiospamc.client.Client.send')
async def test_process_valid_request(mock_connection, spam):
    client = Client()
    response = await client.process(spam)

    request = client.send.call_args[0][0]

    assert isinstance(request, Request)
    assert request.verb == 'PROCESS'
    assert request.body


@pytest.mark.asyncio
async def test_process_valid_response(mock_connection, spam):
    client = Client()
    response = await client.process(spam)

    assert isinstance(response, Response)


@pytest.mark.asyncio
async def test_process_invalid_response(mock_connection, response_invalid, spam):
    mock_connection.side_effect = [response_invalid]

    client = Client()
    with pytest.raises(BadResponse):
        response = await client.process(spam)
