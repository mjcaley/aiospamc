#!/usr/bin/env python3

"""Module implementing client objects that all requests go through."""

from dataclasses import dataclass
from ssl import SSLContext
from typing import Any, Callable, Optional, Type

from loguru import logger

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

    @staticmethod
    async def request(
        req: Request, connection: ConnectionManager, parser: ResponseParser
    ) -> Response:
        """Sends a request and returns the parsed response.

        :param req: The request to send.
        :param connection: Instance of a `ConnectionManager`.
        :param parser: Instance of `ResponseParser`.

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

        context_logger = logger.bind(
            connection=connection,
            request=req,
        )

        raise_warnings(req, connection)

        context_logger.info("Sending {} request", req.verb)
        response = await connection.request(bytes(req))
        context_logger = context_logger.bind(response_bytes=response)
        try:
            parsed_response = parser.parse(response)
        except ParseError as error:
            context_logger.exception("Error parsing response")
            raise BadResponse(response) from error
        response_obj = Response(**parsed_response)
        response_obj.raise_for_status()
        context_logger.bind(response=response_obj).info(
            "Successfully received response"
        )

        return response_obj
