#!/usr/bin/env python3

"""Collection of exceptions."""


# Exceptions raised from the Client object
class ClientException(Exception):
    """Base class for exceptions raised from the client."""

    pass


class BadRequest(ClientException):
    """Request is not in the expected format."""

    pass


class BadResponse(ClientException):
    """Response is not in the expected format."""

    pass


# ConnectionManager and Connection object exceptions
class AIOSpamcConnectionException(Exception):
    """Base class for exceptions from the connection."""

    pass


class AIOSpamcConnectionFailed(AIOSpamcConnectionException):
    """Connection failed."""

    pass


class ResponseException(Exception):
    """Base class for exceptions raised from a response."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        super().__init__(message)


class UsageException(ResponseException):
    """Command line usage error."""

    def __init__(self, message: str) -> None:
        super().__init__(64, message)


class DataErrorException(ResponseException):
    """Data format error."""

    def __init__(self, message: str) -> None:
        super().__init__(65, message)


class NoInputException(ResponseException):
    """Cannot open input."""

    def __init__(self, message: str) -> None:
        super().__init__(66, message)


class NoUserException(ResponseException):
    """Addressee unknown."""

    def __init__(self, message: str) -> None:
        super().__init__(67, message)


class NoHostException(ResponseException):
    """Hostname unknown."""

    def __init__(self, message: str) -> None:
        super().__init__(68, message)


class UnavailableException(ResponseException):
    """Service unavailable."""

    def __init__(self, message: str) -> None:
        super().__init__(69, message)


class InternalSoftwareException(ResponseException):
    """Internal software error."""

    def __init__(self, message: str) -> None:
        super().__init__(70, message)


class OSErrorException(ResponseException):
    """System error (e.g. can't fork the process)."""

    def __init__(self, message: str) -> None:
        super().__init__(71, message)


class OSFileException(ResponseException):
    """Critical operating system file missing."""

    def __init__(self, message: str) -> None:
        super().__init__(72, message)


class CantCreateException(ResponseException):
    """Can't create (user) output file."""

    def __init__(self, message: str) -> None:
        super().__init__(73, message)


class IOErrorException(ResponseException):
    """Input/output error."""

    def __init__(self, message: str) -> None:
        super().__init__(74, message)


class TemporaryFailureException(ResponseException):
    """Temporary failure, user is invited to try again."""

    def __init__(self, message: str) -> None:
        super().__init__(75, message)


class ProtocolException(ResponseException):
    """Remote error in protocol."""

    def __init__(self, message: str) -> None:
        super().__init__(76, message)


class NoPermissionException(ResponseException):
    """Permission denied."""

    def __init__(self, message: str) -> None:
        super().__init__(77, message)


class ConfigException(ResponseException):
    """Configuration error."""

    def __init__(self, message: str) -> None:
        super().__init__(78, message)


class TimeoutException(ResponseException):
    """Read timeout."""

    def __init__(self, message: str) -> None:
        super().__init__(79, message)
