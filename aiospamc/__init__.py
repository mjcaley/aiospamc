#!/usr/bin/env python3

'''aiospamc package.

An asyncio-based library to communicate with SpamAssassin's SPAMD service.'''

import asyncio
from typing import SupportsBytes, Union

from .client import Client
from .options import ActionOption, MessageClassOption
from .responses import Response


__all__ = ('Client',
           'MessageClassOption',
           'ActionOption')

__author__ = 'Michael Caley'
__copyright__ = 'Copyright 2016-2019 Michael Caley'
__license__ = 'MIT'
__version__ = '0.6.1'
__email__ = 'mjcaley@darkarctic.com'


async def check(
        message: Union[bytes, SupportsBytes],
        *,
        host: str = 'Localhost',
        port: int = 783,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs) -> Response:
    '''Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param loop: The asyncio event loop.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises TimeoutException: Timeout during connection.
    '''

    c = Client(host=host, port=port, **kwargs, loop=loop)
    response = await c.check(message)

    return response


async def headers(
        message: Union[bytes, SupportsBytes],
        *,
        host: str = 'Localhost',
        port: int = 783,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs) -> Response:
    '''Checks a message if it's spam and return the modified message headers.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param loop: The asyncio event loop.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client`
        instance.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.  The body contains the modified
        message headers, but not the content of the message.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises TimeoutException: Timeout during connection.
    '''

    c = Client(host=host, port=port, **kwargs, loop=loop)
    response = await c.headers(message)

    return response


async def ping(
        *,
        host: str = 'Localhost',
        port: int = 783,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs) -> Response:
    '''Sends a ping to the SPAMD service.

    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param loop: The asyncio event loop.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

    :return: A response with "PONG".

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises TimeoutException: Timeout during connection.
    '''

    c = Client(host=host, port=port, **kwargs, loop=loop)
    response = await c.ping()

    return response


async def process(
        message: Union[bytes, SupportsBytes],
        *,
        host: str = 'Localhost',
        port: int = 783,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs) -> Response:
    '''Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param loop: The asyncio event loop.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.  The body contains a modified
        copy of the message.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises TimeoutException: Timeout during connection.
    '''

    c = Client(host=host, port=port, **kwargs, loop=loop)
    response = await c.process(message)

    return response


async def report(
        message: Union[bytes, SupportsBytes],
        *,
        host: str = 'Localhost',
        port: int = 783,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs) -> Response:
    '''Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param loop: The asyncio event loop.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.  The body contains a report.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises TimeoutException: Timeout during connection.
    '''

    c = Client(host=host, port=port, **kwargs, loop=loop)
    response = await c.report(message)

    return response


async def report_if_spam(
        message: Union[bytes, SupportsBytes],
        *,
        host: str = 'Localhost',
        port: int = 783,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs) -> Response:
    '''Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param loop: The asyncio event loop.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.  The body contains a report if
        the message is considered spam.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises TimeoutException: Timeout during connection.
    '''

    c = Client(host=host, port=port, **kwargs, loop=loop)
    response = await c.report_if_spam(message)

    return response


async def symbols(message: Union[bytes, SupportsBytes],
                  *,
                  host: str = 'Localhost',
                  port: int = 783,
                  loop: asyncio.AbstractEventLoop = None,
                  **kwargs) -> Response:
    '''Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param loop: The asyncio event loop.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

    :return:
        A successful response with a "Spam" header showing if the message is
        considered spam as well as the score.  The body contains a
        comma-separated list of the symbols that were hit.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises TimeoutException: Timeout during connection.
    '''

    c = Client(host=host, port=port, **kwargs, loop=loop)
    response = await c.symbols(message)

    return response


async def tell(
        message: Union[bytes, SupportsBytes],
        message_class: Union[str, MessageClassOption],
        *,
        host: str = 'Localhost',
        port: int = 783,
        remove_action: Union[str, ActionOption] = None,
        set_action: Union[str, ActionOption] = None,
        loop: asyncio.AbstractEventLoop = None,
        **kwargs) -> Response:
    '''Checks a message if it's spam and return a response with a score header.

    :param message: Copy of the message.
    :param message_class: How to classify the message, either "ham" or "spam".
    :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
    :param port: Port number for the SPAMD service, defaults to 783.
    :param remove_action: Remove message class for message in database.
    :param set_action:
        Set message class for message in database.  Either `ham` or `spam`.
    :param loop: The asyncio event loop.
    :param kwargs:
        Additional options to pass to the :class:`aiospamc.client.Client` instance.

    :return:
        A successful response with "DidSet" and/or "DidRemove" headers along with the
        actions that were taken.

    :raises BadResponse: If the response from SPAMD is ill-formed this exception will be raised.
    :raises AIOSpamcConnectionFailed: Raised if an error occurred when trying to connect.
    :raises UsageException: Error in command line usage.
    :raises DataErrorException: Error with data format.
    :raises NoInputException: Cannot open input.
    :raises NoUserException: Addressee unknown.
    :raises NoHostException: Hostname unknown.
    :raises UnavailableException: Service unavailable.
    :raises InternalSoftwareException: Internal software error.
    :raises OSErrorException: System error.
    :raises OSFileException: Operating system file missing.
    :raises CantCreateException: Cannot create output file.
    :raises IOErrorException: Input/output error.
    :raises TemporaryFailureException: Temporary failure, may reattempt.
    :raises ProtocolException: Error in the protocol.
    :raises NoPermissionException: Permission denied.
    :raises ConfigException: Error in configuration.
    :raises TimeoutException: Timeout during connection.
    '''

    c = Client(host=host, port=port, **kwargs, loop=loop)
    response = await c.tell(
        message=message,
        message_class=message_class,
        remove_action=remove_action,
        set_action=set_action
    )

    return response
