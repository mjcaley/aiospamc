"""ConnectionManager classes for TCP and Unix sockets."""

from __future__ import annotations

import asyncio
import ssl
from enum import Enum, auto
from getpass import getpass
from pathlib import Path
from typing import Any, Callable, Optional, Union

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

        self.total = float(total)
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


class ConnectionManagerBuilder:
    """Builder for connection managers."""

    class ManagerType(Enum):
        """Define connection manager type during build."""

        Undefined = auto()
        Tcp = auto()
        Unix = auto()

    def __init__(self):
        """ConnectionManagerBuilder constructor."""

        self._manager_type = self.ManagerType.Undefined
        self._tcp_builder = TcpConnectionManagerBuilder()
        self._unix_builder = UnixConnectionManagerBuilder()
        self._ssl_builder = SSLContextBuilder()
        self._ssl = False
        self._timeout = None

    def build(self) -> Union[UnixConnectionManager, TcpConnectionManager]:
        """Builds the :class:`aiospamc.connections.ConnectionManager`.

        :return: An instance of :class:`aiospamc.connections.TcpConnectionManager`
            or :class:`aiospamc.connections.UnixConnectionManager`
        """

        if self._manager_type is self.ManagerType.Undefined:
            raise ValueError(
                "Connection type is undefined, builder must be called with 'with_unix_socket' or 'with_tcp'"
            )
        elif self._manager_type is self.ManagerType.Tcp:
            ssl_context = None if not self._ssl else self._ssl_builder.build()
            self._tcp_builder.set_ssl_context(ssl_context)
            return self._tcp_builder.set_timeout(self._timeout).build()
        else:
            return self._unix_builder.set_timeout(self._timeout).build()

    def with_unix_socket(self, path: Path) -> ConnectionManagerBuilder:
        """Configures the builder to use a Unix socket connection.

        :param path: Path to the Unix socket.

        :return: This builder instance.
        """

        self._manager_type = self.ManagerType.Unix
        self._unix_builder.set_path(path)
        self._tcp_host = self._tcp_port = None

        return self

    def with_tcp(self, host: str, port: int = 783) -> ConnectionManagerBuilder:
        """Configures the builder to use a TCP connection.

        :param host: Hostname to use.
        :param port: Port to use.

        :return: This builder instance.
        """

        self._manager_type = self.ManagerType.Tcp
        self._tcp_builder.set_host(host).set_port(port)
        self._unix_path = None

        return self

    def add_ssl_context(self, context: ssl.SSLContext) -> ConnectionManagerBuilder:
        """Adds an SSL context when a TCP connection is being used.

        :param context: :class:`ssl.SSLContext` instance.

        :return: This builder instance.
        """

        self._ssl_builder.with_context(context)
        self._ssl = True

        return self

    def set_timeout(self, timeout: Timeout) -> ConnectionManagerBuilder:
        """Sets the timeout for the connection.

        :param timeout: Timeout object.

        :return: This builder instance.
        """

        self._timeout = timeout

        return self


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
        except asyncio.TimeoutError:
            self.logger.exception("Total timeout reached")
            raise

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

    async def _connect(self) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
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

    async def open(self) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a connection, returning the reader and writer objects."""

        raise NotImplementedError

    @property
    def connection_string(self) -> str:
        """String representation of the connection."""

        return self._connection_string


class TcpConnectionManagerBuilder:
    """Builder for :class:`aiospamc.connections.TcpConnectionManager`"""

    def __init__(self):
        """`TcpConnectionManagerBuilder` constructor."""

        self._args = {}

    def build(self) -> TcpConnectionManager:
        """Builds the :class:`aiospamc.connections.TcpConnectionManager`.

        :return: An instance of :class:`aiospamc.connections.TcpConnectionManager`.
        """

        return TcpConnectionManager(**self._args)

    def set_host(self, host: str) -> TcpConnectionManagerBuilder:
        """Sets the host to use.

        :param host: Hostname to use.

        :return: This builder instance.
        """

        self._args["host"] = host
        return self

    def set_port(self, port: int) -> TcpConnectionManagerBuilder:
        """Sets the port to use.

        :param port: Port to use.

        :return: This builder instance.
        """

        self._args["port"] = port
        return self

    def set_ssl_context(self, context: ssl.SSLContext) -> TcpConnectionManagerBuilder:
        """Set an SSL context.

        :param context: An instance of :class:`ssl.SSLContext`.

        :return: This builder instance.
        """

        self._args["ssl_context"] = context
        return self

    def set_timeout(self, timeout: Timeout) -> TcpConnectionManagerBuilder:
        """Sets the timeout for the connection.

        :param timeout: Timeout object.

        :return: This builder instance.
        """

        self._args["timeout"] = timeout
        return self


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

    async def open(self) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
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


class UnixConnectionManagerBuilder:
    """Builder for :class:`aiospamc.connections.UnixConnectionManager`."""

    def __init__(self):
        """`UnixConnectionManagerBuilder` constructor."""

        self._args = {}

    def build(self) -> UnixConnectionManager:
        """Builds a :class:`aiospamc.connections.UnixConnectionManager`.

        :return: An instance of :class:`aiospamc.connections.UnixConnectionManager`.
        """

        return UnixConnectionManager(**self._args)

    def set_path(self, path: Path) -> UnixConnectionManagerBuilder:
        """Sets the unix socket path.

        :param path: Path to the Unix socket.

        :return: This builder instance.
        """

        self._args["path"] = path
        return self

    def set_timeout(self, timeout: Timeout) -> UnixConnectionManagerBuilder:
        """Sets the timeout for the connection.

        :param timeout: Timeout object.

        :return: This builder instance.
        """

        self._args["timeout"] = timeout
        return self


class UnixConnectionManager(ConnectionManager):
    """Connection manager for Unix pipes."""

    def __init__(self, path: Path, timeout: Optional[Timeout] = None):
        """UnixConnectionManager constructor.

        :param path: Unix socket path.
        :param timeout: Timeout configuration
        """

        super().__init__(str(path), timeout)
        self.path = path

    async def open(self) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
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

    def build(self) -> ssl.SSLContext:
        """Builds the SSL context.

        :return: An instance of :class:`ssl.SSLContext`.
        """

        return self._context

    def with_context(self, context: ssl.SSLContext) -> SSLContextBuilder:
        """Use the SSL context.

        :param context: Provided SSL context.

        :return: The builder instance.
        """

        self._context = context

        return self

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

    def add_ca(self, path: Path) -> SSLContextBuilder:
        """Add a certificate authority.

        :param path: Directory or file of certificates.

        :return: The builder instance.
        """

        if path.is_dir():
            return self.add_ca_dir(path)
        elif path.is_file():
            return self.add_ca_file(path)
        else:
            raise FileNotFoundError(path)

    def add_default_ca(self) -> SSLContextBuilder:
        """Add default certificate authorities.

        :return: The builder instance.
        """

        self._context.load_verify_locations(cafile=certifi.where())

        return self

    def add_client(
        self,
        file: Path,
        key: Optional[Path] = None,
        password: Optional[Callable[[], Union[str, bytes, bytearray]]] = None,
    ) -> SSLContextBuilder:
        """Add client certificate.

        :param file: Path to the client certificate.
        :param key: Path to the key.
        :param password: Callable that returns the password, if any.
        """

        self._context.load_cert_chain(file, key, password)

        return self

    def dont_verify(self) -> SSLContextBuilder:
        """Set the context to not verify certificates."""

        self._context.check_hostname = False
        self._context.verify_mode = ssl.CERT_NONE

        return self
