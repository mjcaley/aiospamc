import pytest

import aiospamc


@pytest.mark.integration
async def test_check(spamd_tcp, spam):
    result = await aiospamc.check(spam, host=spamd_tcp[0], port=spamd_tcp[1])

    assert 0 == result.status_code


@pytest.mark.integration
async def test_headers(spamd_tcp, spam):
    result = await aiospamc.headers(spam, host=spamd_tcp[0], port=spamd_tcp[1])

    assert 0 == result.status_code


@pytest.mark.integration
async def test_ping(spamd_tcp):
    result = await aiospamc.ping(host=spamd_tcp[0], port=spamd_tcp[1])

    assert 0 == result.status_code


@pytest.mark.integration
async def test_process(spamd_tcp, spam):
    result = await aiospamc.process(spam, host=spamd_tcp[0], port=spamd_tcp[1])

    assert 0 == result.status_code


@pytest.mark.integration
async def test_report(spamd_tcp, spam):
    result = await aiospamc.report(spam, host=spamd_tcp[0], port=spamd_tcp[1])

    assert 0 == result.status_code


@pytest.mark.integration
async def test_report_if_spam(spamd_tcp, spam):
    result = await aiospamc.report_if_spam(spam, host=spamd_tcp[0], port=spamd_tcp[1])

    assert 0 == result.status_code


@pytest.mark.integration
async def test_symbols(spamd_tcp, spam):
    result = await aiospamc.symbols(spam, host=spamd_tcp[0], port=spamd_tcp[1])

    assert 0 == result.status_code


@pytest.mark.integration
async def test_tell(spamd_tcp, spam):
    result = await aiospamc.tell(
        message=spam,
        message_class="spam",
        host=spamd_tcp[0],
        port=spamd_tcp[1],
    )

    assert 0 == result.status_code
