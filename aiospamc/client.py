"""Module implementing client objects that all requests go through."""

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


class Client:
    """Client class containing factories."""

    default_ssl_context_factory: Optional[SSLFactory] = staticmethod(new_ssl_context)
    default_connection_factory: ConnectionFactory = staticmethod(new_connection_manager)
    default_parser_factory: Type[ResponseParser] = ResponseParser

    def __init__(
        self, ssl_context_factory=None, connection_factory=None, parser_factory=None
    ):
        """Client constructor.

        :param default_ssl_context_factory: SSL context factory function.
        :param default_connection_factory: `ConnectionManager` factory function.
        :param default_parser_factory: Response parser type.
        """

        self.ssl_context_factory = (
            ssl_context_factory or self.default_ssl_context_factory
        )
        self.connection_factory = connection_factory or self.default_connection_factory
        self.parser_factory = parser_factory or self.default_parser_factory

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
        context_logger.bind(response=response_obj).success(
            "Successfully received response"
        )

        return response_obj
