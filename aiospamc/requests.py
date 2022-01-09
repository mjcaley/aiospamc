#!/usr/bin/env python3

"""Contains all requests that can be made to the SPAMD service."""

from typing import Any, Dict, SupportsBytes, Union
import zlib

from .header_values import ContentLengthValue, HeaderValue


class Request:
    """SPAMC request object."""

    def __init__(
        self,
        verb: str,
        version: str = "1.5",
        headers: Dict[str, HeaderValue] = None,
        body: Union[bytes, SupportsBytes] = b"",
        **_,
    ) -> None:
        """Request constructor.

        :param verb: Method name of the request.
        :param version: Version of the protocol.
        :param headers: Collection of headers to be added.
        :param body: Byte string representation of the body.
        """

        self.verb = verb
        self.version = version
        self.headers = headers or {}
        self.body = bytes(body)

    def __bytes__(self) -> bytes:
        if "Compress" in self.headers.keys():
            body = zlib.compress(self.body)
        else:
            body = self.body

        if len(body) > 0:
            self.headers["Content-length"] = ContentLengthValue(length=len(body))

        encoded_headers = b"".join(
            [
                b"%b: %b\r\n" % (key.encode("ascii"), bytes(value))
                for key, value in self.headers.items()
            ]
        )

        request = (
            b"%(verb)b " b"SPAMC/%(version)b" b"\r\n" b"%(headers)b\r\n" b"%(body)b"
        )

        return request % {
            b"verb": self.verb.encode("ascii"),
            b"version": self.version.encode("ascii"),
            b"headers": encoded_headers,
            b"body": body,
        }

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__module__}.{self.__class__.__qualname__} "
            f"[{self.verb}] "
            f"object at {hex(id(self))}>"
        )

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

    def to_dict(self) -> Dict[str, Any]:
        """Converts the request to a dictionary."""

        request_dict = {
            "verb": self.verb,
            "version": self.version,
            "headers": {key: value.to_dict() for key, value in self.headers.items()},
            "body": self.body,
        }

        return request_dict
