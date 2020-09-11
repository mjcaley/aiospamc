#!/usr/bin/env python3

import pytest

import aiospamc
from aiospamc.client import Client


@pytest.fixture
def mock_request(mocker):
    client_cls = mocker.patch('aiospamc.Client', autospec=True)
    yield client_cls


@pytest.fixture
def mock_request(mocker):
    yield mocker.patch("aiospamc.request")


@pytest.mark.asyncio
async def test_check_default_args_passed(mock_request, spam):
    await aiospamc.check(spam)

    assert 'CHECK' == mock_request.call_args.args[0]
    assert 'localhost' == mock_request.call_args.kwargs['host']
    assert 783 == mock_request.call_args.kwargs['port']
    assert None == mock_request.call_kwargs['socket_path']
    assert None == mock_request.await_kwargs['timeout']
    assert None == mock_request.call_kwargs['verify']
    assert None == mock_request.call_kwargs['user']
    assert None == mock_request.call_kwargs['compress']
    assert None == mock_request.call_kwargs['headers']


@pytest.mark.asyncio
async def test_check(mock_request, spam):
    result = await aiospamc.check(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_headers_default_args_passed(mock_request, spam):
    await aiospamc.headers(spam)

    assert 'HEADERS' == mock_request.call_args.args[0]
    assert 'localhost' == mock_request.call_args.kwargs['host']
    assert 783 == mock_request.call_args.kwargs['port']


@pytest.mark.asyncio
async def test_headers(mock_request, spam):
    result = await aiospamc.headers(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_ping_default_args_passed(mocker, mock_request):
    await aiospamc.ping()

    assert 'PING' == mock_request.call_args.args[0]
    assert 'localhost' == mock_request.call_args.kwargs['host']
    assert 783 == mock_request.call_args.kwargs['port']


@pytest.mark.asyncio
async def test_ping(mock_request):
    result = await aiospamc.ping()

    assert result is mock_request.return_value


@pytest.mark.asyncio
async def test_process_default_args_passed(mock_request, spam):
    await aiospamc.process(spam)

    assert 'PROCESS' == mock_request.call_args.args[0]
    assert 'localhost' == mock_request.call_args.kwargs['host']
    assert 783 == mock_request.call_args.kwargs['port']


@pytest.mark.asyncio
async def test_process(mock_request, spam):
    result = await aiospamc.process(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_report_default_args_passed(mock_request, spam):
    await aiospamc.report(spam)

    assert 'REPORT' == mock_request.call_args.args[0]
    assert 'localhost' == mock_request.call_args.kwargs['host']
    assert 783 == mock_request.call_args.kwargs['port']


@pytest.mark.asyncio
async def test_report(mock_request, spam):
    result = await aiospamc.report(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_report_if_spam_default_args_passed(mock_request, spam):
    await aiospamc.report_if_spam(spam)

    assert 'REPORT_IFSPAM' == mock_request.call_args.args[0]
    assert 'localhost' == mock_request.call_args.kwargs['host']
    assert 783 == mock_request.call_args.kwargs['port']


@pytest.mark.asyncio
async def test_report_if_spam(mock_request, spam):
    result = await aiospamc.report_if_spam(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_symbols_default_args_passed(mock_request, spam):
    await aiospamc.symbols(spam)

    assert 'SYMBOLS' == mock_request.call_args.args[0]
    assert 'localhost' == mock_request.call_args.kwargs['host']
    assert 783 == mock_request.call_args.kwargs['port']


@pytest.mark.asyncio
async def test_symbols(mock_request, spam):
    result = await aiospamc.symbols(spam)

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]


@pytest.mark.asyncio
async def test_tell_default_args_passed(mocker, mock_request, spam):
    await aiospamc.tell(
        spam,
        message_class=mocker.Mock(),
        set_action=mocker.Mock(),
        remove_action=mocker.Mock())

    assert 'TELL' == mock_request.call_args.args[0]
    assert 'localhost' == mock_request.call_args.kwargs['host']
    assert 783 == mock_request.call_args.kwargs['port']


@pytest.mark.asyncio
@pytest.mark.parametrize('message_class,remove_action,set_action', [
    ['ham', 'local,remote', 'local,remote'],
    ['spam', 'local,remote', 'local,remote'],
    [aiospamc.MessageClassOption.ham, 'local,remote', 'local,remote'],
    [aiospamc.MessageClassOption.spam, 'local,remote', 'local,remote'],
    ['spam', aiospamc.ActionOption(local=True, remote=False), 'local,remote'],
    ['spam', 'local,remote', aiospamc.ActionOption(local=True, remote=False)],
])
async def test_tell(mock_request, spam, message_class, remove_action, set_action):
    result = await aiospamc.tell(
        spam,
        message_class=message_class,
        remove_action=remove_action,
        set_action=set_action
    )

    assert result is mock_request.return_value
    assert spam == mock_request.await_args.args[1]
    assert message_class == mock_request.await_args.kwargs['headers']['Message-class']
    assert remove_action == mock_request.await_args.kwargs['headers']['Remove']
    assert set_action == mock_request.await_args.kwargs['headers']['Set']
