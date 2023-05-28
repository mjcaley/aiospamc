"""Collection of request and response header value objects."""

import getpass
from base64 import b64encode
from collections import UserDict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Protocol


class HeaderValue(Protocol):  # pragma: no cover
    """Protocol for headers."""

    def __bytes__(self) -> bytes:
        pass

    def to_json(self) -> Any:
        """Convert to a JSON object."""

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


class MessageClassOption(str, Enum):
    """Option to be used for the MessageClass header."""

    spam = "spam"
    ham = "ham"

    def __str__(self) -> str:
        return self.value


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

    local: bool = False
    remote: bool = False


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
    """Class to store headers with shortcut properties."""

    def get_header(self, name: str) -> Optional[str]:
        """Get a string header if it exists.

        :param name: Name of the header.
        :return: The header value.
        """

        if header := self.data.get(name):
            return header.value
        return None

    def set_header(self, name: str, value: str):
        """Sets a string header.

        :param name: Name of the header.
        :param value: Value of the header.
        """

        self.data[name] = GenericHeaderValue(value)

    def get_bytes_header(self, name: str) -> Optional[bytes]:
        """Get a bytes header if it exists.

        :param name: Name of the header.
        :return: The header value.
        """

        if header := self.data.get(name):
            return header.value
        return None

    def set_bytes_header(self, name: str, value: bytes):
        """Sets a string header.

        :param name: Name of the header.
        :param value: Value of the header.
        """

        self.data[name] = BytesHeaderValue(value)

    @property
    def compress(self) -> Optional[str]:
        """Gets the Compress header if it exists.

        :return: Compress header value.
        """

        if header := self.data.get("Compress"):
            return header.algorithm
        return None

    @compress.setter
    def compress(self, value: str = "zlib"):
        """Sets the Compress header.

        :param value: Value of the header.
        """

        self.data["Compress"] = CompressValue(value)

    @property
    def content_length(self) -> Optional[int]:
        """Gets the Content-length header if it exists.

        :return: Content-length header value.
        """

        if header := self.data.get("Content-length"):
            return header.length
        return None

    @content_length.setter
    def content_length(self, value: int):
        """Sets the Content-length header.

        :param value: Value of the header.
        """

        self.data["Content-length"] = ContentLengthValue(value)

    @property
    def message_class(self) -> Optional[MessageClassOption]:
        """Gets the Message-class header if it exists.

        :return: Message-class header value.
        """

        if header := self.data.get("Message-class"):
            return header.value
        return None

    @message_class.setter
    def message_class(self, value: MessageClassOption):
        """Sets the Message-class header.

        :param value: Value of the header.
        """

        self.data["Message-class"] = MessageClassValue(value)

    @property
    def set_(self) -> Optional[ActionOption]:
        """Gets the Set header if it exists.

        :return: Set header value.
        """

        if header := self.data.get("Set"):
            return header.action
        return None

    @set_.setter
    def set_(self, value: ActionOption):
        """Sets the Set header.

        :param value: Value of the header.
        """

        self.data["Set"] = SetOrRemoveValue(value)

    @property
    def remove(self) -> Optional[ActionOption]:
        """Gets the Remove header if it exists.

        :return: Remove header value.
        """

        if header := self.data.get("Remove"):
            return header.action
        return None

    @remove.setter
    def remove(self, value: ActionOption):
        """Sets the Remove header.

        :param value: Value of the header.
        """

        self.data["Remove"] = SetOrRemoveValue(value)

    @property
    def did_set(self) -> Optional[ActionOption]:
        """Gets the DidSet header if it exists.

        :return: DidSet header value.
        """

        if header := self.data.get("DidSet"):
            return header.action
        return None

    @did_set.setter
    def did_set(self, value: ActionOption):
        """Sets the DidSet header.

        :param value: Value of the header.
        """

        self.data["DidSet"] = SetOrRemoveValue(value)

    @property
    def did_remove(self) -> Optional[ActionOption]:
        """Gets the DidRemove header if it exists.

        :return: DidRemove header value.
        """

        if header := self.data.get("DidRemove"):
            return header.action
        return None

    @did_remove.setter
    def did_remove(self, value: ActionOption):
        """Sets the DidRemove header.

        :param value: Value of the header.
        """

        self.data["DidRemove"] = SetOrRemoveValue(value)

    @property
    def spam(self) -> Optional[SpamValue]:
        """Gets the Spam header if it exists.

        :return: Spam header value.
        """

        return self.data.get("Spam")

    @spam.setter
    def spam(self, value: SpamValue):
        """Sets the Spam header.

        :param value: Value of the header.
        """

        self.data["Spam"] = value

    @property
    def user(self) -> Optional[str]:
        """Gets the User header if it exists.

        :return: User header value.
        """

        if header := self.data.get("User"):
            return header.name
        return None

    @user.setter
    def user(self, value: str):
        """Sets the User header.

        :param value: Value of the header.
        """

        self.data["User"] = UserValue(value)
