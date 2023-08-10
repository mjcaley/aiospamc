from __future__ import annotations

import ssl
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Union

import certifi

from aiospamc.connections import (
    ConnectionManager,
    TcpConnectionManager,
    Timeout,
    UnixConnectionManager,
)


class UnixConnectionManagerBuilder:
    def __init__(self):
        self._args = {}

    def build(self) -> UnixConnectionManager:
        return UnixConnectionManager(**self._args)

    def set_path(self, path: Path) -> UnixConnectionManagerBuilder:
        self._args["path"] = path
        return self

    def set_timeout(self, timeout: Timeout) -> UnixConnectionManagerBuilder:
        self._args["timeout"] = timeout
        return self


class TcpConnectionManagerBuilder:
    def __init__(self):
        self._args = {}

    def build(self) -> TcpConnectionManager:
        return TcpConnectionManager(**self._args)

    def set_host(self, host: str) -> TcpConnectionManagerBuilder:
        self._args["host"] = host
        return self

    def set_port(self, port: int) -> TcpConnectionManagerBuilder:
        self._args["port"] = port
        return self

    def set_ssl_context(self, context: ssl.SSLContext) -> TcpConnectionManagerBuilder:
        self._args["ssl_context"] = context
        return self

    def set_timeout(self, timeout: Timeout) -> TcpConnectionManagerBuilder:
        self._args["timeout"] = timeout
        return self


class SSLContextBuilder:
    """SSL context builder."""

    def __init__(self):
        """Builder contstructor. Sets up a default SSL context."""

        self._context = ssl.create_default_context()

    def build(self) -> ssl.SSLContext:
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


class ConnectionManagerBuilder:
    class ManagerType(Enum):
        Undefined = auto()
        Tcp = auto()
        Unix = auto()

    def __init__(self):
        self._manager_type = self.ManagerType.Undefined
        self._tcp_builder = TcpConnectionManagerBuilder()
        self._unix_builder = UnixConnectionManagerBuilder()
        self._ssl_builder = SSLContextBuilder()
        self._ssl = False
        self._timeout = None

    def build(self) -> Union[UnixConnectionManager, TcpConnectionManager]:
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
        self._manager_type = self.ManagerType.Unix
        self._unix_builder.set_path(path)
        self._tcp_host = self._tcp_port = None

        return self

    def with_tcp(self, host: str, port: int = 783) -> ConnectionManagerBuilder:
        self._manager_type = self.ManagerType.Tcp
        self._tcp_builder.set_host(host).set_port(port)
        self._unix_path = None

        return self

    def add_ssl_context(self, context: ssl.SSLContext) -> ConnectionManagerBuilder:
        self._ssl_context = context
        self._ssl = True

        return self

    def set_timeout(self, timeout: Timeout) -> ConnectionManagerBuilder:
        self._timeout = timeout

        return self


def build_ssl_context(
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
