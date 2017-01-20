#!/usr/bin/env python3

import asyncio

import pytest
from fixtures import *

from aiospamc import Client
from aiospamc.exceptions import BadResponse, SPAMDConnectionRefused
from aiospamc.headers import ContentLength, MessageClass, Remove, Set
from aiospamc.options import MessageClassOption, RemoveOption, SetOption
from aiospamc.responses import Response
from aiospamc.requests import Request


@pytest.mark.asyncio
async def test_tell_connection_refused(event_loop, unused_tcp_port, spam):
    client = Client('localhost', unused_tcp_port, loop=event_loop)
    with pytest.raises(SPAMDConnectionRefused):
        response = await client.tell(MessageClassOption.spam,
                                     spam,
                                     SetOption(local=True, remote=True))

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
@pytest.mark.parametrized('test_input,expected', [
    (RemoveOption(local=True, remote=False), 'Remove: local\r\n'),
    (RemoveOption(local=False, remote=True), 'Remove: remote\r\n'),
    (RemoveOption(local=True, remote=True), 'Remove: local, remote\r\n'),
    (SetOption(local=True, remote=False), 'Set: local\r\n'),
    (SetOption(local=False, remote=True), 'Set: remote\r\n'),
    (SetOption(local=True, remote=True), 'Set: local, remote\r\n'),
])
async def test_tell_valid_request(reader, writer, test_input, expected, spam):
    client = Client()
    response = await client.tell(MessageClassOption.spam,
                                 spam,
                                 test_input)

    args = writer.writer.call_args
    assert expected in args[0][0]

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_tell_verb_at_start(reader, writer, spam):
    client = Client()
    response = await client.tell(MessageClassOption.spam,
                                 spam,
                                 SetOption(local=True, remote=True))

    args = writer.write.call_args
    assert args[0][0].startswith(b'TELL')

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
@pytest.mark.parametrize('test_input,expected', [
    (RemoveOption(local=True, remote=False), (b'TELL',
                                              spam().encode(),
                                              bytes(MessageClass(MessageClassOption.spam)),
                                              bytes(Remove(RemoveOption(local=True, remote=False))))),
    (SetOption(local=True, remote=False), (b'TELL',
                                           spam().encode(),
                                           bytes(MessageClass(MessageClassOption.spam)),
                                           bytes(Set(SetOption(local=True, remote=False)))))
])
async def test_tell_request_call(reader, writer, test_input, expected, spam):
    client = Client()
    response = await client.tell(MessageClassOption.spam,
                                 spam,
                                 test_input)

    args = writer.write.call_args

    assert all([phrase in args[0][0] for phrase in expected])

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_tell_valid_response(spam):
    client = Client()
    response = await client.tell(MessageClassOption.spam,
                                 spam,
                                 SetOption(local=True, remote=True))

    assert isinstance(response, Response)

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
@pytest.mark.responses(response_invalid())
async def test_tell_invalid_response(spam):
    client = Client()
    with pytest.raises(BadResponse):
        response = await client.tell(MessageClassOption.spam,
                                     spam,
                                     SetOption(local=True, remote=True))

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_tell_valid_request(reader, writer, spam):
    client = Client()
    response = await client.tell(MessageClassOption.spam,
                                 spam,
                                 SetOption(local=True, remote=True))

    args = writer.write.call_args[0][0].decode()
    # We can't guarantee the order of the headers, so we have to break things up
    assert args.startswith('TELL SPAMC/1.5\r\n')
    assert 'Set: local, remote\r\n' in args
    assert 'Message-class: spam\r\n' in args
    assert 'Content-length: {}\r\n'.format(len(spam.encode())) in args
    assert args.endswith(spam)

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_tell_compress_header_request(reader, writer, spam):
    client = Client(compress=True)
    response = await client.tell(MessageClassOption.spam,
                                 spam,
                                 SetOption(local=True, remote=True))

    args = writer.write.call_args
    assert b'Compress:' in args[0][0]

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
async def test_tell_user_header_request(reader, writer, spam):
    client = Client(user='TestUser')
    response = await client.tell(MessageClassOption.spam,
                                 spam,
                                 SetOption(local=True, remote=True))

    args = writer.write.call_args
    assert b'User: TestUser' in args[0][0]
