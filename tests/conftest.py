import asyncio
import concurrent.futures
import datetime
import ssl
import sys
import threading
from asyncio import StreamReader, StreamWriter
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from socket import gethostbyname
from subprocess import PIPE, STDOUT, Popen, TimeoutExpired

import pytest
import trustme
from cryptography.hazmat.primitives.serialization import (
    BestAvailableEncryption,
    Encoding,
    PrivateFormat,
    load_pem_private_key,
)
from pytest_mock import MockerFixture

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


@pytest.fixture(scope="session")
def ca():
    yield trustme.CA()


@pytest.fixture(scope="session")
def server_cert(ca, hostname, ip_address):
    yield ca.issue_cert(hostname, ip_address)


@pytest.fixture(scope="session")
def ca_cert_path(ca, tmp_path_factory: pytest.TempdirFactory):
    tmp_path = tmp_path_factory.mktemp("ca_certs")
    cert_file = tmp_path / "ca_cert.pem"
    ca.cert_pem.write_to_path(cert_file)

    yield cert_file


@pytest.fixture(scope="session")
def server_cert_and_key(server_cert, tmp_path_factory: pytest.TempdirFactory):
    tmp_path = tmp_path_factory.mktemp("server_certs")
    cert_file = tmp_path / "server.cert"
    key_file = tmp_path / "server.key"

    cert_file.write_bytes(
        b"".join([blob.bytes() for blob in server_cert.cert_chain_pems])
    )
    server_cert.private_key_pem.write_to_path(key_file)

    yield cert_file, key_file


@pytest.fixture(scope="session")
def client_private_key_password():
    yield b"password"


@pytest.fixture(scope="session")
def client_cert_and_key(
    ca,
    hostname,
    ip_address,
    tmp_path_factory: pytest.TempdirFactory,
    client_private_key_password,
):
    tmp_path = tmp_path_factory.mktemp("client_certs")
    cert_file = tmp_path / "client.cert"
    key_file = tmp_path / "client.key"
    cert_key_file = tmp_path / "client_cert_key.pem"
    enc_key_file = tmp_path / "client_enc_key.pem"

    cert: trustme.LeafCert = ca.issue_cert(hostname, ip_address)

    cert.private_key_and_cert_chain_pem.write_to_path(cert_key_file)
    cert_file.write_bytes(b"".join([blob.bytes() for blob in cert.cert_chain_pems]))
    cert.private_key_pem.write_to_path(key_file)

    client_private_key = load_pem_private_key(
        cert.private_key_pem.bytes(),
        None,
    )
    client_enc_key_bytes = client_private_key.private_bytes(
        Encoding.PEM,
        PrivateFormat.PKCS8,
        BestAvailableEncryption(client_private_key_password),
    )
    enc_key_file.write_bytes(client_enc_key_bytes)

    yield cert_file, key_file, cert_key_file, enc_key_file


@pytest.fixture(scope="session")
def server_cert_path(server_cert_and_key):
    yield server_cert_and_key[0]


@pytest.fixture(scope="session")
def server_key_path(server_cert_and_key):
    yield server_cert_and_key[1]


@pytest.fixture(scope="session")
def client_cert_and_key_path(client_cert_and_key):
    yield client_cert_and_key[2]


@pytest.fixture(scope="session")
def client_cert_path(client_cert_and_key):
    yield client_cert_and_key[0]


@pytest.fixture(scope="session")
def client_key_path(client_cert_and_key):
    yield client_cert_and_key[1]


@pytest.fixture(scope="session")
def client_encrypted_key_path(client_cert_and_key):
    yield client_cert_and_key[3]


@dataclass
class ServerResponse:
    response: bytes = b""


class FakeServer:
    def __init__(self, loop: asyncio.AbstractEventLoop, resp: ServerResponse):
        self.loop = loop
        self.resp = resp
        self.is_ready = threading.Event()
        self.is_done = None

    async def server(self, reader: StreamReader, writer: StreamWriter):
        buffer_size = 1024
        data = b""
        while chunk := await reader.read(buffer_size):
            data += chunk
            if len(chunk) < buffer_size:
                break
        writer.write(self.resp.response)
        if writer.can_write_eof():
            writer.write_eof()
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        self.is_done.set()

    async def create_server(self, *args, **kwargs):
        raise NotImplementedError

    async def start_server(self, *args, **kwargs):
        server = await self.create_server(*args, **kwargs)
        self.is_ready.set()
        await self.is_done.wait()
        server.close()
        await server.wait_closed()

    def run(self, *args, **kwargs):
        asyncio.set_event_loop(self.loop)
        self.is_done = asyncio.Event()
        self.loop.run_until_complete(self.start_server(*args, **kwargs))


class FakeTcpServer(FakeServer):
    async def create_server(self, port, ssl_context=None):
        return await asyncio.start_server(
            self.server, "localhost", port, ssl=ssl_context
        )


class FakeUnixServer(FakeServer):
    async def create_server(self, path):
        return await asyncio.start_unix_server(self.server, path)


