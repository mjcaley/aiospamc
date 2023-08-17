from shutil import which
from subprocess import Popen, PIPE

import aiospamc

import pytest


def check_spamd_version():
    import re

    process = Popen([which("spamd"), "--version"], stdout=PIPE)
    process.wait()
    version = re.match(rb".*?(\d+)\.\d+\.\d+\n", process.stdout.read())
    return [int(i) for i in version.groups()]


pytestmark = pytest.mark.skipif(check_spamd_version()[0] < 4, reason="SpamAssassin 4+ supports client certificate authentication")


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
