#!/usr/bin/end python

"""Frontend functions for the package."""

from aiospamc.exceptions import BadResponse
from typing import (
    Any,
    Callable,
    Dict,
    Mapping,
    NamedTuple,
    Optional,
    SupportsBytes,
    Type,
    Union,
)
from ssl import SSLContext

from .header_values import HeaderValue
from .connections import Timeout, new_connection, new_ssl_context, ConnectionManager
from .options import ActionOption, MessageClassOption
from .incremental_parser import ParseError, ResponseParser
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
    client: Client = None,
) -> Response:
    if not client:
        client = DEFAULT_CLIENT
    ssl_context = client.ssl_context_factory(verify)
    connection = client.connection_factory(
        host, port, socket_path, timeout, ssl_context
    )
    parser = client.parser_factory()

    request = Request(verb, headers=headers)
    if user:
        request.headers["User"] = user
    if compress:
        request.headers["Compress"] = "zlib"
    if message:
        request.body = bytes(message)

    response = await connection.request(bytes(request))
    try:
        parsed_response = parser.parse(response)
    except ParseError as e:
        raise BadResponse(e, response)
    response_obj = Response(**parsed_response)

    return response_obj


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
    :raises TimeoutException: Timeout during connection.
    """

    client = kwargs.get("client")

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
        client=client,
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
    :raises TimeoutException: Timeout during connection.
    """

    client = kwargs.get("client")

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
        client=client,
    )


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
    :raises TimeoutException: Timeout during connection.
    """

    client = kwargs.get("client")

    return await request(
        "PING",
        host=host,
        port=port,
        socket_path=socket_path,
        timeout=timeout,
        verify=verify,
        client=client,
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
    :raises TimeoutException: Timeout during connection.
    """

    client = kwargs.get("client")

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
        client=client,
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
    :raises TimeoutException: Timeout during connection.
    """

    client = kwargs.get("client")

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
        client=client,
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
    :raises TimeoutException: Timeout during connection.
    """

    client = kwargs.get("client")

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
        client=client,
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
    :raises TimeoutException: Timeout during connection.
    """

    client = kwargs.get("client")

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
        client=client,
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
    compress: bool = False,
    **kwargs,
) -> Response:
    """Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param message_class: Classify the message as 'spam' or 'ham'.
    :param remove_action: Remove message class for message in database.
    :param set_action:
        Set message class for message in database.  Either `ham` or `spam`.
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
    :raises TimeoutException: Timeout during connection.
    """

    client = kwargs.get("client")

    headers: Dict[str, Any] = {"Message-class": message_class}
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
        client=client,
    )
