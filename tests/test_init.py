#!/usr/bin/env python3

import pytest
from asynctest import CoroutineMock

import aiospamc
from aiospamc.client import Client


@pytest.mark.asyncio
@pytest.mark.parametrize('method', [
    'check',
    'headers',
    'process',
    'report',
    'report_if_spam',
    'symbols'
])
async def test_frontend_function_with_message(mocker, method, spam):
    mock = mocker.patch.object(Client, method, new=CoroutineMock())
    func = getattr(aiospamc, method)
    result = await func(spam)

    assert result
    assert mock.called
    assert result is mock.return_value


@pytest.mark.asyncio
async def test_ping(mocker):
    mock = mocker.patch.object(Client, 'ping', new=CoroutineMock())
    result = await aiospamc.ping()

    assert result
    assert mock.called
    assert result is mock.return_value


@pytest.mark.asyncio
@pytest.mark.parametrize('message_class,remove_action,set_action', [
    ['ham', 'local,remote', 'local,remote'],
    ['spam', 'local,remote', 'local,remote'],
    [aiospamc.MessageClassOption.ham, 'local,remote', 'local,remote'],
    [aiospamc.MessageClassOption.spam, 'local,remote', 'local,remote'],
    ['spam', aiospamc.ActionOption(local=True, remote=False), 'local,remote'],
    ['spam', 'local,remote', aiospamc.ActionOption(local=True, remote=False)],
])
async def test_tell(mocker, spam, message_class, remove_action, set_action):
    mock = mocker.patch.object(Client, 'tell', new=CoroutineMock())
    result = await aiospamc.tell(
        spam,
        message_class=message_class,
        remove_action=remove_action,
        set_action=set_action
    )

    assert result
    assert mock.called
    assert result is mock.return_value
