"""Collection of exceptions."""


class ClientException(Exception):
    """Base class for exceptions raised from the client."""

    pass


class BadRequest(ClientException):
    """Request is not in the expected format."""

    pass


class BadResponse(ClientException):
    """Response is not in the expected format."""

    pass


class AIOSpamcConnectionFailed(ClientException):
    """Connection failed."""

    pass


class TimeoutException(Exception):
    """General timeout exception."""

    pass


class ClientTimeoutException(ClientException, TimeoutException):
    """Timeout exception from the client."""

    pass


class ParseError(Exception):
    """Error occurred while parsing."""

    def __init__(self, message=None):
        """Construct parsing exception with optional message.

        :param message: User friendly message.
        """

        self.message = message


class NotEnoughDataError(ParseError):
    """Expected more data than what the protocol content specified."""

    pass


class TooMuchDataError(ParseError):
    """Too much data was received than what the protocol content specified."""

    pass
