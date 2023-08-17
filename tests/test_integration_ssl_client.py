from shutil import which
from subprocess import PIPE, Popen

import pytest

import aiospamc


def spamd_lt_4():
    import re

    spamd_exe = which("spamd")
    if not spamd_exe:
        return True

    process = Popen([spamd_exe, "--version"], stdout=PIPE)
    process.wait()
    version = re.match(rb".*?(\d+)\.\d+\.\d+\n", process.stdout.read())
    parsed = [int(i) for i in version.groups()]

    return parsed[0] < 4


pytestmark = pytest.mark.skipif(
    spamd_lt_4(),
    reason="Only SpamAssassin 4+ supports client certificate authentication",
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
