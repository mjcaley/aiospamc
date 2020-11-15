#!/usr/bin/env python3

import sys

import pytest

import aiospamc


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_check(spamd, spam):
    result = await aiospamc.check(spam, socket_path=spamd["unix"]["socket"])

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_headers(spamd, spam):
    result = await aiospamc.headers(spam, socket_path=spamd["unix"]["socket"])

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_ping(spamd):
    result = await aiospamc.ping(socket_path=spamd["unix"]["socket"])

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_process(spamd, spam):
    result = await aiospamc.process(spam, socket_path=spamd["unix"]["socket"])

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_report(spamd, spam):
    result = await aiospamc.report(spam, socket_path=spamd["unix"]["socket"])

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_report_if_spam(spamd, spam):
    result = await aiospamc.report_if_spam(spam, socket_path=spamd["unix"]["socket"])

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_symbols(spamd, spam):
    result = await aiospamc.symbols(spam, socket_path=spamd["unix"]["socket"])

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_tell(spamd, spam):
    result = await aiospamc.tell(message=spam, message_class="spam", socket_path=spamd["unix"]["socket"])

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_without_newline(spamd):
    result = await aiospamc.check(message=b"acb", socket_path=spamd["unix"]["socket"])

    assert 0 == result.status_code
