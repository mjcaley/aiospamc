"""Module for the parsing functions and objects."""

from __future__ import annotations

import re
from enum import Enum, auto
from typing import Any, Callable, Mapping, Union

import loguru
from loguru import logger

from .exceptions import NotEnoughDataError, ParseError, TooMuchDataError
from .header_values import (
    ActionOption,
    BytesHeaderValue,
    CompressValue,
    ContentLengthValue,
    GenericHeaderValue,
    MessageClassOption,
    MessageClassValue,
    SetOrRemoveValue,
    SpamValue,
    UserValue,
)


class States(Enum):
    """States for the parser state machine."""

    Status = auto()
    Header = auto()
    Body = auto()
    Done = auto()


class Parser:
    """The parser state machine.

    :ivar result: Storage location for parsing results."""

    def __init__(
        self,
        delimiter: bytes,
        status_parser: Callable[[bytes], Mapping[str, str]],
        header_parser: Callable[[bytes], tuple[str, Any]],
        body_parser: Callable[[bytes, int], bytes],
        start: States = States.Status,
    ) -> None:
        """Parser constructor.

        :param delimiter: Byte string to split the different sections of the message.
        :param status_parser: Callable to parse the status line of the message.
        :param header_parser: Callable to parse each header line of the message.
        :param body_parser: Callable to parse the body of the message.
        :param start: The state to start the parser on.  Allowed for easier testing.
        """

        self.delimiter = delimiter
        self.status_parser = status_parser
        self.header_parser = header_parser
        self.body_parser = body_parser
        self.result: dict[str, Any] = {"headers": {}, "body": b""}

        self._state = start
        self.buffer = b""

        self._logger = logger

    def _bind(self, **kwargs) -> loguru.Logger:
        """Helper method to bind a new logger.

        :return: A new logger instance.
        """

        self._logger = self._logger.bind(**kwargs)
        return self._logger

    @property
    def state(self) -> States:
        """The current state of the parser.

        :return: The :class:`States` instance.
        """

        return self._state

    def parse(self, stream: bytes) -> Mapping[str, Any]:
        """Entry method to parse a message.

        :param stream: Byte string to parse.

        :return: Returns the parser results dictionary stored in the class attribute :attr:`result`.

        :raises NotEnoughDataError: Raised when not enough data is sent to be parsed.
        :raises TooMuchDataError: Raised when too much data is sent to be parsed.
        :raises ParseError: Raised when a general parse error is found.
        """

        self.buffer += stream

        while self._state != States.Done:
            if self._state == States.Status:
                self.status()
            elif self._state == States.Header:
                self.header()
            elif self._state == States.Body:  # pragma: no branch
                self.body()

        return self.result

    def status(self) -> None:
        """Splits the message at the delimiter and sends the first part of the message to the :attr:`status_parser` callable to
        be parsed.  If successful then the results are stored in the :attr:`result` class attribute and the state
        transitions to :class:`States.Header`.

        :raises NotEnoughDataError: When there is no delimiter the message is incomplete.
        :raises ParseError: When the :attr:`status_parser` callable experiences an error.
        """

        status_line, delimiter, leftover = self.buffer.partition(self.delimiter)

        if status_line and delimiter:
            self.buffer = leftover
            parsed_status = self.status_parser(status_line)
            self.result = {**self.result, **parsed_status}
            self._state = States.Header
            self._bind(**parsed_status)
            self._logger.debug("Finished parsing status line")
        else:
            raise NotEnoughDataError

    def header(self) -> None:
        """Splits the message at the delimiter and sends the line to the :attr:`header_parser`.

        When splitting the action will be determined depending what is matched:

        +-------------+-----------+-----------+----------------------------------------------------------------------+
        | Header line | Delimiter | Leftover  | Action                                                               |
        +=============+===========+===========+======================================================================+
        |     No      |    Yes    | Delimiter | Headers done, empty body. Clear buffer and transition to             |
        |             |           |           | :class:`States.Body`.                                                |
        +-------------+-----------+-----------+----------------------------------------------------------------------+
        |     No      |    Yes    |    N/A    | Headers done.  Transition to :class:`States.Body`.                   |
        +-------------+-----------+-----------+----------------------------------------------------------------------+
        |     Yes     |    Yes    |    N/A    | Parse header.  Record in :attr:`result` class attribute.             |
        +-------------+-----------+-----------+----------------------------------------------------------------------+
        |     No      |    No     |    No     | Message was a status line only.  Transition to :class:`States.Body`. |
        +-------------+-----------+-----------+----------------------------------------------------------------------+

        :raises ParseError: None of the previous conditions are matched.
        """

        header_line, delimiter, leftover = self.buffer.partition(self.delimiter)

        if self._at_end_of_headers_with_empty_body(header_line, delimiter, leftover):
            self.buffer = b""
            self._state = States.Body
            self._bind(headers=self.result["headers"])
            self._logger.debug("Finished parsing headers")
        elif self._at_end_of_headers(header_line, delimiter):
            self.buffer = leftover
            self._state = States.Body
            self._bind(headers=self.result["headers"])
            self._logger.debug("Finished parsing headers")
        elif self._at_next_header(header_line, delimiter):
            self.buffer = leftover
            key, value = self.header_parser(header_line)
            self.result["headers"][key] = value
            self._logger.debug("Parsed header {}", key)
        elif self._is_status_line_only(header_line, delimiter, leftover):
            self._state = States.Body
            self._logger.debug("No headers to parse")
        else:
            raise ParseError("Header section not in recognizable format")

    def _at_end_of_headers_with_empty_body(
        self, header_line: bytes, delimiter: bytes, leftover: bytes
    ) -> bool:
        """Helper method to check if the header sections is done and there is an empty body.

        :param header_line: Contents of the header line.
        :param delimiter: Separator between the header line and the rest of the response.
        :param leftover: Remaining response contents.

        :return: If the header section is finished, and there is no remaining content for a body.
        """

        return all([not header_line, delimiter, leftover == self.delimiter])

    @staticmethod
    def _at_end_of_headers(header_line: bytes, delimiter: bytes) -> bool:
        """Helper method to check if the parser is at the end of the header section.

        :param header_line: Contents of the header line.
        :param delimiter: Separator between the header line and the rest of the response.

        :return: If the header section is finished and there is a delimiter.
        """

        return all([not header_line, delimiter])

    @staticmethod
    def _at_next_header(header_line: bytes, delimiter: bytes) -> bool:
        """Helper method to check if a header can be parsed.

        :param header_line: Contents of the header line.
        :param delimiter: Separator between the header line and the rest of the response.

        :return: If the header line is finished, and there is another header.
        """

        return all([header_line, delimiter])

    @staticmethod
    def _is_status_line_only(
        header_line: bytes, delimiter: bytes, leftover: bytes
    ) -> bool:
        """Helper method to check if the response is a status line only, without a header section.

        :param header_line: Contents of the header line.
        :param delimiter: Separator between the header line and the rest of the response.
        :param leftover: Remaining response contents.

        :return: If the response was a status line only without a header section or body.
        """

        return all([not header_line, not delimiter, not leftover])

    def body(self) -> None:
        """Uses the length defined in the `Content-length` header (defaulted to 0) to determine how many bytes the body
        contains.

        :raises TooMuchDataError:
            When there are too many bytes in the buffer compared to the `Content-length` header value.  Transitions the
            state to :class:`States.Done`.
        """

        content_length = (
            self.result["headers"]
            .get("Content-length", ContentLengthValue(length=0))
            .length
        )
        try:
            self.result["body"] += self.body_parser(self.buffer, content_length)
            self._state = States.Done
            self._logger.debug("Finished parsing body")
        except TooMuchDataError:
            self._state = States.Done
            self._logger.error("Body parsed was larger than the content length")
            raise


