"""Collection of exceptions."""


class ClientException(Exception):
    """Base class for exceptions raised from the client."""


class BadRequest(ClientException):
    """Request is not in the expected format."""


class BadResponse(ClientException):
    """Response is not in the expected format."""


class AIOSpamcConnectionFailed(ClientException):
    """Connection failed."""


class TimeoutException(Exception):
    """General timeout exception."""


class ClientTimeoutException(ClientException, TimeoutException):
    """Timeout exception from the client."""


class ParseError(Exception):
    """Error occurred while parsing."""

    def __init__(self, message=None):
        """Construct parsing exception with optional message.

        :param message: User friendly message.
        """

        self.message = message


class NotEnoughDataError(ParseError):
    """Expected more data than what the protocol content specified."""


class TooMuchDataError(ParseError):
    """Too much data was received than what the protocol content specified."""
