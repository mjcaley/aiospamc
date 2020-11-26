#!/usr/bin/end python

"""Frontend functions for the package."""

import logging
import time
from typing import (
    Any,
    Callable,
    Dict,
    NamedTuple,
    Optional,
    SupportsBytes,
    Type,
    Union,
)
from ssl import SSLContext

from .connections import Timeout, new_connection, new_ssl_context, ConnectionManager
from .exceptions import BadResponse, ParseError
from .header_values import CompressValue, MessageClassValue, UserValue
from .options import ActionOption, MessageClassOption
from .incremental_parser import ResponseParser, parse_set_remove_value
from .responses import Response
from .requests import Request


ConnectionFactory = Callable[
    [
        Optional[str],
        Optional[int],
        Optional[str],
        Optional[Timeout],
        Optional[SSLContext],
    ],
    ConnectionManager,
]
SSLFactory = Callable[[Any], Optional[SSLContext]]


class Client(NamedTuple):
    ssl_context_factory: SSLFactory
    connection_factory: ConnectionFactory
    parser_factory: Type[ResponseParser]


DEFAULT_CLIENT = Client(new_ssl_context, new_connection, ResponseParser)

LOGGER = logging.getLogger("aiospamc")


async def request(
    req: Request, connection: ConnectionManager, parser: ResponseParser
) -> Response:
    """Sends a request and returns the parsed response.

    :param req: The request to send.
    :param connection: An instance of a connection.
    :param parser: An instance of a response parser.

    :return: The parsed response.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    """

    start = time.monotonic()
    LOGGER.info(
        "Sending %s request",
        req.verb,
        extra={
            "message_id": id(req.body),
            "request_id": id(req),
            "connection_id": id(connection),
        },
    )
    response = await connection.request(bytes(req))
    try:
        parsed_response = parser.parse(response)
    except ParseError as error:
        LOGGER.exception(
            "Error parsing response",
            exc_info=error,
            extra={"request_id": id(req), "connection_id": id(connection)},
        )
        raise BadResponse(response) from error
    response_obj = Response(**parsed_response)
    response_obj.raise_for_status()
    end = time.monotonic()
    LOGGER.info(
        "Successfully received response in %0.2f",
        end - start,
        extra={"request_id": id(req), "connection_id": id(connection)},
    )

    return response_obj


def _new_connection(
    connection_factory: ConnectionFactory,
    ssl_context_factory: SSLFactory,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Any = None,
) -> ConnectionManager:
    ssl_context = ssl_context_factory(verify)
    connection = connection_factory(host, port, socket_path, timeout, ssl_context)

    return connection


def _add_headers(req: Request, user: Optional[str], compress: Optional[bool]) -> None:
    if user:
        req.headers["User"] = UserValue(user)
    if compress:
        req.headers["Compress"] = CompressValue()


async def check(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = False,
    **kwargs,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :module:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
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

    client = kwargs.get("client", DEFAULT_CLIENT)

    req = Request("CHECK", body=bytes(message))
    _add_headers(req, user, compress)
    connection = _new_connection(
        client.connection_factory,
        client.ssl_context_factory,
        host,
        port,
        socket_path,
        timeout,
        verify,
    )
    parser = client.parser_factory()

    return await request(req, connection, parser)


async def headers(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = False,
    **kwargs,
) -> Response:
    """Checks a message if it's spam and return the modified message headers.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :module:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
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

    client = kwargs.get("client", DEFAULT_CLIENT)

    req = Request("HEADERS", body=bytes(message))
    _add_headers(req, user, compress)
    connection = _new_connection(
        client.connection_factory,
        client.ssl_context_factory,
        host,
        port,
        socket_path,
        timeout,
        verify,
    )
    parser = client.parser_factory()

    return await request(req, connection, parser)


async def ping(
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    **kwargs,
) -> Response:
    """Sends a ping to the SPAMD service.

    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :module:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.

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

    client = kwargs.get("client", DEFAULT_CLIENT)

    req = Request("PING")
    connection = _new_connection(
        client.connection_factory,
        client.ssl_context_factory,
        host,
        port,
        socket_path,
        timeout,
        verify,
    )
    parser = client.parser_factory()

    return await request(req, connection, parser)


async def process(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = False,
    **kwargs,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :module:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
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

    client = kwargs.get("client", DEFAULT_CLIENT)

    req = Request("PROCESS", body=bytes(message))
    _add_headers(req, user, compress)
    connection = _new_connection(
        client.connection_factory,
        client.ssl_context_factory,
        host,
        port,
        socket_path,
        timeout,
        verify,
    )
    parser = client.parser_factory()

    return await request(req, connection, parser)


async def report(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = False,
    **kwargs,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :module:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
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

    client = kwargs.get("client", DEFAULT_CLIENT)

    req = Request("REPORT", body=bytes(message))
    _add_headers(req, user, compress)
    connection = _new_connection(
        client.connection_factory,
        client.ssl_context_factory,
        host,
        port,
        socket_path,
        timeout,
        verify,
    )
    parser = client.parser_factory()

    return await request(req, connection, parser)


async def report_if_spam(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = False,
    **kwargs,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :module:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
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

    client = kwargs.get("client", DEFAULT_CLIENT)

    req = Request("REPORT_IFSPAM", body=bytes(message))
    _add_headers(req, user, compress)
    connection = _new_connection(
        client.connection_factory,
        client.ssl_context_factory,
        host,
        port,
        socket_path,
        timeout,
        verify,
    )
    parser = client.parser_factory()

    return await request(req, connection, parser)


async def symbols(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = False,
    **kwargs,
) -> Response:
    """Checks a message if it's spam and return a response with rules that matched.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param socket_path: Path to Unix socket.
    :param timeout: Timeout settings.
    :param verify:
        Enable SSL. `True` will use the root certificates from the :module:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
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

    client = kwargs.get("client", DEFAULT_CLIENT)

    req = Request("SYMBOLS", body=bytes(message))
    _add_headers(req, user, compress)
    connection = _new_connection(
        client.connection_factory,
        client.ssl_context_factory,
        host,
        port,
        socket_path,
        timeout,
        verify,
    )
    parser = client.parser_factory()

    return await request(req, connection, parser)


async def tell(
    message: Union[bytes, SupportsBytes],
    message_class: Union[str, MessageClassOption],
    remove_action: Union[str, ActionOption] = None,
    set_action: Union[str, ActionOption] = None,
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = False,
    **kwargs,
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
        Enable SSL. `True` will use the root certificates from the :module:`certifi` package.
        `False` will use SSL, but not verify the root certificates. Passing a string to a filename
        will use the path to verify the root certificates.
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

    client = kwargs.get("client", DEFAULT_CLIENT)

    headers: Dict[str, Any] = {
        "Message-class": MessageClassValue(MessageClassOption(message_class))
    }
    if remove_action:
        headers["Remove"] = parse_set_remove_value(remove_action)
    if set_action:
        headers["Set"] = parse_set_remove_value(set_action)
    req = Request("TELL", headers=headers, body=bytes(message))
    _add_headers(req, user, compress)

    connection = _new_connection(
        client.connection_factory,
        client.ssl_context_factory,
        host,
        port,
        socket_path,
        timeout,
        verify,
    )
    parser = client.parser_factory()

    return await request(req, connection, parser)
