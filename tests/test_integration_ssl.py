import pytest

import aiospamc


@pytest.mark.integration
async def test_verify_false(spamd, hostname, ssl_port, ca_cert):
    result = await aiospamc.ping(host=hostname, port=ssl_port, verify=ca_cert)

    assert 0 == result.status_code


@pytest.mark.integration
async def test_check(spamd, hostname, ssl_port, spam, ca_cert):
    result = await aiospamc.check(spam, host=hostname, port=ssl_port, verify=ca_cert)

    assert 0 == result.status_code


@pytest.mark.integration
async def test_headers(spamd, hostname, ssl_port, spam, ca_cert):
    result = await aiospamc.headers(spam, host=hostname, port=ssl_port, verify=ca_cert)

    assert 0 == result.status_code


@pytest.mark.integration
async def test_ping(spamd, hostname, ssl_port, ca_cert):
    result = await aiospamc.ping(
        host=hostname,
        port=ssl_port,
        verify=ca_cert,
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_process(spamd, hostname, ssl_port, spam, ca_cert):
    result = await aiospamc.process(spam, host=hostname, port=ssl_port, verify=ca_cert)

    assert 0 == result.status_code


@pytest.mark.integration
async def test_report(spamd, hostname, ssl_port, spam, ca_cert):
    result = await aiospamc.report(spam, host=hostname, port=ssl_port, verify=ca_cert)

    assert 0 == result.status_code


@pytest.mark.integration
async def test_report_if_spam(spamd, hostname, ssl_port, spam, ca_cert):
    result = await aiospamc.report_if_spam(
        spam, host=hostname, port=ssl_port, verify=ca_cert
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_symbols(spamd, hostname, ssl_port, spam, ca_cert):
    result = await aiospamc.symbols(spam, host=hostname, port=ssl_port, verify=ca_cert)

    assert 0 == result.status_code


@pytest.mark.integration
async def test_tell(spamd, hostname, ssl_port, spam, ca_cert):
    result = await aiospamc.tell(
        message=spam,
        message_class="spam",
        host=hostname,
        port=ssl_port,
        verify=ca_cert,
    )

    assert 0 == result.status_code
