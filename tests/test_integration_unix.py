import sys

import pytest

import aiospamc


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
async def test_check(spamd_unix, spam):
    result = await aiospamc.check(spam, socket_path=spamd_unix)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
async def test_headers(spamd_unix, spam):
    result = await aiospamc.headers(spam, socket_path=spamd_unix)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
async def test_ping(spamd_unix):
    result = await aiospamc.ping(socket_path=spamd_unix)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
async def test_process(spamd_unix, spam):
    result = await aiospamc.process(spam, socket_path=spamd_unix)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
async def test_report(spamd_unix, spam):
    result = await aiospamc.report(spam, socket_path=spamd_unix)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
async def test_report_if_spam(spamd_unix, spam):
    result = await aiospamc.report_if_spam(spam, socket_path=spamd_unix)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
async def test_symbols(spamd_unix, spam):
    result = await aiospamc.symbols(spam, socket_path=spamd_unix)

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
async def test_tell(spamd_unix, spam):
    result = await aiospamc.tell(
        message=spam, message_class="spam", socket_path=spamd_unix
    )

    assert 0 == result.status_code


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix sockets not supported on Windows"
)
@pytest.mark.integration
async def test_message_without_newline(spamd_unix):
    result = await aiospamc.check(message=b"acb", socket_path=spamd_unix)

    assert 0 == result.status_code
