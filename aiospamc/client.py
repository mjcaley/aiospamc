"""Module implementing client objects that all requests go through."""

from loguru import logger

from .connections import ConnectionManager
from .exceptions import BadResponse
from .incremental_parser import ParseError, ResponseParser
from .requests import Request
from .responses import Response
from .user_warnings import raise_warnings


class Client:
    """Client object to submit requests."""

    def __init__(self, connection_manager: ConnectionManager):
        """Client constructor.

        :param connection_manager: Instance of a connection manager.
        """

        self.connection_manager = connection_manager

    async def request(self, req: Request):
        """Sends a request and returns the parsed response.

        :param req: The request to send.

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
            connection=self.connection_manager,
            request=req,
        )

        raise_warnings(req, self.connection_manager)

        context_logger.info("Sending {} request", req.verb)
        response = await self.connection_manager.request(bytes(req))
        context_logger = context_logger.bind(response_bytes=response)
        try:
            parser = ResponseParser()
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
