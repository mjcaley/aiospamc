#!/usr/bin/env python3

"""Collection of request and response header value objects."""

import getpass
from base64 import b64encode
from collections import UserDict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Protocol


class HeaderValue(Protocol):  # pragma: no cover
    def __bytes__(self) -> bytes:
        pass

    def to_json(self) -> Any:
        pass


@dataclass
class BytesHeaderValue:
    """Header with bytes value.

    :param value: Value of the header.
    """

    value: bytes

    def __bytes__(self) -> bytes:
        return self.value

    def to_json(self) -> Any:
        """Converts object to a JSON serializable object."""

        return b64encode(self.value).decode()


@dataclass
class GenericHeaderValue:
    """Generic header value."""

    value: str
    encoding: str = "utf8"

    def __bytes__(self) -> bytes:
        return self.value.encode(self.encoding)

    def to_json(self) -> Any:
        """Converts object to a JSON serializable object."""

        return self.value


@dataclass
class CompressValue:
    """Compress header.  Specifies what encryption scheme to use.  So far only
    'zlib' is supported.
    """

    algorithm: str = "zlib"

    def __bytes__(self) -> bytes:
        return self.algorithm.encode("ascii")

    def to_json(self) -> Any:
        """Converts object to a JSON serializable object."""

        return self.algorithm


@dataclass
class ContentLengthValue:
    """ContentLength header.  Indicates the length of the body in bytes."""

    length: int = 0

    def __int__(self) -> int:
        return self.length

    def __bytes__(self) -> bytes:
        return str(self.length).encode("ascii")

    def to_json(self) -> Any:
        """Converts object to a JSON serializable object."""

        return self.length


class MessageClassOption(Enum):
    """Option to be used for the MessageClass header."""

    spam = "spam"
    ham = "ham"


@dataclass
class MessageClassValue:
    """MessageClass header.  Used to specify whether a message is 'spam' or
    'ham.'
    """

    value: MessageClassOption = MessageClassOption.ham

    def __bytes__(self) -> bytes:
        return self.value.name.encode("ascii")

    def to_json(self) -> Any:
        """Converts object to a JSON serializable object."""

        return self.value.value


@dataclass
class ActionOption:
    """Option to be used in the DidRemove, DidSet, Set, and Remove headers.

    :param local: An action will be performed on the SPAMD service's local database.
    :param remote: An action will be performed on the SPAMD service's remote database.
    """

    local: Optional[bool]
    remote: Optional[bool]


@dataclass
class SetOrRemoveValue:
    """Base class for headers that implement "local" and "remote" rules."""

    action: ActionOption

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

    def to_json(self) -> Any:
        """Converts object to a JSON serializable object."""

        return {"local": self.action.local, "remote": self.action.remote}


@dataclass
class SpamValue:
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

    def to_json(self) -> Any:
        """Converts object to a JSON serializable object."""

        return {"value": self.value, "score": self.score, "threshold": self.threshold}


@dataclass
class UserValue:
    """User header.  Used to specify which user the SPAMD service should use
    when loading configuration files."""

    name: str = getpass.getuser()

    def __bytes__(self) -> bytes:
        return self.name.encode("ascii")

    def __str__(self) -> str:
        return self.name

    def to_json(self) -> Any:
        """Converts object to a JSON serializable object."""

        return self.name


class Headers(UserDict):
    def get_header(self, name: str) -> Optional[GenericHeaderValue]:
        return self.data.get(name)

    def set_header(self, name: str, value: GenericHeaderValue):
        self.data[name] = value

    def get_bytes_header(self, name: str) -> Optional[BytesHeaderValue]:
        return self.data.get(name)

    def set_bytes_header(self, name: str, value: BytesHeaderValue):
        self.data[name] = value

    @property
    def compress(self) -> Optional[CompressValue]:
        return self.data.get("Compress")

    @compress.setter
    def compress(self, value: CompressValue):
        self.data["Compress"] = value

    @property
    def content_length(self) -> Optional[ContentLengthValue]:
        return self.data.get("Content-length")

    @content_length.setter
    def content_length(self, value: ContentLengthValue):
        self.data["Content-length"] = value

    @property
    def message_class(self) -> Optional[MessageClassValue]:
        return self.data.get("Message-class")

    @message_class.setter
    def message_class(self, value: MessageClassValue):
        self.data["Message-class"] = value

    @property
    def set_(self) -> Optional[SetOrRemoveValue]:
        return self.data.get("Set")

    @set_.setter
    def set_(self, value: SetOrRemoveValue):
        self.data["Set"] = value

    @property
    def remove(self) -> Optional[SetOrRemoveValue]:
        return self.data.get("Remove")

    @remove.setter
    def remove(self, value: SetOrRemoveValue):
        self.data["Remove"] = value

    @property
    def did_set(self) -> Optional[SetOrRemoveValue]:
        return self.data.get("DidSet")

    @did_set.setter
    def did_set(self, value: SetOrRemoveValue):
        self.data["DidSet"] = value

    @property
    def did_remove(self) -> Optional[SetOrRemoveValue]:
        return self.data.get("DidRemove")

    @did_remove.setter
    def did_remove(self, value: SetOrRemoveValue):
        self.data["DidRemove"] = value

    @property
    def spam(self) -> Optional[SpamValue]:
        return self.data.get("Spam")

    @spam.setter
    def spam(self, value: SpamValue):
        self.data["Spam"] = value

    @property
    def user(self) -> Optional[UserValue]:
        return self.data.get("User")

    @user.setter
    def user(self, value: UserValue):
        self.data["User"] = value