def parse_request_status(stream: bytes) -> dict[str, str]:
    """Parses the status line from a request.

    :param stream: The byte stream to parse.

    :return: A dictionary with the keys `verb`, `protocol` and `version`.

    :raises ParseError:
        When the status line is in an invalid format, not a valid verb, or doesn't have the correct protocol.
    """

    try:
        verb, protocol_version = stream.decode("ascii").split(" ")
        protocol, version = protocol_version.split("/")
    except ValueError as error:
        raise ParseError(
            "Could not parse request status line, not in recognizable format"
        ) from error

    if verb not in [
        "CHECK",
        "HEADERS",
        "PING",
        "PROCESS",
        "REPORT_IFSPAM",
        "REPORT",
        "SKIP",
        "SYMBOLS",
        "TELL",
    ]:
        raise ParseError("Not a valid verb")

    if protocol != "SPAMC":
        raise ParseError("Protocol name does not match")

    return {"verb": verb, "protocol": protocol, "version": version}


def parse_response_status(stream: bytes) -> dict[str, Union[str, int]]:
    """Parse the status line for a response.

    :param stream: The byte stream to parse.

    :return: A dictionary with the keys `protocol`, `version`, `status_code`, and `message`.

    :raises ParseError:
        When the status line is in an invalid format, status code is not an integer, or doesn't have the correct
        protocol.
    """

    try:
        protocol_version, status_code, message = list(
            filter(None, stream.decode("ascii").split(" ", 2))
        )
        protocol, version = protocol_version.split("/")
    except ValueError as error:
        raise ParseError(
            "Could not parse response status line, not in recognizable format"
        ) from error

    if protocol != "SPAMD":
        raise ParseError("Protocol name does not match")

    try:
        status_code_int = int(status_code)
    except ValueError as error:
        raise ParseError("Protocol status code is not an integer") from error

    return {
        "protocol": protocol,
        "version": version,
        "status_code": status_code_int,
        "message": message,
    }


