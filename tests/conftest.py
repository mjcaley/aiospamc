#!/usr/bin/env python3

import datetime
from functools import partial
from pathlib import Path
from shutil import which
from subprocess import DEVNULL, TimeoutExpired, Popen
import sys

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509

import pytest

from aiospamc.header_values import ContentLengthValue
from aiospamc.requests import Request


def pytest_addoption(parser):
    parser.addoption("--spamd-process-timeout", action="store", default=10, type=int)


@pytest.fixture
def x_headers():
    from aiospamc.header_values import GenericHeaderValue

    return {"A": GenericHeaderValue(value="a"), "B": GenericHeaderValue(value="b")}


@pytest.fixture
def spam():
    """Example spam message using SpamAssassin's GTUBE message."""

    return (
        b"Subject: Test spam mail (GTUBE)\n"
        b"Message-ID: <GTUBE1.1010101@example.net>\n"
        b"Date: Wed, 23 Jul 2003 23:30:00 +0200\n"
        b"From: Sender <sender@example.net>\n"
        b"To: Recipient <recipient@example.net>\n"
        b"Precedence: junk\n"
        b"MIME-Version: 1.0\n"
        b"Content-Type: text/plain; charset=us-ascii\n"
        b"Content-Transfer-Encoding: 7bit\n\n"
        b"This is the GTUBE, the\n"
        b"\tGeneric\n"
        b"\tTest for\n"
        b"\tUnsolicited\n"
        b"\tBulk\n"
        b"\tEmail\n\n"
        b"If your spam filter supports it, the GTUBE provides a test by which you\n"
        b"can verify that the filter is installed correctly and is detecting incoming\n"
        b"spam. You can send yourself a test mail containing the following string of\n"
        b"characters (in upper case and with no white spaces and line breaks):\n\n"
        b"XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X\n\n"
        b"You should send this test mail from an account outside of your network.\n\n"
    )


@pytest.fixture
def request_with_body():
    body = b"Test body\n"
    return Request(
        verb="CHECK",
        version="1.5",
        headers={"Content-length": ContentLengthValue(len(body))},
        body=body,
    )


@pytest.fixture
def request_ping():
    """PING request."""
    return Request(verb="PING")


@pytest.fixture
def response_empty():
    """Empty response."""
    return b""


@pytest.fixture
def response_ok():
    """OK response in bytes."""
    return b"SPAMD/1.5 0 EX_OK\r\n\r\n"


@pytest.fixture
def response_pong():
    """PONG response in bytes."""
    return b"SPAMD/1.5 0 PONG\r\n"


@pytest.fixture
def response_tell():
    """Examplte TELL response."""
    return b"SPAMD/1.1 0 EX_OK\r\n\r\n\r\n"


@pytest.fixture
def response_spam_header():
    """Response with Spam header in bytes."""
    return b"SPAMD/1.1 0 EX_OK\r\nSpam: True ; 1000.0 / 1.0\r\n\r\n"


@pytest.fixture
def response_with_body():
    """Response with body and Content-length header in bytes."""
    return b"SPAMD/1.5 0 EX_OK\r\nContent-length: 10\r\n\r\nTest body\n"


@pytest.fixture
def response_empty_body():
    """Response with Content-length header, but empty body in bytes."""
    return b"SPAMD/1.5 0 EX_OK\r\nContent-length: 0\r\n\r\n"


@pytest.fixture
def response_invalid():
    """Invalid response in bytes."""
    return b"Invalid response"


# Response exceptions
@pytest.fixture
def ex_usage():
    """Command line usage error."""
    return b"SPAMD/1.5 64 EX_USAGE\r\n\r\n"


@pytest.fixture
def ex_data_err():
    """Data format error."""
    return b"SPAMD/1.5 65 EX_DATAERR\r\n\r\n"


@pytest.fixture
def ex_no_input():
    """No input response in bytes."""
    return b"SPAMD/1.5 66 EX_NOINPUT\r\n\r\n"


@pytest.fixture
def ex_no_user():
    """No user response in bytes."""
    return b"SPAMD/1.5 67 EX_NOUSER\r\n\r\n"


@pytest.fixture
def ex_no_host():
    """No host response in bytes."""
    return b"SPAMD/1.5 68 EX_NOHOST\r\n\r\n"


@pytest.fixture
def ex_unavailable():
    """Unavailable response in bytes."""
    return b"SPAMD/1.5 69 EX_UNAVAILABLE\r\n\r\n"


@pytest.fixture
def ex_software():
    """Software exception response in bytes."""
    return b"SPAMD/1.5 70 EX_SOFTWARE\r\n\r\n"


@pytest.fixture
def ex_os_err():
    """Operating system error response in bytes."""
    return b"SPAMD/1.5 71 EX_OSERR\r\n\r\n"


