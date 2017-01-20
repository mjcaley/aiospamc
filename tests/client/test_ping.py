#!/usr/bin/env python3

import asyncio

import pytest
from fixtures import *

from aiospamc import Client
from aiospamc.exceptions import BadResponse, SPAMDConnectionRefused
from aiospamc.responses import Response


@pytest.mark.asyncio
async def test_ping_connection_refused(event_loop, unused_tcp_port):
    client = Client('localhost', unused_tcp_port, loop=event_loop)
    with pytest.raises(SPAMDConnectionRefused):
        response = await client.ping()

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_ping_valid_response():
    client = Client()
    response = await client.ping()

    assert isinstance(response, Response)

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
@pytest.mark.responses(response_invalid())
async def test_ping_invalid_response():
    client = Client()
    with pytest.raises(BadResponse):
        response = await client.ping()

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_ping_verb_at_start(reader, writer):
    client = Client()
    response = await client.ping()

    args = writer.write.call_args
    assert args[0][0].startswith(b'PING')

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_ping_valid_request(reader, writer, request_ping):
    client = Client()
    response = await client.ping()

    args = writer.write.call_args
    assert args[0][0] == request_ping

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_ping_user_header_request(reader, writer):
    client = Client(user='TestUser')
    response = await client.ping()

    args = writer.write.call_args
    assert b'User: TestUser' in args[0][0]
