from __future__ import annotations
from pathlib import Path
import ssl
from typing import Optional, Union

import certifi

from aiospamc.connections import TcpConnectionManager, Timeout, UnixConnectionManager



class UnixConnectionManagerBuilder:
    def __init__(self, connection_manager: UnixConnectionManager):
        self._connection_manager = connection_manager

    def build(self) -> UnixConnectionManager:
        return self._connection_manager
    
    def set_path(self, path: Path) -> UnixConnectionManagerBuilder:
        self._connection_manager.path = path
        return self
    
    def set_timeout(self, timeout: Timeout) -> UnixConnectionManagerBuilder:
        self._connection_manager.timeout = timeout
        return self


class TcpConnectionManagerBuilder:
    def __init__(self, connection_manager: TcpConnectionManager):
        self._connection_manager = connection_manager

    def build(self) -> TcpConnectionManager:
        return self._connection_manager
    
    def set_host(self, host: str) -> TcpConnectionManagerBuilder:
        self._connection_manager.host = host
        return self
    
    def set_port(self, port: int) -> TcpConnectionManagerBuilder:
        self._connection_manager.port = port
        return self
    
    def set_ssl_context(self, context: ssl.SSLContext) -> TcpConnectionManagerBuilder:
        self._connection_manager.ssl_context = context
        return self
    
    def set_timeout(self, timeout: Timeout) -> TcpConnectionManagerBuilder:
        self._connection_manager.timeout = timeout
        return self


class ConnectionManagerBuilder:
    def __init__(self):
        self._builder: Union[UnixConnectionManagerBuilder, TcpConnectionManagerBuilder] = None
    
    def build(self):
        if not self._builder:
            raise ValueError("Connection information was not provided")
        return self._builder.build()

    def with_unix_socket(self, path: Path) -> UnixConnectionManagerBuilder:
        connection_manager = UnixConnectionManager(path)
        self._builder = UnixConnectionManagerBuilder(connection_manager)
    
        return self._builder

    def with_tcp(self, host: str, port: int = 783) -> TcpConnectionManagerBuilder:
        self._connection_manager = TcpConnectionManager(host, port)

        return self
    

class MonolithicConnectionManagerBuilder:
    def __init__(self):
        pass

    def build(self):
        pass


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
