#!/usr/bin/env python3

import pytest
from asynctest import patch

from aiospamc import Client
from aiospamc.exceptions import BadResponse, AIOSpamcConnectionFailed
from aiospamc.options import ActionOption, MessageClassOption
from aiospamc.responses import Response
from aiospamc.requests import Request


@pytest.mark.asyncio
@pytest.mark.usefixtures('connection_refused')
async def test_tell_connection_refused(spam):
    client = Client(host='localhost')
    with pytest.raises(AIOSpamcConnectionFailed):
        response = await client.tell(MessageClassOption.spam,
                                     spam,
                                     ActionOption(local=True, remote=True))


@pytest.mark.asyncio
async def test_tell_valid_response(mock_connection, spam):
    client = Client(host='localhost')
    response = await client.tell(MessageClassOption.spam,
                                 spam,
                                 ActionOption(local=True, remote=True))

    assert isinstance(response, Response)


@pytest.mark.asyncio
@pytest.mark.parametrize('set_,remove,message_class', [
    (None,                                  None,                                   MessageClassOption.spam),
    (None,                                  ActionOption(local=True, remote=True),  MessageClassOption.spam),
    (ActionOption(local=True, remote=True), None,                                   MessageClassOption.spam),
    (ActionOption(local=True, remote=True), ActionOption(local=True, remote=True),  MessageClassOption.spam),

    (None,                                  None,                                   MessageClassOption.ham),
    (None,                                  ActionOption(local=True, remote=True),  MessageClassOption.ham),
    (ActionOption(local=True, remote=True), None,                                   MessageClassOption.ham),
    (ActionOption(local=True, remote=True), ActionOption(local=True, remote=True),  MessageClassOption.ham),
])
@patch('aiospamc.client.Client.send')
async def test_tell_valid_request(mock_connection,
                                  set_,
                                  remove,
                                  message_class,
                                  spam):
    client = Client(host='localhost')

    response = await client.tell(message_class,
                                 spam,
                                 set_,
                                 remove)

    request = client.send.call_args[0][0]

    assert isinstance(request, Request)
    assert request.verb == 'TELL'
    assert request.body
    assert request.get_header('Message-class').value == message_class
    if set_:
        assert request.get_header('Set').action is set_
    if remove:
        assert request.get_header('Remove').action is remove


@pytest.mark.asyncio
async def test_tell_invalid_response(mock_connection, response_invalid, spam):
    mock_connection.side_effect = [response_invalid]

    client = Client(host='localhost')
    with pytest.raises(BadResponse):
        response = await client.tell(MessageClassOption.spam,
                                     spam,
                                     ActionOption(local=True, remote=True))