def parse_message_class_value(
    stream: Union[str, MessageClassOption]
) -> MessageClassValue:
    """Parses the `Message-class` header value.

    :param stream: String or :class:`aiospamc.header_values.MessageClassOption` instance.

    :return: A :class:`aiospamc.header_values.MessageClassValue` instance representing the value.

    :raises ParseError: When the value doesn't match either `ham` or `spam`.
    """

    value: MessageClassOption
    if isinstance(stream, MessageClassOption):
        value = stream
    else:
        try:
            value = getattr(MessageClassOption, stream.strip())
        except AttributeError as error:
            raise ParseError("Unable to parse Message-class header value") from error

    return MessageClassValue(value=value)


def parse_content_length_value(stream: Union[str, int]) -> ContentLengthValue:
    """Parses the `Content-length` header value.

    :param stream: String or integer value of the header.

    :return: A :class:`aiospamc.header_values.ContentLengthValue` instance.

    :raises ParseError: When the value cannot be cast to an integer.
    """

    try:
        value = int(stream)
    except ValueError as error:
        raise ParseError(
            "Unable to parse Content-length value, must be integer"
        ) from error

    return ContentLengthValue(length=value)


def parse_compress_value(stream: str) -> CompressValue:
    """Parses a value for the `Compress` header.

    :param stream: String to parse.

    :return: A :class:`aiospamc.header_values.CompressValue` instance.
    """

    return CompressValue(algorithm=stream.strip())


def parse_set_remove_value(stream: Union[ActionOption, str]) -> SetOrRemoveValue:
    """Parse a value for the :class:`aiospamc.header_values.DidRemove`, :class:`aiospamc.header_values.DidSet`, :class:`aiospamc.header_values.Remove`, and :class:`aiospamc.header_values.Set` headers.

    :param stream: String to parse or an instance of :class:`aiospamc.header_values.ActionOption`.

    :return: A :class:`aiospamc.header_values.SetOrRemoveValue` instance.
    """

    if isinstance(stream, ActionOption):
        value = stream
    else:
        stream = stream.replace(" ", "")
        values = stream.split(",")

        if "local" in values:
            local = True
        else:
            local = False

        if "remote" in values:
            remote = True
        else:
            remote = False

        value = ActionOption(local=local, remote=remote)

    return SetOrRemoveValue(action=value)


