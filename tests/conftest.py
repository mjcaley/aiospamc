import datetime
import sys
from pathlib import Path
from shutil import which
from socket import gethostbyname
from subprocess import PIPE, STDOUT, Popen, TimeoutExpired

import pytest
import trustme
from pytest_mock import MockerFixture

from aiospamc.client import Client, Client2
from aiospamc.connections import ConnectionManager
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
def response_not_spam():
    """Response with Spam header, but it's ham."""
    return b"SPAMD/1.1 0 EX_OK\r\nSpam: False ; 0.0 / 1.0\r\n\r\n"


@pytest.fixture
def response_with_body():
    """Response with body and Content-length header in bytes."""
    return b"SPAMD/1.5 0 EX_OK\r\nContent-length: 10\r\n\r\nTest body\n"


@pytest.fixture
def response_empty_body():
    """Response with Content-length header, but empty body in bytes."""
    return b"SPAMD/1.5 0 EX_OK\r\nContent-length: 0\r\n\r\n"


@pytest.fixture
def response_learned():
    """Response with DidSet set to local."""
    return b"SPAMD/1.1 0 EX_OK\r\nDidSet: local\r\n\r\n"


@pytest.fixture
def response_forgotten():
    """Response with DidRemove set to local."""
    return b"SPAMD/1.1 0 EX_OK\r\nDidRemove: local\r\n\r\n"


@pytest.fixture
def response_reported():
    """Response with DidSet set to remote."""
    return b"SPAMD/1.1 0 EX_OK\r\nDidSet: remote\r\n\r\n"


@pytest.fixture
def response_revoked():
    """Response with DidRemove set to remote."""
    return b"SPAMD/1.1 0 EX_OK\r\nDidRemove: remote\r\n\r\n"


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
def mock_client(mocker: MockerFixture, response_ok):
    connection_factory = mocker.Mock()
    connection_factory.return_value.request = mocker.AsyncMock(return_value=response_ok)

    mock_connection_factory = mocker.patch.object(
        Client, "default_connection_factory", connection_factory
    )

    mock_connection_manager = mocker.patch.object(
        ConnectionManager, "request", mocker.AsyncMock(return_value=response_ok)
    )

    yield mock_connection_factory


@pytest.fixture
def mock_client_response(mock_client):
    def inner(response):
        mock_client.return_value.request.return_value = response
        return mock_client

    return inner


@pytest.fixture
def mock_client_raises(mock_client):
    def inner(side_effect):
        mock_client.return_value.request.side_effect = side_effect
        return mock_client

    return inner


# Integration fixtures


@pytest.fixture(scope="session")
def ca():
    yield trustme.CA()


@pytest.fixture(scope="session")
def ca_cert(ca, tmp_path_factory: pytest.TempdirFactory):
    tmp_path = tmp_path_factory.mktemp("ca_certs")
    cert_file = tmp_path / "ca_cert.pem"
    ca.cert_pem.write_to_path(cert_file)

    yield cert_file


@pytest.fixture(scope="session")
def server_cert_and_key(
    ca, hostname, ip_address, tmp_path_factory: pytest.TempdirFactory
):
    tmp_path = tmp_path_factory.mktemp("server_certs")
    cert_file = tmp_path / "server.cert"
    key_file = tmp_path / "server.key"

    cert: trustme.LeafCert = ca.issue_cert(hostname, ip_address)

    cert_file.write_bytes(b"".join([blob.bytes() for blob in cert.cert_chain_pems]))
    cert.private_key_pem.write_to_path(key_file)

    yield cert_file, key_file


@pytest.fixture(scope="session")
def client_cert_and_key(
    ca, hostname, ip_address, tmp_path_factory: pytest.TempdirFactory
):
    tmp_path = tmp_path_factory.mktemp("client_certs")
    cert_file = tmp_path / "client.cert"
    key_file = tmp_path / "client.key"

    cert: trustme.LeafCert = ca.issue_cert(hostname, ip_address)

    cert_file.write_bytes(b"".join([blob.bytes() for blob in cert.cert_chain_pems]))
    cert.private_key_pem.write_to_path(key_file)

    yield cert_file, key_file


@pytest.fixture(scope="session")
def server_cert(server_cert_and_key):
    yield server_cert_and_key[0]


@pytest.fixture(scope="session")
def server_key(server_cert_and_key):
    yield server_cert_and_key[1]


@pytest.fixture(scope="session")
def client_cert(client_cert_and_key):
    yield client_cert_and_key[0]


@pytest.fixture(scope="session")
def client_key(client_cert_and_key):
    yield client_cert_and_key[1]


@pytest.fixture(scope="session")
def spamd(
    ip_address, tcp_port, ssl_port, unix_socket, server_cert, server_key, request
):
    # Configure options
    options = [
        "--local",
        "--allow-tell",
        f"--listen={ip_address}:{tcp_port}",
        f"--listen=ssl:{ip_address}:{ssl_port}",
        "--server-key",
        f"{server_key}",
        "--server-cert",
        f"{server_cert}",
    ]
    if sys.platform != "win32":
        options += [f"--socketpath={unix_socket}"]

    # Spawn spamd
    spamd_exe = Path(which("spamd"))
    process = Popen(
        [spamd_exe, *options],
        stdout=PIPE,
        stderr=STDOUT,
        cwd=spamd_exe.parent,
        universal_newlines=True,
    )

    # Check the log to see if spamd is running
    timeout = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=request.config.getoption("--spamd-process-timeout")
    )

    running = False
    spamd_start = "info: spamd: server started on"
    while not running:
        if datetime.datetime.utcnow() > timeout:
            raise TimeoutError

        for line in process.stdout:
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
