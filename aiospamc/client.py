#!/usr/bin/env python3

"""Module implementing client objects that all requests go through."""

from dataclasses import dataclass
import logging
from typing import (
    Any,
    Callable,
    Optional,
    Type,
)
from ssl import SSLContext
import time

from .connections import (
    ConnectionManager,
    Timeout,
    new_connection_manager,
    new_ssl_context,
)
from .exceptions import BadResponse
from .header_values import CompressValue, UserValue
from .incremental_parser import ParseError, ResponseParser
from .requests import Request
from .responses import Response
from .user_warnings import raise_warnings


LOGGER = logging.getLogger(__package__)


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


@dataclass
class Client:
    """Client class containing factories."""

    ssl_context_factory: SSLFactory = new_ssl_context
    connection_factory: ConnectionFactory = new_connection_manager
    parser_factory: Type[ResponseParser] = ResponseParser

    async def request(
        self,
        req: Request,
        host: str = "localhost",
        port: int = 783,
        socket_path: str = None,
        timeout: Timeout = None,
        verify: Optional[Any] = None,
        user: str = None,
        compress: bool = False,
    ) -> Response:
        """Sends a request and returns the parsed response.

        :param req: The request to send.
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

        :return: The parsed response.

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

        ssl_context = self.ssl_context_factory(verify)
        connection = self.connection_factory(
            host, port, socket_path, timeout, ssl_context
        )
        parser = self.parser_factory()

        if user:
            req.headers["User"] = UserValue(user)
        if compress:
            req.headers["Compress"] = CompressValue()

        raise_warnings(req, connection)

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
