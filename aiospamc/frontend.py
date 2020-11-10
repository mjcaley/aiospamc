#!/usr/bin/end python

"""Frontend functions for the package."""

from typing import Any, Callable, Mapping, Optional, SupportsBytes, Union
from ssl import SSLContext

from .header_values import HeaderValue
from .connections import Timeout, new_connection, new_ssl_context, ConnectionManager
from .options import ActionOption, MessageClassOption
from .incremental_parser import ResponseParser
from .responses import Response
from .requests import Request


ConnectionFactory = Callable[
    [str, int, str, Optional[Timeout], Optional[SSLContext]], ConnectionManager
]
SSLFactory = Callable[[Any], SSLContext]


async def request(
    verb: str,
    message: Union[bytes, SupportsBytes] = None,
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: Optional[str] = None,
    compress: bool = False,
    headers: Optional[Mapping[str, Union[str, HeaderValue]]] = None,
    parser_cls: Any = ResponseParser,
    ssl_factory: SSLFactory = new_ssl_context,
    connection_factory: ConnectionFactory = new_connection,
) -> Response:

    ssl_context = ssl_factory(verify)
    connection = connection_factory(host, port, socket_path, timeout, ssl_context)
    parser = parser_cls()

    request = Request(verb, headers=headers)
    if user:
        request.headers["User"] = user
    if compress:
        request.headers["Compress"] = "zlib"
    if message:
        request.body = bytes(message)

    response = await connection.request(bytes(request))
    parsed_response = parser.parse(response)

    return parsed_response


async def check(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = None,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param timeout: Timeout settings.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

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
    :raises TimeoutException: Timeout during connection.
    """

    return await request(
        "CHECK",
        message,
        host=host,
        port=port,
        socket_path=socket_path,
        timeout=timeout,
        verify=verify,
        user=user,
        compress=compress,
    )


async def headers(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = None,
) -> Response:
    """Checks a message if it's spam and return the modified message headers.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param timeout: Timeout settings.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client`
        instance.

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
    :raises TimeoutException: Timeout during connection.
    """

    return await request(
        "HEADERS",
        message,
        host=host,
        port=port,
        socket_path=socket_path,
        timeout=timeout,
        verify=verify,
        user=user,
        compress=compress,
    )


async def ping(
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = None,
) -> Response:
    """Sends a ping to the SPAMD service.

    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param timeout: Timeout settings.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

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
    :raises TimeoutException: Timeout during connection.
    """

    return await request(
        "PING",
        host=host,
        port=port,
        socket_path=socket_path,
        timeout=timeout,
        verify=verify,
        user=user,
        compress=compress,
    )


async def process(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = None,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param timeout: Timeout settings.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

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
    :raises TimeoutException: Timeout during connection.
    """

    return await request(
        "PROCESS",
        message,
        host=host,
        port=port,
        socket_path=socket_path,
        timeout=timeout,
        verify=verify,
        user=user,
        compress=compress,
    )


async def report(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = None,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param timeout: Timeout settings.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

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
    :raises TimeoutException: Timeout during connection.
    """

    return await request(
        "REPORT",
        message,
        host=host,
        port=port,
        socket_path=socket_path,
        timeout=timeout,
        verify=verify,
        user=user,
        compress=compress,
    )


async def report_if_spam(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = None,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param timeout: Timeout settings.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

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
    :raises TimeoutException: Timeout during connection.
    """

    return await request(
        "REPORT_IFSPAM",
        message,
        host=host,
        port=port,
        socket_path=socket_path,
        timeout=timeout,
        verify=verify,
        user=user,
        compress=compress,
    )


async def symbols(
    message: Union[bytes, SupportsBytes],
    *,
    host: str = "localhost",
    port: int = 783,
    socket_path: str = None,
    timeout: Timeout = None,
    verify: Optional[Any] = None,
    user: str = None,
    compress: bool = None,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param timeout: Timeout settings.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

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
    :raises TimeoutException: Timeout during connection.
    """

    return await request(
        "SYMBOLS",
        message,
        host=host,
        port=port,
        socket_path=socket_path,
        timeout=timeout,
        verify=verify,
        user=user,
        compress=compress,
    )


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
    compress: bool = None,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param message_class: How to classify the message, either "ham" or "spam".
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param remove_action: Remove message class for message in database.
    :param set_action:
        Set message class for message in database.  Either `ham` or `spam`.
    :param timeout: Timeout settings.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

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
    :raises TimeoutException: Timeout during connection.
    """

    headers = {"Message-class": message_class}
    if remove_action:
        headers["Remove"] = remove_action
    if set_action:
        headers["Set"] = set_action

    return await request(
        "TELL",
        message,
        host=host,
        port=port,
        socket_path=socket_path,
        timeout=timeout,
        verify=verify,
        user=user,
        compress=compress,
        headers=headers,
    )