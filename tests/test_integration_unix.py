#!/usr/bin/env python3

import sys

import pytest

import aiospamc


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_check(spamd, unix_socket, spam):
    result = await aiospamc.check(spam, socket_path=unix_socket)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_headers(spamd, unix_socket, spam):
    result = await aiospamc.headers(spam, socket_path=unix_socket)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_ping(spamd, unix_socket):
    result = await aiospamc.ping(socket_path=unix_socket)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_process(spamd, unix_socket, spam):
    result = await aiospamc.process(spam, socket_path=unix_socket)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_report(spamd, unix_socket, spam):
    result = await aiospamc.report(spam, socket_path=unix_socket)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_report_if_spam(spamd, unix_socket, spam):
    result = await aiospamc.report_if_spam(spam, socket_path=unix_socket)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_symbols(spamd, unix_socket, spam):
    result = await aiospamc.symbols(spam, socket_path=unix_socket)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_tell(spamd, unix_socket, spam):
    result = await aiospamc.tell(
        message=spam, message_class="spam", socket_path=unix_socket
    )

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_without_newline(spamd, unix_socket):
    result = await aiospamc.check(message=b"acb", socket_path=unix_socket)

    assert 0 == result.status_code
