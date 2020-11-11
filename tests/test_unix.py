#!/usr/bin/env python3

import pytest

import aiospamc


@pytest.mark.integration
@pytest.mark.asyncio
async def test_check(spamd, spam):
    result = await aiospamc.check(spam, socket_path=spamd['unix']['socket'])

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_headers(spamd, spam):
    result = await aiospamc.headers(spam, socket_path=spamd['unix']['socket'])

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ping(spamd):
    result = await aiospamc.ping(socket_path=spamd['unix']['socket'])

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process(spamd, spam):
    result = await aiospamc.process(spam, socket_path=spamd['unix']['socket'])

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_report(spamd, spam):
    result = await aiospamc.report(spam, socket_path=spamd['unix']['socket'])

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_report_if_spam(spamd, spam):
    result = await aiospamc.report_if_spam(spam, socket_path=spamd['unix']['socket'])

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_symbols(spamd, spam):
    result = await aiospamc.symbols(spam, socket_path=spamd['unix']['socket'])

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tell(spamd, spam):
    result = await aiospamc.tell(message=spam, message_class='spam', socket_path=spamd['unix']['socket'])

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_without_newline(spamd):
    result = await aiospamc.check(message=b'acb', host=spamd['tcp']['host'], port=spamd['tcp']['port'])

    assert result
