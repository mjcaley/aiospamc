#!/usr/bin/env python3

import pytest

import aiospamc


@pytest.mark.integration
@pytest.mark.asyncio
async def test_verify_false(spamd, hostname, ssl_port, certificate_authority):
    result = await aiospamc.ping(
        host=hostname, port=ssl_port, verify=certificate_authority
    )

    assert 0 == result.status_code


@pytest.mark.integration
@pytest.mark.asyncio
async def test_check(spamd, hostname, ssl_port, spam, certificate_authority):
    result = await aiospamc.check(
        spam, host=hostname, port=ssl_port, verify=certificate_authority
    )

    assert 0 == result.status_code


@pytest.mark.integration
@pytest.mark.asyncio
async def test_headers(spamd, hostname, ssl_port, spam, certificate_authority):
    result = await aiospamc.headers(
        spam, host=hostname, port=ssl_port, verify=certificate_authority
    )

    assert 0 == result.status_code


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ping(spamd, hostname, ssl_port, certificate_authority):
    result = await aiospamc.ping(
        host=hostname,
        port=ssl_port,
        verify=certificate_authority,
    )

    assert 0 == result.status_code


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process(spamd, hostname, ssl_port, spam, certificate_authority):
    result = await aiospamc.process(
        spam, host=hostname, port=ssl_port, verify=certificate_authority
    )

    assert 0 == result.status_code


@pytest.mark.integration
@pytest.mark.asyncio
async def test_report(spamd, hostname, ssl_port, spam, certificate_authority):
    result = await aiospamc.report(
        spam, host=hostname, port=ssl_port, verify=certificate_authority
    )

    assert 0 == result.status_code


@pytest.mark.integration
@pytest.mark.asyncio
async def test_report_if_spam(spamd, hostname, ssl_port, spam, certificate_authority):
    result = await aiospamc.report_if_spam(
        spam, host=hostname, port=ssl_port, verify=certificate_authority
    )

    assert 0 == result.status_code


@pytest.mark.integration
@pytest.mark.asyncio
async def test_symbols(spamd, hostname, ssl_port, spam, certificate_authority):
    result = await aiospamc.symbols(
        spam, host=hostname, port=ssl_port, verify=certificate_authority
    )

    assert 0 == result.status_code


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tell(spamd, hostname, ssl_port, spam, certificate_authority):
    result = await aiospamc.tell(
        message=spam,
        message_class="spam",
        host=hostname,
        port=ssl_port,
        verify=certificate_authority,
    )

    assert 0 == result.status_code


@pytest.mark.skip(reason="spamc implementation doesn't support newline either")
@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_without_newline(spamd, hostname, ssl_port, certificate_authority):
    result = await aiospamc.check(
        message=b"acb", host=hostname, port=ssl_port, verify=certificate_authority
    )

    assert 0 == result.status_code