@pytest.fixture
def ex_os_file():
    """Operating system file error in bytes."""
    return b"SPAMD/1.5 72 EX_OSFILE\r\n\r\n"


@pytest.fixture
def ex_cant_create():
    """Can't create response error in bytes."""
    return b"SPAMD/1.5 73 EX_CANTCREAT\r\n\r\n"


@pytest.fixture
def ex_io_err():
    """Input/output error response in bytes."""
    return b"SPAMD/1.5 74 EX_IOERR\r\n\r\n"


@pytest.fixture
def ex_temp_fail():
    """Temporary failure error response in bytes."""
    return b"SPAMD/1.5 75 EX_TEMPFAIL\r\n\r\n"


@pytest.fixture
def ex_protocol():
    """Protocol error response in bytes."""
    return b"SPAMD/1.5 76 EX_PROTOCOL\r\n\r\n"


@pytest.fixture
def ex_no_perm():
    """No permission error response in bytes."""
    return b"SPAMD/1.5 77 EX_NOPERM\r\n\r\n"


@pytest.fixture
def ex_config():
    """Configuration error response in bytes."""
    return b"SPAMD/1.5 78 EX_CONFIG\r\n\r\n"


@pytest.fixture
def ex_timeout():
    """Timeout error response in bytes."""
    return b"SPAMD/1.5 79 EX_TIMEOUT\r\n\r\n"


@pytest.fixture
def ex_undefined():
    """Undefined exception in bytes."""
    return b"SPAMD/1.5 999 EX_UNDEFINED\r\n\r\n"


# Integration fixtures


@pytest.fixture(scope="session")
def certificate(tmp_path_factory):
    certs_path = tmp_path_factory.mktemp("localhost_certs")
    key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "CA"),
            x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "Ontario"),
            x509.NameAttribute(x509.NameOID.LOCALITY_NAME, "Toronto"),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "mjcaley"),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, "aiospamc"),
        ]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=7))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False
        )
        .sign(key, hashes.SHA256())
    )

    key_path = certs_path / "localhost.key"
    with open(str(key_path), "wb") as key_file:
        key_file.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    cert_path = certs_path / "localhost.cert"
    with open(str(cert_path), "wb") as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))

    yield key_path, cert_path


@pytest.fixture(scope="session")
def spamd_tcp_options():
    port = 1783

    return {"host": "localhost", "port": port}


@pytest.fixture(scope="session")
def spamd_ssl_options(certificate):
    port = 11783

    return {
        "host": "localhost",
        "port": port,
        "key": str(certificate[0]),
        "cert": str(certificate[1]),
    }


@pytest.fixture(scope="session")
def spamd_unix_options(tmp_path_factory):
    path = tmp_path_factory.mktemp("sockets") / "spamd.sock"

    if sys.platform == "win32":
        return None
    else:
        return {"socket": str(path)}


@pytest.fixture(scope="session")
def spamd(
    spamd_tcp_options, spamd_ssl_options, spamd_unix_options, tmp_path_factory, request
):
    spamd_path = str(Path(which("spamd")).parent)
    spamd_start = "info: spamd: server started on"
    log_file = tmp_path_factory.mktemp("spamd") / "spamd.log"

    options = [
        f"--syslog={str(log_file)}",
        "--local",
        "--allow-tell",
        f'--listen={spamd_tcp_options["host"]}:{spamd_tcp_options["port"]}',
        f'--listen=ssl:{spamd_ssl_options["host"]}:{spamd_ssl_options["port"]}',
        "--server-key",
        f'{spamd_ssl_options["key"]}',
        "--server-cert",
        f'{spamd_ssl_options["cert"]}',
    ]
    if spamd_unix_options:
        options += [f'--socketpath={spamd_unix_options["socket"]}']

    process = Popen(
        ["spamd", *options],
        cwd=spamd_path,
        stdout=DEVNULL,
        stderr=DEVNULL,
        universal_newlines=True,
    )

    def terminate(process):
        process.terminate()
        try:
            process.wait(timeout=5)
        except TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

    request.addfinalizer(partial(terminate, process))

    timeout = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=request.config.getoption("--spamd-process-timeout")
    )
    while not log_file.exists():
        if datetime.datetime.utcnow() > timeout:
            raise TimeoutError

    running = False
    with open(str(log_file), "r") as log:
        while not running:
            if datetime.datetime.utcnow() > timeout:
                raise TimeoutError

            log.seek(0)
            for line in log:
                if spamd_start in line:
                    running = True
                    break

    if running:
        yield {
            "tcp": spamd_tcp_options,
            "ssl": spamd_ssl_options,
            "unix": spamd_unix_options,
        }
    else:
        raise ChildProcessError
