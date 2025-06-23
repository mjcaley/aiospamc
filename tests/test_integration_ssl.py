import aiospamc
import pytest


@pytest.mark.integration
async def test_verify_false(spamd_ssl):
    result = await aiospamc.ping(host=spamd_ssl[0], port=spamd_ssl[1], verify=False)

    assert 0 == result.status_code


@pytest.mark.integration
async def test_check(spamd_ssl, ca_cert_path, spam):
    result = await aiospamc.check(
        spam, host=spamd_ssl[0], port=spamd_ssl[1], verify=ca_cert_path
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_headers(spamd_ssl, ca_cert_path, spam):
    result = await aiospamc.headers(
        spam, host=spamd_ssl[0], port=spamd_ssl[1], verify=ca_cert_path
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_ping(spamd_ssl, ca_cert_path):
    result = await aiospamc.ping(
        host=spamd_ssl[0],
        port=spamd_ssl[1],
        verify=ca_cert_path,
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_process(spamd_ssl, ca_cert_path, spam):
    result = await aiospamc.process(
        spam, host=spamd_ssl[0], port=spamd_ssl[1], verify=ca_cert_path
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_report(spamd_ssl, ca_cert_path, spam):
    result = await aiospamc.report(
        spam, host=spamd_ssl[0], port=spamd_ssl[1], verify=ca_cert_path
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_report_if_spam(spamd_ssl, ca_cert_path, spam):
    result = await aiospamc.report_if_spam(
        spam, host=spamd_ssl[0], port=spamd_ssl[1], verify=ca_cert_path
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_symbols(spamd_ssl, ca_cert_path, spam):
    result = await aiospamc.symbols(
        spam, host=spamd_ssl[0], port=spamd_ssl[1], verify=ca_cert_path
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_tell(spamd_ssl, ca_cert_path, spam):
    result = await aiospamc.tell(
        message=spam,
        message_class="spam",
        host=spamd_ssl[0],
        port=spamd_ssl[1],
        verify=ca_cert_path,
    )

    assert 0 == result.status_code
