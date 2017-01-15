#!/usr/bin/env python3

import asyncio

import pytest

from servers import *

from aiospamc import Client
from aiospamc.exceptions import BadResponse, SPAMDConnectionRefused
from aiospamc.headers import ContentLength, MessageClass, Remove, Set
from aiospamc.options import MessageClassOption, RemoveOption, SetOption
from aiospamc.responses import Response
from aiospamc.requests import Request


@pytest.mark.asyncio
async def test_tell_connection_refused(event_loop, unused_tcp_port):
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    with pytest.raises(SPAMDConnectionRefused):
        response = await client.tell(MessageClassOption.spam,
                                     GTUBE,
                                     SetOption(local=True, remote=True))

@pytest.mark.asyncio
@pytest.mark.parametrized('test_input,expected', [
    (RemoveOption(local=True, remote=False), 'Remove: local\r\n'),
    (RemoveOption(local=False, remote=True), 'Remove: remote\r\n'),
    (RemoveOption(local=True, remote=True), 'Remove: local, remote\r\n'),
    (SetOption(local=True, remote=False), 'Set: local\r\n'),
    (SetOption(local=False, remote=True), 'Set: remote\r\n'),
    (SetOption(local=True, remote=True), 'Set: local, remote\r\n'),
])
async def test_tell_valid_request(event_loop, unused_tcp_port, test_input, expected):
    mock = MockServer(b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    response = await client.tell(MessageClassOption.spam,
                                 GTUBE,
                                 test_input)

    assert expected in server.requests[0]

@pytest.mark.asyncio
@pytest.mark.parametrize('test_input,expected', [
    (RemoveOption(local=True, remote=False), Request('TELL',
                                                     GTUBE,
                                                     MessageClass(MessageClassOption.spam),
                                                     Remove(RemoveOption(local=True, remote=True)),)),
    (SetOption(local=True, remote=False), Request('TELL',
                                                  GTUBE,
                                                  MessageClass(MessageClassOption.spam),
                                                  Set(SetOption(local=True, remote=True)),))
])
async def test_tell_request_call(event_loop, unused_tcp_port, mocker, test_input, expected):
    mock = MockServer(b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    mocker.spy(client, 'send')
    response = await client.tell(MessageClassOption.spam,
                                 GTUBE,
                                 test_input)

    assert client.send.call_args == ((expected,),)

@pytest.mark.asyncio
async def test_tell_valid_response(event_loop, unused_tcp_port):
    mock = MockServer(b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    response = await client.tell(MessageClassOption.spam,
                                 GTUBE,
                                 SetOption(local=True, remote=True))

    assert isinstance(response, Response)

@pytest.mark.asyncio
async def test_tell_invalid_response(event_loop, unused_tcp_port):
    mock = MockServer(b'Invalid')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    with pytest.raises(BadResponse):
        response = await client.tell(MessageClassOption.spam,
                                     GTUBE,
                                     SetOption(local=True, remote=True))

@pytest.mark.asyncio
async def test_tell_valid_request(event_loop, unused_tcp_port):
    mock = MockServer(b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    response = await client.tell(MessageClassOption.spam,
                                 GTUBE,
                                 SetOption(local=True, remote=True))

    # We can't guarantee the order of the headers, so we have to break things up
    assert ((mock.requests[0].decode().startswith('TELL SPAMC/1.5')) and
            ('Set: local, remote' in mock.requests[0].decode()) and
            ('Message-class: spam' in mock.requests[0].decode()) and
            ('Content-length: {}'.format(len(GTUBE.encode())) in mock.requests[0].decode()) and
            (mock.requests[0].decode().endswith(GTUBE)))

@pytest.mark.asyncio
async def test_tell_compress_header_request(event_loop, unused_tcp_port):
    mock = MockServer(b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, compress=True, loop=event_loop)
    response = await client.tell(MessageClassOption.spam,
                                 GTUBE,
                                 SetOption(local=True, remote=True))

    assert b'Compress:' in mock.requests[0]

@pytest.mark.asyncio
async def test_tell_user_header_request(event_loop, unused_tcp_port):
    mock = MockServer(b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, user='TestUser', loop=event_loop)
    response = await client.tell(MessageClassOption.spam,
                                 GTUBE,
                                 SetOption(local=True, remote=True))

    assert b'User: TestUser' in mock.requests[0]
