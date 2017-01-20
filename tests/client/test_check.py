#!/usr/bin/env python3

import asyncio

import pytest
from fixtures import *

from aiospamc import Client
from aiospamc.exceptions import BadResponse, SPAMDConnectionRefused
from aiospamc.responses import Response


@pytest.mark.asyncio
async def test_check_connection_refused(event_loop, unused_tcp_port, spam):
    client = Client('localhost', unused_tcp_port, loop=event_loop)
    with pytest.raises(SPAMDConnectionRefused):
        response = await client.check(spam)

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_check_valid_response(spam):
    client = Client()
    response = await client.check(spam)

    assert isinstance(response, Response)

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
@pytest.mark.responses(response_invalid())
async def test_check_invalid_response(spam):
    client = Client()
    with pytest.raises(BadResponse):
        response = await client.check(spam)

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_check_verb_at_start(reader, writer, spam):
    client = Client()
    response = await client.check(spam)

    args = writer.write.call_args
    assert args[0][0].startswith(b'CHECK')

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_check_valid_request(reader, writer, spam):
    client = Client()
    response = await client.check(spam)

    arg = writer.write.call_args
    assert arg[0][0].decode() == 'CHECK SPAMC/1.5\r\nContent-length: {}\r\n\r\n{}'.format(len(spam.encode()), spam)

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_check_compress_header_request(reader, writer, spam):
    client = Client(compress=True)
    response = await client.check(spam)

    args = writer.write.call_args
    assert b'Compress:' in args[0][0]

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_check_user_header_request(reader, writer, spam):
    client = Client(user='TestUser')
    response = await client.check(spam)

    args = writer.write.call_args
    assert b'User: TestUser' in args[0][0]
