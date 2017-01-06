#!/usr/bin/env python3

import asyncio

import pytest

from servers import *

from aiospamc import Client
from aiospamc.exceptions import BadResponse, SPAMDConnectionRefused
from aiospamc.options import Action, MessageClassOption
from aiospamc.responses import SPAMDResponse


@pytest.mark.asyncio
async def test_tell_connection_refused(event_loop, unused_tcp_port):
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    with pytest.raises(SPAMDConnectionRefused):
        response = await client.tell(MessageClassOption.spam,
                                     GTUBE,
                                     set_action=Action(local=True, remote=True),
                                     remove_action=Action(local=False, remote=False))

@pytest.mark.asyncio
async def test_tell_valid_response(event_loop, unused_tcp_port):
    server = await valid_response(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    response = await client.tell(MessageClassOption.spam,
                                 GTUBE,
                                 set_action=Action(local=True, remote=True),
                                 remove_action=Action(local=False, remote=False))

    assert isinstance(response, SPAMDResponse)

@pytest.mark.asyncio
async def test_tell_invalid_response(event_loop, unused_tcp_port):
    server = await invalid_response(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    with pytest.raises(BadResponse):
        response = await client.tell(MessageClassOption.spam,
                                     GTUBE,
                                     set_action=Action(local=True, remote=True),
                                     remove_action=Action(local=False, remote=False))

@pytest.mark.asyncio
async def test_tell_valid_request(event_loop, unused_tcp_port):
    server = await valid_response(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    response = await client.tell(MessageClassOption.spam,
                                 GTUBE,
                                 set_action=Action(local=True, remote=True),
                                 remove_action=Action(local=False, remote=False))

    test_response = ('TELL SPAMC/1.5\r\n'
                     'Set: local, remote\r\n'
                     'Content-length: {}\r\n'
                     'Message-class: spam\r\n\r\n'
                     '{}')
    assert server.request.decode() == test_response.format(len(GTUBE.encode()), GTUBE)

@pytest.mark.asyncio
async def test_tell_compress_header_request(event_loop, unused_tcp_port):
    server = await valid_response(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, compress=True, loop=event_loop)
    response = await client.tell(MessageClassOption.spam,
                                 GTUBE,
                                 set_action=Action(local=True, remote=True),
                                 remove_action=Action(local=False, remote=False))

    assert b'Compress:' in server.request

@pytest.mark.asyncio
async def test_tell_user_header_request(event_loop, unused_tcp_port):
    server = await valid_response(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, user='TestUser', loop=event_loop)
    response = await client.tell(MessageClassOption.spam,
                                 GTUBE,
                                 set_action=Action(local=True, remote=True),
                                 remove_action=Action(local=False, remote=False))

    assert b'User: TestUser' in server.request
