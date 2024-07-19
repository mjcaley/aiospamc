"""Contains classes used for responses."""

from __future__ import annotations

import zlib
from base64 import b64encode
from enum import IntEnum
from typing import Any, SupportsBytes, Union

from .exceptions import TimeoutException
from .header_values import ContentLengthValue, Headers


class Status(IntEnum):
    """Enumeration for the status values defined by SPAMD."""

    EX_OK = 0
    EX_USAGE = 64
    EX_DATAERR = 65
    EX_NOINPUT = 66
    EX_NOUSER = 67
    EX_NOHOST = 68
    EX_UNAVAILABLE = 69
    EX_SOFTWARE = 70
    EX_OSERR = 71
    EX_OSFILE = 72
    EX_CANTCREAT = 73
    EX_IOERR = 74
    EX_TEMPFAIL = 75
    EX_PROTOCOL = 76
    EX_NOPERM = 77
    EX_CONFIG = 78
    EX_TIMEOUT = 79


class Response:
    """Class to encapsulate response."""

    def __init__(
        self,
        version: str = "1.5",
        status_code: Union[Status, int] = 0,
        message: str = "",
        headers: Union[dict[str, Any], Headers, None] = None,
        body: bytes = b"",
        **_,
    ):
        """Response constructor.

        :param version: Version reported by the SPAMD service response.
        :param status_code: Success or error code.
        :param message: Message associated with status code.
        :param body: Byte string representation of the body.
        :param headers: Collection of headers to be added.
        """

        self.version = version
        if isinstance(headers, dict):
            self.headers = Headers(headers)
        elif isinstance(headers, Headers):
            self.headers = headers
        else:
            self.headers = Headers()
        self._status_code: Union[Status, int]
        self.status_code = status_code
        self.message = message
        self.body = body

    def __bytes__(self) -> bytes:
        if "Compress" in self.headers:
            body = zlib.compress(self.body)
        else:
            body = self.body

        if len(body) > 0:
            self.headers["Content-length"] = ContentLengthValue(length=len(body))

        status = self.status_code
        encoded_headers = b"".join(
            [
                b"%b: %b\r\n" % (key.encode("ascii"), bytes(value))
                for key, value in self.headers.items()
            ]
        )
        message = self.message.encode("ascii")

        return (
            b"SPAMD/%(version)b "
            b"%(status)d "
            b"%(message)b\r\n"
            b"%(headers)b\r\n"
            b"%(body)b"
            % {
                b"version": self.version.encode("ascii"),
                b"status": status,
                b"message": message,
                b"headers": encoded_headers,
                b"body": body,
            }
        )

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__module__}.{self.__class__.__qualname__} "
            f"[{self.message}] "
            f"object at {hex(id(self))}>"
        )

    def __eq__(self, other: Any) -> bool:
        try:
            return (
                self.version == other.version
                and self.headers == other.headers
                and self.status_code == other.status_code
                and self.message == other.message
                and self.body == other.body
            )
        except AttributeError:
            return False

    @property
    def status_code(self) -> Union[Status, int]:
        """Status code property getter.

        :return: Value of status code.
        """

        return self._status_code

    @status_code.setter
    def status_code(self, code: Union[Status, int]) -> None:
        """Status code property setter.

        :param code: Status code value to set.
        """

        try:
            self._status_code = Status(code)
        except ValueError:
            self._status_code = code

    @property
    def body(self) -> bytes:
        """Body property getter.

        :return: Value of body.
        """

        return self._body

    @body.setter
    def body(self, value: Union[bytes, SupportsBytes]) -> None:
        """Body property setter.

        :param value: Value to set the body.
        """

        self._body = bytes(value)

    def raise_for_status(self) -> None:
        """Raises an exception if the status code isn't zero.

        :raises ResponseException:
        :raises UsageException:
        :raises DataErrorException:
        :raises NoInputException:
        :raises NoUserException:
        :raises NoHostException:
        :raises UnavailableException:
        :raises InternalSoftwareException:
        :raises OSErrorException:
        :raises OSFileException:
        :raises CantCreateException:
        :raises IOErrorException:
        :raises TemporaryFailureException:
        :raises ProtocolException:
        :raises NoPermissionException:
        :raises ConfigException:
        :raises ServerTimeoutException:
        """

        if self.status_code == 0:
            return
        else:
            status_exception = {
                64: UsageException,
                65: DataErrorException,
                66: NoInputException,
                67: NoUserException,
                68: NoHostException,
                69: UnavailableException,
                70: InternalSoftwareException,
                71: OSErrorException,
                72: OSFileException,
                73: CantCreateException,
                74: IOErrorException,
                75: TemporaryFailureException,
                76: ProtocolException,
                77: NoPermissionException,
                78: ConfigException,
                79: ServerTimeoutException,
            }
            if self.status_code in status_exception:
                raise status_exception[self.status_code](self.message, self)
            else:
                raise ResponseException(self.status_code, self.message, self)

    def to_json(self) -> dict[str, Any]:
        """Converts to JSON serializable object."""

        return {
            "version": self.version,
            "status_code": int(self.status_code),
            "message": self.message,
            "headers": {key: value.to_json() for key, value in self.headers.items()},
            "body": b64encode(self.body).decode(),
        }


