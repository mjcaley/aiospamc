#!/usr/bin/env python3

import pytest

import aiospamc
from aiospamc.client import Client


@pytest.fixture
def mock_client_cls(mocker):
    client_cls = mocker.patch('aiospamc.Client', autospec=True)
    yield client_cls


@pytest.mark.asyncio
async def test_check_default_args_passed(mocker, mock_client_cls, spam):
    await aiospamc.check(spam)

    assert 'localhost' == mock_client_cls.call_args.kwargs['host']
    assert 783 == mock_client_cls.call_args.kwargs['port']


@pytest.mark.asyncio
async def test_check(mocker, mock_client_cls, spam):
    mocker.spy(aiospamc, 'client')
    result = await aiospamc.check(spam)

    assert result is mock_client_cls.return_value.check.return_value
    assert spam is mock_client_cls.return_value.check.await_args.args[0]


@pytest.mark.asyncio
async def test_headers_default_args_passed(mocker, mock_client_cls, spam):
    await aiospamc.headers(spam)

    assert 'localhost' == mock_client_cls.call_args.kwargs['host']
    assert 783 == mock_client_cls.call_args.kwargs['port']


@pytest.mark.asyncio
async def test_headers(mocker, mock_client_cls, spam):
    mocker.spy(aiospamc, 'headers')
    result = await aiospamc.headers(spam)

    assert result is mock_client_cls.return_value.headers.return_value
    assert spam is mock_client_cls.return_value.headers.await_args.args[0]


@pytest.mark.asyncio
async def test_ping_default_args_passed(mocker, mock_client_cls):
    await aiospamc.ping()

    assert 'localhost' == mock_client_cls.call_args.kwargs['host']
    assert 783 == mock_client_cls.call_args.kwargs['port']


@pytest.mark.asyncio
async def test_ping(mock_client_cls):
    result = await aiospamc.ping()

    assert result is mock_client_cls.return_value.ping.return_value


@pytest.mark.asyncio
async def test_process_default_args_passed(mocker, mock_client_cls, spam):
    await aiospamc.process(spam)

    assert 'localhost' == mock_client_cls.call_args.kwargs['host']
    assert 783 == mock_client_cls.call_args.kwargs['port']


@pytest.mark.asyncio
async def test_process(mocker, mock_client_cls, spam):
    mocker.spy(aiospamc, 'process')
    result = await aiospamc.process(spam)

    assert result is mock_client_cls.return_value.process.return_value
    assert spam is mock_client_cls.return_value.process.await_args.args[0]


@pytest.mark.asyncio
async def test_tell_default_args_passed(mocker, mock_client_cls, spam):
    await aiospamc.tell(
        spam,
        message_class=mocker.Mock(),
        set_action=mocker.Mock(),
        remove_action=mocker.Mock())

    assert 'localhost' == mock_client_cls.call_args.kwargs['host']
    assert 783 == mock_client_cls.call_args.kwargs['port']


@pytest.mark.asyncio
@pytest.mark.parametrize('message_class,remove_action,set_action', [
    ['ham', 'local,remote', 'local,remote'],
    ['spam', 'local,remote', 'local,remote'],
    [aiospamc.MessageClassOption.ham, 'local,remote', 'local,remote'],
    [aiospamc.MessageClassOption.spam, 'local,remote', 'local,remote'],
    ['spam', aiospamc.ActionOption(local=True, remote=False), 'local,remote'],
    ['spam', 'local,remote', aiospamc.ActionOption(local=True, remote=False)],
])
async def test_tell(mocker, mock_client_cls, spam, message_class, remove_action, set_action):
    mock_instance = mock_client_cls.return_value

    result = await aiospamc.tell(
        spam,
        message_class=message_class,
        remove_action=remove_action,
        set_action=set_action
    )

    assert result is mock_instance.tell.return_value
    assert spam == mock_instance.tell.await_args.kwargs['message']
    assert message_class == mock_instance.tell.await_args.kwargs['message_class']
    assert remove_action == mock_instance.tell.await_args.kwargs['remove_action']
    assert set_action == mock_instance.tell.await_args.kwargs['set_action']
