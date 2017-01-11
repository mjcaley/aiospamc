#!/usr/bin/env python3

import asyncio

import pytest

from servers import *

from aiospamc import Client
from aiospamc.exceptions import BadResponse, SPAMDConnectionRefused
from aiospamc.responses import Response


@pytest.mark.asyncio
async def test_process_connection_refused(event_loop, unused_tcp_port):
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    with pytest.raises(SPAMDConnectionRefused):
        response = await client.process(GTUBE)

@pytest.mark.asyncio
async def test_process_valid_response(event_loop, unused_tcp_port):
    server = await valid_response(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    response = await client.process(GTUBE)

    assert isinstance(response, Response)

@pytest.mark.asyncio
async def test_process_invalid_response(event_loop, unused_tcp_port):
    server = await invalid_response(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    with pytest.raises(BadResponse):
        response = await client.process(GTUBE)

@pytest.mark.asyncio
async def test_process_valid_request(event_loop, unused_tcp_port):
    server = await valid_response(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    response = await client.process(GTUBE)

    assert server.request.decode() == 'PROCESS SPAMC/1.5\r\nContent-length: {}\r\n\r\n{}'.format(len(GTUBE.encode()), GTUBE)

@pytest.mark.asyncio
async def test_process_compress_header_request(event_loop, unused_tcp_port):
    server = await valid_response(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, compress=True, loop=event_loop)
    response = await client.process(GTUBE)

    assert b'Compress:' in server.request

@pytest.mark.asyncio
async def test_process_user_header_request(event_loop, unused_tcp_port):
    server = await valid_response(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, user='TestUser', loop=event_loop)
    response = await client.process(GTUBE)

    assert b'User: TestUser' in server.request
