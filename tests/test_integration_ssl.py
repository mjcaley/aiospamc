from pathlib import Path

import pytest

import aiospamc


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


@pytest.mark.integration
async def test_check_client_auth(
    spamd_ssl_client, ca_cert_path, client_cert_path, client_key_path, spam
):
    result = await aiospamc.check(
        spam,
        host=spamd_ssl_client[0],
        port=spamd_ssl_client[1],
        verify=ca_cert_path,
        cert=(client_cert_path, client_key_path),
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_headers_client_auth(
    spamd_ssl_client, ca_cert_path, client_cert_path, client_key_path, spam
):
    result = await aiospamc.headers(
        spam,
        host=spamd_ssl_client[0],
        port=spamd_ssl_client[1],
        verify=ca_cert_path,
        cert=(client_cert_path, client_key_path),
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_ping_client_auth(
    spamd_ssl_client, ca_cert_path, client_cert_path, client_key_path
):
    result = await aiospamc.ping(
        host=spamd_ssl_client[0],
        port=spamd_ssl_client[1],
        verify=ca_cert_path,
        cert=(client_cert_path, client_key_path),
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_process_client_auth(
    spamd_ssl_client, ca_cert_path, client_cert_path, client_key_path, spam
):
    result = await aiospamc.process(
        spam,
        host=spamd_ssl_client[0],
        port=spamd_ssl_client[1],
        verify=ca_cert_path,
        cert=(client_cert_path, client_key_path),
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_report_client_auth(
    spamd_ssl_client, ca_cert_path, client_cert_path, client_key_path, spam
):
    result = await aiospamc.report(
        spam,
        host=spamd_ssl_client[0],
        port=spamd_ssl_client[1],
        verify=ca_cert_path,
        cert=(client_cert_path, client_key_path),
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_report_if_spam_client_auth(
    spamd_ssl_client, ca_cert_path, client_cert_path, client_key_path, spam
):
    result = await aiospamc.report_if_spam(
        spam,
        host=spamd_ssl_client[0],
        port=spamd_ssl_client[1],
        verify=ca_cert_path,
        cert=(client_cert_path, client_key_path),
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_symbols_client_auth(
    spamd_ssl_client, ca_cert_path, client_cert_path, client_key_path, spam
):
    result = await aiospamc.symbols(
        spam,
        host=spamd_ssl_client[0],
        port=spamd_ssl_client[1],
        verify=ca_cert_path,
        cert=(client_cert_path, client_key_path),
    )

    assert 0 == result.status_code


@pytest.mark.integration
async def test_tell_client_auth(
    spamd_ssl_client, ca_cert_path, client_cert_path, client_key_path, spam
):
    result = await aiospamc.tell(
        message=spam,
        message_class="spam",
        host=spamd_ssl_client[0],
        port=spamd_ssl_client[1],
        verify=ca_cert_path,
        cert=(client_cert_path, client_key_path),
    )

    assert 0 == result.status_code
