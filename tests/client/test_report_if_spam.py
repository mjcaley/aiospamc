#!/usr/bin/env python3

import asyncio

import pytest

from servers import *

from aiospamc import Client
from aiospamc.exceptions import BadResponse, SPAMDConnectionRefused
from aiospamc.responses import Response


@pytest.mark.asyncio
async def test_report_if_spam_connection_refused(event_loop, unused_tcp_port):
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    with pytest.raises(SPAMDConnectionRefused):
        response = await client.report_if_spam(GTUBE)

@pytest.mark.asyncio
async def test_report_if_spam_valid_response(event_loop, unused_tcp_port):
    mock = MockServer(b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    response = await client.report_if_spam(GTUBE)

    assert isinstance(response, Response)

@pytest.mark.asyncio
async def test_report_if_spam_invalid_response(event_loop, unused_tcp_port):
    mock = MockServer(b'Invalid')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    with pytest.raises(BadResponse):
        response = await client.report_if_spam(GTUBE)

@pytest.mark.asyncio
async def test_report_if_spam_valid_request(event_loop, unused_tcp_port):
    mock = MockServer(b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    response = await client.report_if_spam(GTUBE)

    assert mock.requests[0].decode() == 'REPORT_IFSPAM SPAMC/1.5\r\nContent-length: {}\r\n\r\n{}'.format(len(GTUBE.encode()), GTUBE)

@pytest.mark.asyncio
async def test_report_if_spam_compress_header_request(event_loop, unused_tcp_port):
    mock = MockServer(b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, compress=True, loop=event_loop)
    response = await client.report_if_spam(GTUBE)

    assert b'Compress:' in mock.requests[0]

@pytest.mark.asyncio
async def test_report_if_spam_user_header_request(event_loop, unused_tcp_port):
    mock = MockServer(b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, user='TestUser', loop=event_loop)
    response = await client.report_if_spam(GTUBE)

    assert b'User: TestUser' in mock.requests[0]
