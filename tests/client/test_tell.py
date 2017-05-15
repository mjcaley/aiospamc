#!/usr/bin/env python3

import pytest
from asynctest import patch

from aiospamc import Client
from aiospamc.exceptions import BadResponse, AIOSpamcConnectionFailed
from aiospamc.headers import ContentLength, MessageClass, Remove, Set
from aiospamc.options import MessageClassOption, RemoveOption, SetOption
from aiospamc.responses import Response
from aiospamc.requests import Request


@pytest.mark.asyncio
@pytest.mark.usefixtures('connection_refused')
async def test_tell_connection_refused(spam):
    client = Client()
    with pytest.raises(AIOSpamcConnectionFailed):
        response = await client.tell(MessageClassOption.spam,
                                     spam,
                                     SetOption(local=True, remote=True))


@pytest.mark.asyncio
@pytest.mark.parametrize('set_remove_name,set_remove,message_class', [
    ('Remove', RemoveOption(local=True, remote=False), MessageClassOption.spam),
    ('Remove', RemoveOption(local=False, remote=True), MessageClassOption.spam),
    ('Remove', RemoveOption(local=True, remote=True), MessageClassOption.spam),
    ('Set', SetOption(local=True, remote=False), MessageClassOption.spam),
    ('Set', SetOption(local=False, remote=True), MessageClassOption.spam),
    ('Set', SetOption(local=True, remote=True), MessageClassOption.spam),

    ('Remove', RemoveOption(local=True, remote=False), MessageClassOption.ham),
    ('Remove', RemoveOption(local=False, remote=True), MessageClassOption.ham),
    ('Remove', RemoveOption(local=True, remote=True), MessageClassOption.ham),
    ('Set', SetOption(local=True, remote=False), MessageClassOption.ham),
    ('Set', SetOption(local=False, remote=True), MessageClassOption.ham),
    ('Set', SetOption(local=True, remote=True), MessageClassOption.ham),
])
@patch('aiospamc.client.Client.send')
async def test_tell_valid_request(mock_connection,
                                  set_remove_name,
                                  set_remove,
                                  message_class,
                                  spam):
    client = Client()

    response = await client.tell(message_class,
                                 spam,
                                 set_remove)

    request = client.send.call_args[0][0]

    assert isinstance(request, Request)
    assert request.verb == 'TELL'
    assert request.body
    assert request.get_header('Message-class').value == message_class
    assert request.get_header(set_remove_name).action.local == set_remove.local
    assert request.get_header(set_remove_name).action.remote == set_remove.remote


@pytest.mark.asyncio
async def test_tell_valid_response(mock_connection, spam):
    client = Client()
    response = await client.tell(MessageClassOption.spam,
                                 spam,
                                 SetOption(local=True, remote=True))

    assert isinstance(response, Response)


@pytest.mark.asyncio
async def test_tell_invalid_response(mock_connection, response_invalid, spam):
    mock_connection.side_effect = [response_invalid]

    client = Client()
    with pytest.raises(BadResponse):
        response = await client.tell(MessageClassOption.spam,
                                     spam,
                                     SetOption(local=True, remote=True))