def parse_spam_value(stream: str) -> SpamValue:
    """Parses the values for the `Spam` header.

    :param stream: String to parse.

    :return: A :class:`aiospamc.header_values.SpamValue` instance.

    :raises ParseError: Raised if there is no true/false value, or valid numbers for the score or threshold.
    """

    stream = stream.replace(" ", "")
    try:
        found, score, threshold = re.split("[;/]", stream)
    except ValueError as error:
        raise ParseError("Spam header in unrecognizable format") from error

    found = found.lower()
    if found in ["true", "yes"]:
        value = True
    elif found in ["false", "no"]:
        value = False
    else:
        raise ParseError("Spam header is not a true or false value")

    try:
        parsed_score = float(score)
    except ValueError as error:
        raise ParseError("Cannot parse Spam header score value") from error

    try:
        parsed_threshold = float(threshold)
    except ValueError as error:
        raise ParseError("Cannot parse Spam header threshold value") from error

    return SpamValue(value=value, score=parsed_score, threshold=parsed_threshold)


def parse_user_value(stream: str) -> UserValue:
    """Parse the username.

    :param stream: String of username to parse. Whitespace is trimmed.

    :return: The :class:`aiospamc.header_values.UserValue` instance.
    """

    return UserValue(name=stream.strip())


def parse_header_value(header: str, value: Union[str, bytes]) -> Any:
    """Sends the header value stream to the header value parsing function.

    :param header: Name of the header.
    :param value: String or byte stream of the header value.

    :return: The :class:`aiospamc.header_values.HeaderValue` instance from the parsing function.
    """

    if header in header_value_parsers:
        if isinstance(value, bytes):
            try:
                return header_value_parsers[header](value.decode())
            except UnicodeDecodeError as error:
                raise ParseError(message="Unable to decode header value") from error
        else:
            return header_value_parsers[header](value)
    else:
        if isinstance(value, bytes):
            try:
                return GenericHeaderValue(value.decode())
            except UnicodeDecodeError:
                return BytesHeaderValue(value)
        else:
            return GenericHeaderValue(value)


def parse_header(stream: bytes) -> tuple[str, Any]:
    """Splits the header line and sends to the header parsing function.

    :param stream: Byte stream of the header line.

    :return: A tuple of the header name and value.
    """

    header, _, value = stream.partition(b":")
    parsed_header = header.decode("ascii").strip()
    parsed_value = parse_header_value(parsed_header, value)

    return parsed_header, parsed_value


def parse_body(stream: bytes, content_length: int) -> bytes:
    """Parses the body of a message.

    :param stream: Byte stream for the body.
    :param content_length: Expected length of the body in bytes.

    :return: Byte stream of the body.

    :raises NotEnoughDataError: If the length is less than the stream.
    :raises TooMuchDataError: If the length is more than the stream.
    """

    if len(stream) == content_length:
        return stream
    elif len(stream) < content_length:
        raise NotEnoughDataError
    else:
        raise TooMuchDataError


header_value_parsers = {
    "Compress": parse_compress_value,
    "Content-length": parse_content_length_value,
    "DidRemove": parse_set_remove_value,
    "DidSet": parse_set_remove_value,
    "Message-class": parse_message_class_value,
    "Remove": parse_set_remove_value,
    "Set": parse_set_remove_value,
    "Spam": parse_spam_value,
    "User": parse_user_value,
}
"""Mapping for header names to their parsing functions."""


class RequestParser(Parser):
    """Sub-class of the parser for requests."""

    def __init__(self):
        """RequestParse constructor."""

        super().__init__(
            delimiter=b"\r\n",
            status_parser=parse_request_status,
            header_parser=parse_header,
            body_parser=parse_body,
        )


class ResponseParser(Parser):
    """Sub-class of the parser for responses."""

    def __init__(self):
        """ResponseParser constructor."""

        super().__init__(
            delimiter=b"\r\n",
            status_parser=parse_response_status,
            header_parser=parse_header,
            body_parser=parse_body,
        )