class ResponseException(Exception):
    """Base class for exceptions raised from a response."""

    def __init__(self, code: int, message: str, response: Response):
        """ResponseException constructor.

        :param code: Response code number.
        :param message: Message response.
        """

        self.code = code
        self.response = response
        super().__init__(message)


class UsageException(ResponseException):
    """Command line usage error."""

    def __init__(self, message: str, response: Response):
        """UsageException constructor.

        :param message: Message response.
        """

        super().__init__(64, message, response)


class DataErrorException(ResponseException):
    """Data format error."""

    def __init__(self, message: str, response: Response):
        """DataErrorException constructor.

        :param message: Message response.
        """

        super().__init__(65, message, response)


class NoInputException(ResponseException):
    """Cannot open input."""

    def __init__(self, message: str, response: Response):
        """NoInputException constructor.

        :param message: Message response.
        """

        super().__init__(66, message, response)


class NoUserException(ResponseException):
    """Addressee unknown."""

    def __init__(self, message: str, response: Response):
        """NoUserException constructor.

        :param message: Message response.
        """

        super().__init__(67, message, response)


class NoHostException(ResponseException):
    """Hostname unknown."""

    def __init__(self, message: str, response: Response):
        """NoHostException constructor.

        :param message: Message response.
        """

        super().__init__(68, message, response)


class UnavailableException(ResponseException):
    """Service unavailable."""

    def __init__(self, message: str, response: Response):
        """UnavailableException constructor.

        :param message: Message response.
        """

        super().__init__(69, message, response)


class InternalSoftwareException(ResponseException):
    """Internal software error."""

    def __init__(self, message: str, response: Response):
        """InternalSoftwareException constructor.

        :param message: Message response.
        """

        super().__init__(70, message, response)


class OSErrorException(ResponseException):
    """System error (e.g. can't fork the process)."""

    def __init__(self, message: str, response: Response):
        """OSErrorException constructor.

        :param message: Message response.
        """

        super().__init__(71, message, response)


class OSFileException(ResponseException):
    """Critical operating system file missing."""

    def __init__(self, message: str, response: Response):
        """OSFileException constructor.

        :param message: Message response.
        """

        super().__init__(72, message, response)


class CantCreateException(ResponseException):
    """Can't create (user) output file."""

    def __init__(self, message: str, response: Response):
        """CantCreateException constructor.

        :param message: Message response.
        """

        super().__init__(73, message, response)


class IOErrorException(ResponseException):
    """Input/output error."""

    def __init__(self, message: str, response: Response):
        """IOErrorException constructor.

        :param message: Message response.
        """

        super().__init__(74, message, response)


class TemporaryFailureException(ResponseException):
    """Temporary failure, user is invited to try again."""

    def __init__(self, message: str, response: Response):
        """TemporaryFailureException constructor.

        :param message: Message response.
        """

        super().__init__(75, message, response)


class ProtocolException(ResponseException):
    """Remote error in protocol."""

    def __init__(self, message: str, response: Response):
        """ProtocolException constructor.

        :param message: Message response.
        """

        super().__init__(76, message, response)


class NoPermissionException(ResponseException):
    """Permission denied."""

    def __init__(self, message: str, response: Response):
        """NoPermissionException constructor.

        :param message: Message response.
        """

        super().__init__(77, message, response)


class ConfigException(ResponseException):
    """Configuration error."""

    def __init__(self, message: str, response: Response):
        """ConfigException constructor.

        :param message: Message response.
        """

        super().__init__(78, message, response)


class ServerTimeoutException(ResponseException, TimeoutException):
    """Timeout exception from the server."""

    def __init__(self, message: str, response: Response):
        """ServerTimeoutException constructor.

        :param message: Message response.
        """

        super().__init__(79, message, response)
