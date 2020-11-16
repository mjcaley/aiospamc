#!/usr/bin/env python3

"""Contains classes used for responses."""

from enum import IntEnum
from typing import Any, Dict, SupportsBytes, Union
import zlib

from .exceptions import *
from .header_values import ContentLengthValue, HeaderValue


class Status(IntEnum):
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
        headers: Dict[str, HeaderValue] = None,
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
        self.headers = headers or {}
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

    def __str__(self):
        return (
            f"<{self.status_code} - "
            f"{self.message}: "
            f'{".".join([self.__class__.__module__, self.__class__.__qualname__])} '
            f"object at {id(self)}>"
        )

    def __eq__(self, other: Any) -> bool:
        return (
            self.version == other.version
            and self.headers == other.headers
            and self.status_code == other.status_code
            and self.message == other.message
            and self.body == other.body
        )

    @property
    def status_code(self) -> Union[Status, int]:
        return self._status_code

    @status_code.setter
    def status_code(self, code: Union[Status, int]) -> None:
        try:
            self._status_code = Status(code)
        except ValueError:
            self._status_code = code

    @property
    def body(self) -> bytes:
        return self._body

    @body.setter
    def body(self, value: Union[bytes, SupportsBytes]) -> None:
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
                raise status_exception[self.status_code](self.message)
            else:
                raise ResponseException(self.status_code, self.message)
