#!/usr/bin/env python3

import pytest

from aiospamc import Client
from aiospamc.options import MessageClassOption


@pytest.mark.integration
@pytest.mark.asyncio
async def test_check(spamd_tcp, spam):
    c = Client(host=spamd_tcp[0], port=spamd_tcp[1])
    result = await c.check(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_headers(spamd_tcp, spam):
    c = Client(host=spamd_tcp[0], port=spamd_tcp[1])
    result = await c.headers(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ping(spamd_tcp):
    c = Client(host=spamd_tcp[0], port=spamd_tcp[1])
    result = await c.ping()

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process(spamd_tcp, spam):
    c = Client(host=spamd_tcp[0], port=spamd_tcp[1])
    result = await c.process(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_report(spamd_tcp, spam):
    c = Client(host=spamd_tcp[0], port=spamd_tcp[1])
    result = await c.report(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_report_if_spam(spamd_tcp, spam):
    c = Client(host=spamd_tcp[0], port=spamd_tcp[1])
    result = await c.report_if_spam(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_symbols(spamd_tcp, spam):
    c = Client(host=spamd_tcp[0], port=spamd_tcp[1])
    result = await c.symbols(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tell(spamd_tcp, spam):
    c = Client(host=spamd_tcp[0], port=spamd_tcp[1])
    result = await c.tell(message_class=MessageClassOption.spam, message=spam)

    assert result
