"""Frontend functions for the package."""

from __future__ import annotations

import ssl
from functools import partial
from pathlib import Path
from typing import Any, Optional, SupportsBytes, Union, cast

from loguru import logger

from .client import Client
from .connections import ConnectionManagerBuilder, SSLContextBuilder, Timeout
from .header_values import ActionOption, MessageClassOption, MessageClassValue
from .incremental_parser import parse_set_remove_value
from .requests import Request
from .responses import Response


class FrontendClientBuilder:
    """Builds the :class:`aiospamc.client.Client` based off of frontend arguments."""

    def __init__(self):
        """Constructor for FrontendClientBuilder."""

        self._connection_builder = ConnectionManagerBuilder()
        self._ssl = False
        self._ssl_builder = SSLContextBuilder()

    def build(self) -> Client:
        """Builds the :class:`aiospamc.client.Client`.

        :return: An instance of :class:`aiospamc.client.Client`.
        """

        if self._ssl:
            self._connection_builder.add_ssl_context(self._ssl_builder.build())
        connection_manager = self._connection_builder.build()

        return Client(connection_manager)

    def with_connection(
        self,
        host: str = "localhost",
        port: int = 783,
        socket_path: Optional[Path] = None,
    ) -> FrontendClientBuilder:
        """Sets the type of connection manager to use.

        Defaults to TCP, but if a Unix socket is provided it will be used.

        :param host: TCP hostname to use.
        :param port: TCP port to use.
        :param socket_path: Path to the Unix socket.

        :return: This builder instance.
        """

        if socket_path:
            self._connection_builder = self._connection_builder.with_unix_socket(
                socket_path
            )
        else:
            self._connection_builder = self._connection_builder.with_tcp(host, port)

        return self

    def add_verify(
        self, verify: Union[bool, Path, ssl.SSLContext, None] = None
    ) -> FrontendClientBuilder:
        """Adds an SSL context to the connection manager.

        :param verify: How to configure the SSL context. If `True`, add the default
            certificate authorities. If `False`, accept any certificate. If a :class:`pathlib.Path`,
            add the certificates from it. If an :class:`ssl.SSLContext`, then use it.

        :return: This builder instance.
        """

        if verify is None:
            return self

        self._ssl = True

        if verify is True:
            self._ssl_builder.add_default_ca()
        elif verify is False:
            self._ssl_builder.add_default_ca().dont_verify()
        elif isinstance(verify, ssl.SSLContext):
            self._ssl_builder.with_context(verify)
        else:
            self._ssl_builder.add_ca(verify)

        return self

    def add_client_cert(
        self,
        cert: Optional[
            Union[
                Path,
                tuple[Path, Optional[Path]],
                tuple[Path, Optional[Path], Optional[str]],
            ]
        ],
    ) -> FrontendClientBuilder:
        """Add a client certificate to authenticate to the server.

        :param cert: Client certificate. Takes up to three a three tuple value.
            1. Path to the certificate and key.
            2. Path to the certificate and path to the key.
            3. Path to the certificate, path to the key, and password of the key.

        :return: This builder instance.
        """

        if cert is None:
            return self

        if not self._ssl:
            self.add_verify(True)

        def pwd_check(password: Optional[str] = None) -> str:
            """Return the password, otherwise throw an exception.

            :return: The password.
            :raises ValueError: When the password is `None`.
            """

            if password is None:
                raise ValueError("Private key password not provided")
            return password

        if isinstance(cert, Path):
            self._ssl_builder.add_client(cert, password=partial(pwd_check, None))
        elif isinstance(cert, tuple) and len(cert) == 2:
            client, key = cast(tuple[Path, Optional[Path]], cert)
            self._ssl_builder.add_client(client, key, password=partial(pwd_check, None))
        elif isinstance(cert, tuple) and len(cert) == 3:
            client, key, password = cast(
                tuple[Path, Optional[Path], Optional[str]], cert
            )
            self._ssl_builder.add_client(
                client, key, password=partial(pwd_check, password)
            )
        else:
            raise TypeError("Unexepected value")

        return self

    def set_timeout(self, timeout: Optional[Timeout] = None) -> FrontendClientBuilder:
        """Sets the timeout for the connection.

        :param timeout: Timeout object.

        :return: This builder instance.
        """

        if timeout:
            self._connection_builder.set_timeout(timeout)

        return self


def _add_compress_header(request: Request, compress: bool):
    """Adds a compress header to the request if specified.

    :param request: The request to be modified.
    :param compress: Switch if to add compress header.
    """

    if compress:
        request.headers.compress = "zlib"


