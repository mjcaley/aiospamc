#!/usr/bin/env python3

import pytest

from aiospamc import Client
from aiospamc.options import MessageClassOption


@pytest.mark.integration
@pytest.mark.asyncio
async def test_check(spamd_unix, spam):
    c = Client(socket_path=spamd_unix)
    result = await c.check(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_headers(spamd_unix, spam):
    c = Client(socket_path=spamd_unix)
    result = await c.headers(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ping(spamd_unix):
    c = Client(socket_path=spamd_unix)
    result = await c.ping()

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process(spamd_unix, spam):
    c = Client(socket_path=spamd_unix)
    result = await c.process(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_report(spamd_unix, spam):
    c = Client(socket_path=spamd_unix)
    result = await c.report(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_report_if_spam(spamd_unix, spam):
    c = Client(socket_path=spamd_unix)
    result = await c.report_if_spam(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_symbols(spamd_unix, spam):
    c = Client(socket_path=spamd_unix)
    result = await c.symbols(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tell(spamd_unix, spam):
    c = Client(socket_path=spamd_unix)
    result = await c.tell(message_class=MessageClassOption.spam, message=spam)

    assert result
