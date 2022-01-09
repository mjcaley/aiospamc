#!/usr/bin/env python3

"""Collection of request and response header value objects."""

import getpass
from dataclasses import dataclass, asdict
from typing import Any, Dict

from .options import ActionOption, MessageClassOption


class HeaderValue:
    """Base class for header values."""

    def __bytes__(self) -> bytes:
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        """Converts the value to a dictionary."""

        return asdict(self)


@dataclass
class BytesHeaderValue(HeaderValue):
    """Header with bytes value.

    :param value: Value of the header.
    """

    value: bytes

    def __bytes__(self) -> bytes:
        return self.value


@dataclass
class GenericHeaderValue(HeaderValue):
    """Generic header value."""

    value: str
    encoding: str = "utf8"

    def __bytes__(self) -> bytes:
        return self.value.encode(self.encoding)


@dataclass
class CompressValue(HeaderValue):
    """Compress header.  Specifies what encryption scheme to use.  So far only
    'zlib' is supported.
    """

    algorithm: str = "zlib"

    def __bytes__(self) -> bytes:
        return self.algorithm.encode("ascii")


@dataclass
class ContentLengthValue(HeaderValue):
    """ContentLength header.  Indicates the length of the body in bytes."""

    length: int = 0

    def __int__(self) -> int:
        return self.length

    def __bytes__(self) -> bytes:
        return str(self.length).encode("ascii")


@dataclass
class MessageClassValue(HeaderValue):
    """MessageClass header.  Used to specify whether a message is 'spam' or
    'ham.'
    """

    value: MessageClassOption = MessageClassOption.ham

    def __bytes__(self) -> bytes:
        return self.value.name.encode("ascii")

    def to_dict(self) -> Dict[str, Any]:
        """Converts the value to a dictionary."""

        return {"value": self.value.value}


@dataclass
class SetOrRemoveValue(HeaderValue):
    """Base class for headers that implement "local" and "remote" rules."""

    action: ActionOption = ActionOption(local=False, remote=False)

    def __bytes__(self) -> bytes:
        if not self.action.local and not self.action.remote:
            # if nothing is set, then return a blank string so the request
            # doesn't get tainted
            return b""

        values = []
        if self.action.local:
            values.append(b"local")
        if self.action.remote:
            values.append(b"remote")

        return b", ".join(values)


@dataclass
class SpamValue(HeaderValue):
    """Spam header.  Used by the SPAMD service to report on if the submitted
    message was spam and the score/threshold that it used."""

    value: bool = False
    score: float = 0.0
    threshold: float = 0.0

    def __bool__(self) -> bool:
        return self.value

    def __bytes__(self) -> bytes:
        return b"%b ; %.1f / %.1f" % (
            str(self.value).encode("ascii"),
            self.score,
            self.threshold,
        )


@dataclass
class UserValue(HeaderValue):
    """User header.  Used to specify which user the SPAMD service should use
    when loading configuration files."""

    name: str = getpass.getuser()

    def __bytes__(self) -> bytes:
        return self.name.encode("ascii")

    def __str__(self) -> str:
        return self.name
