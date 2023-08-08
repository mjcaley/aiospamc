"""ConnectionManager classes for TCP and Unix sockets."""

from __future__ import annotations

import asyncio
import ssl
from pathlib import Path
from typing import Any, Optional, Tuple, Union

import certifi
import loguru
from loguru import logger

from .exceptions import AIOSpamcConnectionFailed, ClientTimeoutException


class Timeout:
    """Container object for defining timeouts."""

    def __init__(
        self,
        total: float = 600,
        connection: Optional[float] = None,
        response: Optional[float] = None,
    ) -> None:
        """Timeout constructor.

        :param total: The total length of time in seconds to set the timeout.
        :param connection: The length of time in seconds to allow for a connection to live before timing out.
        :param response: The length of time in seconds to allow for a response from the server before timing out.
        """

        self.total = total
        self.connection = connection
        self.response = response

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}("
            f"total={self.total}, "
            f"connection={self.connection}, "
            f"response={self.response}"
            ")"
        )


class ConnectionManager:
    """Stores connection parameters and creates connections."""

    def __init__(
        self, connection_string: str, timeout: Optional[Timeout] = None
    ) -> None:
        """ConnectionManager constructor.

        :param timeout: Timeout configuration
        """

        self._connection_string = connection_string
        self.timeout = timeout or Timeout()
        self._logger = logger.bind(
            connection_string=self.connection_string,
            timeout=self.timeout,
        )

    @property
    def logger(self) -> loguru.Logger:
        """Return the logger object."""

        return self._logger

    async def request(self, data: bytes) -> bytes:
        """Send bytes data and receive a response.

        :raises: AIOSpamcConnectionFailed
        :raises: ClientTimeoutException

        :param data: Data to send.
        """

        try:
            response = await asyncio.wait_for(self._send(data), self.timeout.total)
        except asyncio.TimeoutError as error:
            self.logger.exception("Total timeout reached")
            raise ClientTimeoutException from error

        return response

    async def _send(self, data: bytes) -> bytes:
        """Opens a connection, sends data to the writer, waits for the reader, then returns the response.

        :param data: Data to send.

        :return: Byte data from the response.
        """

        reader, writer = await self._connect()

        writer.write(data)
        if writer.can_write_eof():
            writer.write_eof()
        await writer.drain()

        response = await self._receive(reader)

        writer.close()
        await writer.wait_closed()

        return response

    async def _receive(self, reader: asyncio.StreamReader) -> bytes:
        """Takes a reader and returns the response.

        :param reader: asyncio reader.

        :return: Byte data from the response.
        """

        try:
            response = await asyncio.wait_for(reader.read(), self.timeout.response)
        except asyncio.TimeoutError as error:
            self.logger.exception("Timed out receiving data")
            raise ClientTimeoutException from error

        self.logger.success("Successfully received data")

        return response

    async def _connect(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a connection from the connection manager.

        :return: Tuple or asyncio reader and writer.
        """

        try:
            reader, writer = await asyncio.wait_for(
                self.open(), self.timeout.connection
            )
        except asyncio.TimeoutError as error:
            self.logger.exception("Timeout when connecting")
            raise ClientTimeoutException from error

        self.logger.success("Successfully connected")

        return reader, writer

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a connection, returning the reader and writer objects."""

        raise NotImplementedError

    @property
    def connection_string(self) -> str:
        """String representation of the connection."""

        return self._connection_string


class TcpConnectionManager(ConnectionManager):
    """Connection manager for TCP connections."""

    def __init__(
        self,
        host: str,
        port: int,
        ssl_context: Optional[ssl.SSLContext] = None,
        timeout: Optional[Timeout] = None,
    ) -> None:
        """TcpConnectionManager constructor.

        :param host: Hostname or IP address.
        :param port: TCP port.
        :param ssl_context: SSL context.
        :param timeout: Timeout configuration.
        """

        super().__init__(f"{host}:{port}", timeout)
        self.host = host
        self.port = port
        self.ssl_context = ssl_context

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a TCP connection.

        :raises: AIOSpamcConnectionFailed

        :return: Reader and writer for the connection.
        """

        try:
            reader, writer = await asyncio.open_connection(
                self.host, self.port, ssl=self.ssl_context
            )
        except (ConnectionRefusedError, OSError) as error:
            self.logger.exception("Exception occurred when connecting")
            raise AIOSpamcConnectionFailed from error

        return reader, writer


class UnixConnectionManager(ConnectionManager):
    """Connection manager for Unix pipes."""

    def __init__(self, path: str, timeout: Optional[Timeout] = None):
        """UnixConnectionManager constructor.

        :param path: Unix socket path.
        :param timeout: Timeout configuration
        """

        super().__init__(path, timeout)
        self.path = path

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a unix socket path connection.

        :raises: AIOSpamcConnectionFailed

        :return: Reader and writer for the connection.
        """

        try:
            reader, writer = await asyncio.open_unix_connection(self.path)
        except (ConnectionRefusedError, OSError) as error:
            self.logger.exception("Exception occurred when connecting")
            raise AIOSpamcConnectionFailed from error

        return reader, writer


class SSLContextBuilder:
    """SSL context builder."""

    def __init__(self):
        """Builder contstructor. Sets up a default SSL context."""

        self._context = ssl.create_default_context()

    @property
    def context(self) -> ssl.SSLContext:
        """The constructed SSL context."""

        return self._context

    def add_ca_file(self, file: Path) -> SSLContextBuilder:
        """Add certificate authority from a file.

        :param file: File of concatenated certificates.

        :return: The builder instance.
        """

        self._context.load_verify_locations(cafile=file)

        return self

    def add_ca_dir(self, dir: Path) -> SSLContextBuilder:
        """Add certificate authority from a directory.

        :param dir: Directory of certificates.

        :return: The builder instance.
        """

        self._context.load_verify_locations(capath=dir)

        return self

    def add_default_ca(self) -> SSLContextBuilder:
        """Add default certificate authorities.

        :return: The builder instance.
        """

        self._context.load_verify_locations(cafile=certifi.where())

        return self

    def add_client(
        self, file: Path, key: Optional[Path] = None, password: Optional[str] = None
    ) -> SSLContextBuilder:
        """Add client certificate.

        :param file: Path to the client certificate.
        :param key: Path to the key.
        :param password: Password of the key.
        """

        self._context.load_cert_chain(file, key, password)

        return self

    def dont_verify(self) -> SSLContextBuilder:
        """Set the context to not verify certificates."""

        self._context.check_hostname = False
        self._context.verify_mode = ssl.CERT_NONE

        return self


def new_ssl_context(
    verify: bool = True,
    ca_cert: Optional[Path] = None,
    client_cert: Optional[Path] = None,
    client_key: Optional[Path] = None,
    key_password: Optional[str] = None,
) -> ssl.SSLContext:
    """Creates an SSL context based on the supplied parameter.

    :param verify: Whether to verify the server certficiate.
    :param ca_cert: Path to the certificate authority file if being overridden.
    :param client_cert: Path to the client certificate.
    :param client_key: Path to the client certificate private key.
    :param client_password: Password of the private key.

    :return: The SSL context if created.
    """

    builder = SSLContextBuilder()

    if verify:
        builder.add_default_ca()
    else:
        builder.add_default_ca().dont_verify()

    if ca_cert is not None:
        path = Path(ca_cert).absolute()
        if path.is_dir():
            builder.add_ca_dir(path)
        elif path.is_file():
            builder.add_ca_file(path)
        else:
            raise FileNotFoundError(f"CA certificate path does not exist at {ca_cert}")

    if client_cert:
        builder.add_client(client_cert, client_key, key_password)

    return builder.context


def new_connection_manager(
    host: Optional[str] = None,
    port: Optional[int] = None,
    socket_path: Optional[str] = None,
    timeout: Optional[Timeout] = None,
    context: Optional[ssl.SSLContext] = None,
) -> ConnectionManager:
    """Create a new connection manager.

    :param host: TCP hostname.
    :param port: TCP port number.
    :param socket_path: Unix socket path.
    :param timeout: Timeout configuration.
    :param context: SSL context configuration.
    """

    if socket_path:
        return UnixConnectionManager(socket_path, timeout=timeout)
    elif host and port:
        return TcpConnectionManager(host, port, context, timeout)
    else:
        raise ValueError('Either "host" and "port" or "socket_path" must be specified.')
