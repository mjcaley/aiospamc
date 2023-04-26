#!/usr/bin/env python3

import datetime
import sys
from pathlib import Path
from shutil import which
from socket import gethostbyname
from subprocess import DEVNULL, Popen, TimeoutExpired

import pytest
import trustme

from aiospamc.client import Client
from aiospamc.header_values import ContentLengthValue
from aiospamc.incremental_parser import ResponseParser
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
def response_timeout():
    """Server timeout response."""
    return b"SPAMD/1.0 79 Timeout: (30 second timeout while trying to CHECK)\r\n"


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


@pytest.fixture(scope="session")
def hostname():
    return "localhost"


@pytest.fixture(scope="session")
def ip_address(hostname):
    return gethostbyname(hostname)


@pytest.fixture(scope="session")
def tcp_port():
    return 1783


@pytest.fixture(scope="session")
def ssl_port():
    return 11783


@pytest.fixture(scope="session")
def unix_socket(tmp_path_factory):
    return str(tmp_path_factory.mktemp("sockets") / "spamd.sock")


@pytest.fixture
def mock_client_dependency(mocker, response_ok):
    ssl_factory = mocker.Mock()
    connection_factory = mocker.Mock()
    connection_factory.return_value.request = mocker.AsyncMock(return_value=response_ok)
    parser_factory = mocker.Mock(return_value=ResponseParser())

    return Client(ssl_factory, connection_factory, parser_factory)


@pytest.fixture
def mock_client_response(mock_client_dependency):
    def inner(response):
        mock_client_dependency.connection_factory.return_value.request.return_value = (
            response
        )

        return mock_client_dependency

    return inner


# Integration fixtures


@pytest.fixture(scope="session")
def create_certificate(tmp_path_factory, hostname, ip_address):
    certs_tmp_path = tmp_path_factory.mktemp("localhost_certs")
    ca_path = certs_tmp_path / "ca.pem"
    cert_path = certs_tmp_path / "cert.pem"

    ca = trustme.CA()
    cert = ca.issue_cert(hostname, ip_address)

    ca.cert_pem.write_to_path(ca_path)
    cert.private_key_and_cert_chain_pem.write_to_path(cert_path)

    yield ca_path, cert_path


@pytest.fixture(scope="session")
def certificate_authority(create_certificate):
    yield create_certificate[0]


@pytest.fixture(scope="session")
def certificate(create_certificate):
    yield create_certificate[1]


@pytest.fixture(scope="session")
def spamd(
    tmp_path_factory, ip_address, tcp_port, ssl_port, unix_socket, certificate, request
):
    # Configure options
    options = [
        # f"--syslog={str(log_file)}",
        "--local",
        "--allow-tell",
        f"--listen={ip_address}:{tcp_port}",
        f"--listen=ssl:{ip_address}:{ssl_port}",
        "--server-key",
        f"{certificate}",
        "--server-cert",
        f"{certificate}",
    ]
    if sys.platform != "win32":
        options += [f"--socketpath={unix_socket}"]
    print(f"options used are: {options}")

    # Setup log file
    spamd_path = str(Path(which("spamd")).parent)
    log_file = tmp_path_factory.mktemp("spamd") / "spamd.log"
    log_file.touch()

    # Spawn spamd
    with open(log_file, "r") as log:
        process = Popen(
            [which("spamd"), *options],
            cwd=spamd_path,
            # stdout=log,
            stderr=DEVNULL,
            universal_newlines=True,
        )

        # Check the log to see if spamd is running
        timeout = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=request.config.getoption("--spamd-process-timeout")
        )
        while not log_file.exists():
            if datetime.datetime.utcnow() > timeout:
                raise TimeoutError

        running = False
        spamd_start = "info: spamd: server started on"
        # with open(str(log_file), "r") as log:
        while not running:
            if datetime.datetime.utcnow() > timeout:
                print(log_file.read_text())
                raise TimeoutError

            log.seek(0)
            for line in log:
                if spamd_start in line:
                    running = True
                    break

        if not running:
            raise ChildProcessError

        yield

        # Stop spamd
        process.terminate()
        try:
            process.wait(timeout=5)
        except TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