@pytest.fixture
async def fake_tcp_server(unused_tcp_port, response_ok):
    resp = ServerResponse(response_ok)
    fake = FakeTcpServer(asyncio.new_event_loop(), resp)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(fake.run, unused_tcp_port)
        fake.is_ready.wait()
        yield resp, "localhost", unused_tcp_port
        fake.loop.call_soon_threadsafe(fake.is_done.set)


@pytest.fixture
async def fake_tcp_ssl_server(unused_tcp_port, response_ok, server_cert):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    server_cert.configure_cert(context)
    resp = ServerResponse(response_ok)
    fake = FakeTcpServer(asyncio.new_event_loop(), resp)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(fake.run, unused_tcp_port, context)
        fake.is_ready.wait()
        yield resp, "localhost", unused_tcp_port
        fake.loop.call_soon_threadsafe(fake.is_done.set)


@pytest.fixture
async def fake_tcp_ssl_client(unused_tcp_port, response_ok, ca, server_cert):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    server_cert.configure_cert(context)
    ca.configure_trust(context)
    resp = ServerResponse(response_ok)
    fake = FakeTcpServer(asyncio.new_event_loop(), resp)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(fake.run, unused_tcp_port, context)
        fake.is_ready.wait()
        yield resp, "localhost", unused_tcp_port
        fake.loop.call_soon_threadsafe(fake.is_done.set)


@pytest.fixture
def mock_reader_writer(mocker: MockerFixture, response_ok):
    mock_reader = mocker.MagicMock()
    mock_reader.read = mocker.AsyncMock(return_value=response_ok)
    mock_writer = mocker.MagicMock()
    mock_writer.drain = mocker.AsyncMock()
    mock_writer.write = mocker.MagicMock()

    mocker.patch("asyncio.open_connection", return_value=(mock_reader, mock_writer))
    if sys.platform != "win32":
        mocker.patch(
            "asyncio.open_unix_connection", return_value=(mock_reader, mock_writer)
        )

    yield mock_reader, mock_writer


# Integration fixtures


def spawn_spamd(options, timeout):
    spamd_exe = Path(which("spamd"))
    process = Popen(
        [spamd_exe, *options],
        stdout=PIPE,
        stderr=STDOUT,
        cwd=spamd_exe.parent,
        universal_newlines=True,
    )

    timeout = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=timeout)

    running = False
    spamd_start = "info: spamd: server started on"
    while not running:
        if datetime.datetime.now(datetime.UTC) > timeout:
            raise TimeoutError

        for line in process.stdout:
            if spamd_start in line:
                running = True
                break

    if not running:
        raise ChildProcessError

    return process


def shutdown_spamd(process):
    process.terminate()
    try:
        process.wait(timeout=5)
    except TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


@pytest.fixture(scope="session")
def spamd_timeout(request):
    yield request.config.getoption("--spamd-process-timeout")


@pytest.fixture(scope="session")
def spamd_common_options():
    yield ["--local", "--allow-tell"]


@pytest.fixture(scope="session")
def spamd_tcp(spamd_common_options, unused_tcp_port_factory, spamd_timeout):
    port = unused_tcp_port_factory()
    process = spawn_spamd(
        spamd_common_options + [f"--listen=localhost:{port}"], spamd_timeout
    )
    yield "localhost", port
    shutdown_spamd(process)


@pytest.fixture(scope="session")
def spamd_ssl(
    spamd_common_options,
    unused_tcp_port_factory,
    server_cert_path,
    server_key_path,
    spamd_timeout,
):
    port = unused_tcp_port_factory()
    process = spawn_spamd(
        spamd_common_options
        + [
            f"--listen=ssl:localhost:{port}",
            "--server-cert",
            f"{server_cert_path}",
            "--server-key",
            f"{server_key_path}",
        ],
        spamd_timeout,
    )
    yield "localhost", port
    shutdown_spamd(process)


@pytest.fixture(scope="session")
def spamd_ssl_client(
    spamd_common_options,
    unused_tcp_port_factory,
    server_cert_path,
    server_key_path,
    ca_cert_path,
    spamd_timeout,
):
    port = unused_tcp_port_factory()
    process = spawn_spamd(
        spamd_common_options
        + [
            f"--listen=ssl:localhost:{port}",
            "--server-cert",
            f"{server_cert_path}",
            "--server-key",
            f"{server_key_path}",
            "--ssl-ca-file",
            f"{ca_cert_path}",
            "--ssl-verify",
        ],
        spamd_timeout,
    )
    yield "localhost", port
    shutdown_spamd(process)


@pytest.fixture(scope="session")
def spamd_unix(spamd_common_options, tmp_path_factory, spamd_timeout):
    unix_socket = tmp_path_factory.mktemp("spamd") / "spamd.sock"
    process = spawn_spamd(
        spamd_common_options + [f"--socketpath={unix_socket}"], spamd_timeout
    )
    yield unix_socket
    shutdown_spamd(process)