def _add_user_header(request: Request, user: Optional[str]):
    """Adds a user header to the request if specified.

    :param request: The request to be modified.
    :param user: Optional username to be added.
    """

    if user:
        request.headers.user = user


async def check(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: Optional[Path] = None,
    timeout: Optional[Timeout] = None,
    verify: Union[bool, Path, ssl.SSLContext, None] = None,
    cert: Optional[
        Union[
            Path,
            tuple[Path, Optional[Path]],
            tuple[Path, Optional[Path], Optional[str]],
        ]
    ] = None,
    user: Optional[str] = None,
    compress: bool = False,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
    :param cert: Use client certificate. Can either by a :class:`pathlib.Path` to a file that includes both the
        certificate and key. Can be a tuple containing a :class:`pathlib.Path` to the certificate and a :class:`pathlib.Path` to
        the key. Can be a tuple containing a :class:`pathlib.Path` to the certificate, :class:`pathlib.Path` to the key, and a
        password.
    :param user: Username to pass to the SPAMD service.
    :param compress: Enable compress of the request body.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises ServerTimeoutException: Server returned a response that it timed out.
    :raises ClientTimeoutException: Client timed out during connection.
    """

    req = Request("CHECK", body=bytes(message))
    _add_compress_header(req, compress)
    _add_user_header(req, user)
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending CHECK request")

    client_builder = FrontendClientBuilder()
    client = (
        client_builder.with_connection(host, port, socket_path)
        .add_verify(verify)
        .add_client_cert(cert)
        .set_timeout(timeout)
        .build()
    )
    try:
        response = await client.request(req)
    except Exception:
        context_logger.exception("Exception when calling check function")
        raise

    context_logger.bind(response=response).success(
        "Successfully completed check function"
    )

    return response


async def headers(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: Optional[Path] = None,
    timeout: Optional[Timeout] = None,
    verify: Union[bool, Path, ssl.SSLContext, None] = None,
    cert: Union[
        Path,
        tuple[Path, Optional[Path]],
        tuple[Path, Optional[Path], Optional[str]],
        None,
    ] = None,
    user: Optional[str] = None,
    compress: bool = False,
) -> Response:
    """Checks a message if it's spam and return the modified message headers.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
    :param cert: Use client certificate. Can either by a :class:`pathlib.Path` to a file that includes both the
        certificate and key. Can be a tuple containing a :class:`pathlib.Path` to the certificate and a :class:`pathlib.Path` to
        the key. Can be a tuple containing a :class:`pathlib.Path` to the certificate, :class:`pathlib.Path` to the key, and a
        password.
    :param user: Username to pass to the SPAMD service.
    :param compress: Enable compress of the request body.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.  The body contains the modified
        message headers, but not the content of the message.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises ServerTimeoutException: Server returned a response that it timed out.
    :raises ClientTimeoutException: Client timed out during connection.
    """

    req = Request("HEADERS", body=bytes(message))
    _add_compress_header(req, compress)
    _add_user_header(req, user)
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending HEADERS request")

    client_builder = FrontendClientBuilder()
    client = (
        client_builder.with_connection(host, port, socket_path)
        .add_verify(verify)
        .add_client_cert(cert)
        .set_timeout(timeout)
        .build()
    )
    try:
        response = await client.request(req)
    except Exception:
        context_logger.exception("Exception when calling headers function")
        raise

    context_logger.bind(response=response).success(
        "Successfully completed headers function"
    )

    return response


async def ping(
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: Optional[Path] = None,
    timeout: Optional[Timeout] = None,
    verify: Union[bool, Path, ssl.SSLContext, None] = None,
    cert: Union[
        Path,
        tuple[Path, Optional[Path]],
        tuple[Path, Optional[Path], Optional[str]],
        None,
    ] = None,
) -> Response:
    """Sends a ping to the SPAMD service.

    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
    :param cert: Use client certificate. Can either by a :class:`pathlib.Path` to a file that includes both the
        certificate and key. Can be a tuple containing a :class:`pathlib.Path` to the certificate and a :class:`pathlib.Path` to
        the key. Can be a tuple containing a :class:`pathlib.Path` to the certificate, :class:`pathlib.Path` to the key, and a
        password.

    :return: A response with "PONG".

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises ServerTimeoutException: Server returned a response that it timed out.
    :raises ClientTimeoutException: Client timed out during connection.
    """

    req = Request("PING")
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        request=req,
    )
    context_logger.info("Sending PING request")

    client_builder = FrontendClientBuilder()
    client = (
        client_builder.with_connection(host, port, socket_path)
        .add_verify(verify)
        .add_client_cert(cert)
        .set_timeout(timeout)
        .build()
    )
    try:
        response = await client.request(req)
    except Exception:
        context_logger.exception("Exception when calling ping function")
        raise

    context_logger.bind(response=response).success(
        "Successfully completed ping function"
    )

    return response


async def process(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: Optional[Path] = None,
    timeout: Optional[Timeout] = None,
    verify: Union[bool, Path, ssl.SSLContext, None] = None,
    cert: Union[
        Path,
        tuple[Path, Optional[Path]],
        tuple[Path, Optional[Path], Optional[str]],
        None,
    ] = None,
    user: Optional[str] = None,
    compress: bool = False,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
    :param cert: Use client certificate. Can either by a :class:`pathlib.Path` to a file that includes both the
        certificate and key. Can be a tuple containing a :class:`pathlib.Path` to the certificate and a :class:`pathlib.Path` to
        the key. Can be a tuple containing a :class:`pathlib.Path` to the certificate, :class:`pathlib.Path` to the key, and a
        password.
    :param user: Username to pass to the SPAMD service.
    :param compress: Enable compress of the request body.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.  The body contains a modified
        copy of the message.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises ServerTimeoutException: Server returned a response that it timed out.
    :raises ClientTimeoutException: Client timed out during connection.
    """

    req = Request("PROCESS", body=bytes(message))
    _add_compress_header(req, compress)
    _add_user_header(req, user)
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending PROCESS request")

    client_builder = FrontendClientBuilder()
    client = (
        client_builder.with_connection(host, port, socket_path)
        .add_verify(verify)
        .add_client_cert(cert)
        .set_timeout(timeout)
        .build()
    )
    try:
        response = await client.request(req)
    except Exception:
        context_logger.exception("Exception when calling process function")
        raise

    context_logger.bind(response=response).success(
        "Successfully completed process function"
    )

    return response


async def report(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: Optional[Path] = None,
    timeout: Optional[Timeout] = None,
    verify: Union[bool, Path, ssl.SSLContext, None] = None,
    cert: Union[
        Path,
        tuple[Path, Optional[Path]],
        tuple[Path, Optional[Path], Optional[str]],
        None,
    ] = None,
    user: Optional[str] = None,
    compress: bool = False,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
    :param cert: Use client certificate. Can either by a :class:`pathlib.Path` to a file that includes both the
        certificate and key. Can be a tuple containing a :class:`pathlib.Path` to the certificate and a :class:`pathlib.Path` to
        the key. Can be a tuple containing a :class:`pathlib.Path` to the certificate, :class:`pathlib.Path` to the key, and a
        password.
    :param user: Username to pass to the SPAMD service.
    :param compress: Enable compress of the request body.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.  The body contains a report.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises ServerTimeoutException: Server returned a response that it timed out.
    :raises ClientTimeoutException: Client timed out during connection.
    """

    req = Request("REPORT", body=bytes(message))
    _add_compress_header(req, compress)
    _add_user_header(req, user)
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending REPORT request")

    client_builder = FrontendClientBuilder()
    client = (
        client_builder.with_connection(host, port, socket_path)
        .add_verify(verify)
        .add_client_cert(cert)
        .set_timeout(timeout)
        .build()
    )
    try:
        response = await client.request(req)
    except Exception:
        context_logger.exception("Exception when calling report function")
        raise

    context_logger.bind(response=response).success(
        "Successfully completed report function"
    )

    return response


async def report_if_spam(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: Optional[Path] = None,
    timeout: Optional[Timeout] = None,
    verify: Union[bool, Path, ssl.SSLContext, None] = None,
    cert: Union[
        Path,
        tuple[Path, Optional[Path]],
        tuple[Path, Optional[Path], Optional[str]],
        None,
    ] = None,
    user: Optional[str] = None,
    compress: bool = False,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
    :param cert: Use client certificate. Can either by a :class:`pathlib.Path` to a file that includes both the
        certificate and key. Can be a tuple containing a :class:`pathlib.Path` to the certificate and a :class:`pathlib.Path` to
        the key. Can be a tuple containing a :class:`pathlib.Path` to the certificate, :class:`pathlib.Path` to the key, and a
        password.
    :param user: Username to pass to the SPAMD service.
    :param compress: Enable compress of the request body.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.  The body contains a report if
        the message is considered spam.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises ServerTimeoutException: Server returned a response that it timed out.
    :raises ClientTimeoutException: Client timed out during connection.
    """

    req = Request("REPORT_IFSPAM", body=bytes(message))
    _add_compress_header(req, compress)
    _add_user_header(req, user)
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending REPORT_IFSPAM request")

    client_builder = FrontendClientBuilder()
    client = (
        client_builder.with_connection(host, port, socket_path)
        .add_verify(verify)
        .add_client_cert(cert)
        .set_timeout(timeout)
        .build()
    )
    try:
        response = await client.request(req)
    except Exception:
        context_logger.exception("Exception when calling report_if_spam function")
        raise

    context_logger.bind(response=response).success(
        "Successfully completed report_if_spam function"
    )

    return response


async def symbols(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: Optional[Path] = None,
    timeout: Optional[Timeout] = None,
    verify: Union[bool, Path, ssl.SSLContext, None] = None,
    cert: Union[
        Path,
        tuple[Path, Optional[Path]],
        tuple[Path, Optional[Path], Optional[str]],
        None,
    ] = None,
    user: Optional[str] = None,
    compress: bool = False,
) -> Response:
    """Checks a message if it's spam and return a response with rules that matched.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
    :param cert: Use client certificate. Can either by a :class:`pathlib.Path` to a file that includes both the
        certificate and key. Can be a tuple containing a :class:`pathlib.Path` to the certificate and a :class:`pathlib.Path` to
        the key. Can be a tuple containing a :class:`pathlib.Path` to the certificate, :class:`pathlib.Path` to the key, and a
        password.
    :param user: Username to pass to the SPAMD service.
    :param compress: Enable compress of the request body.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.  The body contains a
        comma-separated list of the symbols that were hit.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises ServerTimeoutException: Server returned a response that it timed out.
    :raises ClientTimeoutException: Client timed out during connection.
    """

    req = Request("SYMBOLS", body=bytes(message))
    _add_compress_header(req, compress)
    _add_user_header(req, user)
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending SYMBOLS request")

    client_builder = FrontendClientBuilder()
    client = (
        client_builder.with_connection(host, port, socket_path)
        .add_verify(verify)
        .add_client_cert(cert)
        .set_timeout(timeout)
        .build()
    )
    try:
        response = await client.request(req)
    except Exception:
        context_logger.exception("Exception when calling symbols function")
        raise

    context_logger.bind(response=response).success(
        "Successfully completed symbols function"
    )

    return response


async def tell(
    message: Union[bytes, SupportsBytes],
    message_class: Union[str, MessageClassOption],
    remove_action: Union[str, ActionOption, None] = None,
    set_action: Union[str, ActionOption, None] = None,
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: Optional[Path] = None,
    timeout: Optional[Timeout] = None,
    verify: Optional[Union[bool, Path, ssl.SSLContext]] = None,
    cert: Union[
        Path,
        tuple[Path, Optional[Path]],
        tuple[Path, Optional[Path], Optional[str]],
        None,
    ] = None,
    user: Optional[str] = None,
    compress: bool = False,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param message_class: Classify the message as 'spam' or 'ham'.
    :param remove_action: Remove message class for message in database.
    :param set_action: Set message class for message in database.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
    :param cert: Use client certificate. Can either by a :class:`pathlib.Path` to a file that includes both the
        certificate and key. Can be a tuple containing a :class:`pathlib.Path` to the certificate and a :class:`pathlib.Path` to
        the key. Can be a tuple containing a :class:`pathlib.Path` to the certificate, :class:`pathlib.Path` to the key, and a
        password.
    :param user: Username to pass to the SPAMD service.
    :param compress: Enable compress of the request body.

    :return:
        A successful response with "DidSet" and/or "DidRemove" headers along with the
        actions that were taken.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises ServerTimeoutException: Server returned a response that it timed out.
    :raises ClientTimeoutException: Client timed out during connection.
    """

    headers: dict[str, Any] = {
        "Message-class": MessageClassValue(MessageClassOption(message_class))
    }
    if remove_action:
        headers["Remove"] = parse_set_remove_value(remove_action)
    if set_action:
        headers["Set"] = parse_set_remove_value(set_action)
    req = Request("TELL", headers=headers, body=bytes(message))
    _add_compress_header(req, compress)
    _add_user_header(req, user)
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending TELL request")

    client_builder = FrontendClientBuilder()
    client = (
        client_builder.with_connection(host, port, socket_path)
        .add_verify(verify)
        .add_client_cert(cert)
        .set_timeout(timeout)
        .build()
    )
    try:
        response = await client.request(req)
    except Exception:
        context_logger.exception("Exception when calling tell function")
        raise

    context_logger.bind(response=response).success(
        "Successfully completed tell function"
    )

    return response
