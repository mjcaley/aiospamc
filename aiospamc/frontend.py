#!/usr/bin/env python

"""Frontend functions for the package."""

from typing import (
    Any,
    Dict,
    Optional,
    SupportsBytes,
    Union,
)

from loguru import logger

from .client import Client
from .connections import Timeout
from .header_values import MessageClassValue
from .options import ActionOption, MessageClassOption
from .incremental_parser import parse_set_remove_value
from .responses import Response
from .requests import Request


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
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
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

    client = kwargs.get("client", Client())

    req = Request("CHECK", body=bytes(message))
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending CHECK request")

    try:
        response = await client.request(
            req,
            host=host,
            port=port,
            socket_path=socket_path,
            timeout=timeout,
            verify=verify,
            user=user,
            compress=compress,
        )
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
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
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

    client = kwargs.get("client", Client())

    req = Request("HEADERS", body=bytes(message))
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending HEADERS request")

    try:
        response = await client.request(
            req,
            host=host,
            port=port,
            socket_path=socket_path,
            timeout=timeout,
            verify=verify,
            user=user,
            compress=compress,
        )
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
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
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

    client = kwargs.get("client", Client())

    req = Request("PING")
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        request=req,
    )
    context_logger.info("Sending PING request")

    try:
        response = await client.request(
            req,
            host=host,
            port=port,
            socket_path=socket_path,
            timeout=timeout,
            verify=verify,
        )
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
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
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

    client = kwargs.get("client", Client())

    req = Request("PROCESS", body=bytes(message))
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending PROCESS request")

    try:
        response = await client.request(
            req,
            host=host,
            port=port,
            socket_path=socket_path,
            timeout=timeout,
            verify=verify,
            user=user,
            compress=compress,
        )
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
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
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

    client = kwargs.get("client", Client())

    req = Request("REPORT", body=bytes(message))
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending REPORT request")

    try:
        response = await client.request(
            req,
            host=host,
            port=port,
            socket_path=socket_path,
            timeout=timeout,
            verify=verify,
            user=user,
            compress=compress,
        )
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
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
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

    client = kwargs.get("client", Client())

    req = Request("REPORT_IFSPAM", body=bytes(message))
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending REPORT_IFSPAM request")

    try:
        response = await client.request(
            req,
            host=host,
            port=port,
            socket_path=socket_path,
            timeout=timeout,
            verify=verify,
            user=user,
            compress=compress,
        )
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
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
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

    client = kwargs.get("client", Client())

    req = Request("SYMBOLS", body=bytes(message))
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending SYMBOLS request")

    try:
        response = await client.request(
            req,
            host=host,
            port=port,
            socket_path=socket_path,
            timeout=timeout,
            verify=verify,
            user=user,
            compress=compress,
        )
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
        Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
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

    client = kwargs.get("client", Client())

    headers: Dict[str, Any] = {
        "Message-class": MessageClassValue(MessageClassOption(message_class))
    }
    if remove_action:
        headers["Remove"] = parse_set_remove_value(remove_action)
    if set_action:
        headers["Set"] = parse_set_remove_value(set_action)
    req = Request("TELL", headers=headers, body=bytes(message))
    context_logger = logger.bind(
        host=host,
        port=port,
        socket_path=socket_path,
        user=user,
        request=req,
    )
    context_logger.info("Sending TELL request")

    try:
        response = await client.request(
            req,
            host=host,
            port=port,
            socket_path=socket_path,
            timeout=timeout,
            verify=verify,
            user=user,
            compress=compress,
        )
    except Exception:
        context_logger.exception("Exception when calling tell function")
        raise

    context_logger.bind(response=response).success(
        "Successfully completed tell function"
    )

    return response
