#!/usr/bin/env python3

'''Contains the Client class that is used to interact with SPAMD.'''

import asyncio
import logging
from typing import SupportsBytes, Union

from .options import MessageClassOption, ActionOption
from .exceptions import BadResponse, ResponseException
from .headers import Compress, MessageClass, Remove, Set, User
from .parser import parse, ParseError
from .requests import Request
from .responses import Response


class Client:
    '''Client object for interacting with SPAMD.'''

    def __init__(self,
                 socket_path: str = '/var/run/spamassassin/spamd.sock',
                 host: str = None,
                 port: int = 783,
                 user: str = None,
                 compress: bool = False,
                 ssl: bool = False,
                 loop: asyncio.AbstractEventLoop = None) -> None:
        '''Client constructor.

        :param socket_path: The path to the Unix socket for the SPAMD service.
        :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
        :param port: Port number for the SPAMD service, defaults to 783.
        :param user: Name of the user that SPAMD will run the checks under.
        :param compress: If true, the request body will be compressed.
        :param ssl: If true, will enable SSL/TLS for the connection.
        :param loop: The asyncio event loop.

        :raises ValueError: Raised if the constructor can't tell if it's using a TCP or a Unix domain socket connection.
        '''

        if host and port:
            from aiospamc.connections.tcp_connection import TcpConnectionManager
            self.connection = TcpConnectionManager(host, port)
        elif socket_path:
            from aiospamc.connections.unix_connection import UnixConnectionManager
            self.connection = UnixConnectionManager(socket_path)
        else:
            raise ValueError('Either "host" and "port" or "socket_path" must be specified.')

        self._host = host
        self._port = port
        self._socket_path = socket_path
        self.user = user
        self.compress = compress
        self._ssl = ssl
        self.loop = loop or asyncio.get_event_loop()

        self.parser = parse

        self.logger = logging.getLogger(__name__)
        self.logger.debug('Created instance of %r', self)

    def __repr__(self) -> str:
        client_fmt = ('{}(socket_path={}, '
                      'host={}, '
                      'port={}, '
                      'user={}, '
                      'compress={}, '
                      'ssl={})')
        return client_fmt.format(self.__class__.__name__,
                                 repr(self._socket_path),
                                 repr(self._host),
                                 repr(self._port),
                                 repr(self.user),
                                 repr(self.compress),
                                 repr(self._ssl))

    async def send(self, request: Request) -> Response:
        '''Sends a request to the SPAMD service.

        If the SPAMD service gives a temporary failure response, then its retried.

        :param request: Request object to send.

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

        if self.compress:
            request.headers['Compress'] = Compress()
        if self.user:
            request.headers['User'] = User(name=self.user)

        self.logger.debug('Sending request (%s)', id(request))
        async with self.connection.new_connection() as connection:
            await connection.send(bytes(request))
            self.logger.debug('Request (%s) successfully sent', id(request))
            data = await connection.receive()

        try:
            try:
                response = self.parser(data)
            except ParseError:
                raise BadResponse
            response.raise_for_status()
        except ResponseException as error:
            self.logger.exception('Exception for request (%s)when composing response: %s',
                                  id(request),
                                  error)
            raise

        self.logger.debug('Received response (%s) for request (%s)',
                          id(response),
                          id(request))
        return response

    async def check(self, message: Union[bytes, SupportsBytes]) -> Response:
        '''Request the SPAMD service to check a message with a HEADERS request.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        :return: The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

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

        request = Request('CHECK', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def headers(self, message: Union[bytes, SupportsBytes]) -> Response:
        '''Request the SPAMD service to check a message with a HEADERS request.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        :return: The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain the modified headers of the message.

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

        request = Request('HEADERS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def ping(self) -> Response:
        '''Sends a ping request to the SPAMD service and will receive a
        response if the service is alive.

        :return: Response message will contain 'PONG' if successful.

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

        request = Request('PING')
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def process(self, message: Union[bytes, SupportsBytes]) -> Response:
        '''Request the SPAMD service to check a message with a HEADERS request.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        :return: The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a modified version of the message.

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

        request = Request('PROCESS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def report(self, message: Union[bytes, SupportsBytes]) -> Response:
        '''Request the SPAMD service to check a message with a HEADERS request.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        :return: The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a report composed by the SPAMD service.

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

        request = Request('REPORT', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def report_if_spam(self, message: Union[bytes, SupportsBytes]) -> Response:
        '''Request the SPAMD service to check a message with a HEADERS request.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        :return: The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a report composed by the SPAMD service only if the
            message is marked as being spam.

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

        request = Request('REPORT_IFSPAM', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def symbols(self, message: Union[bytes, SupportsBytes]) -> Response:
        '''Request the SPAMD service to check a message with a HEADERS request.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        :return: The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a comma separated list of all the rule names.

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

        request = Request('SYMBOLS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def tell(self,
                   message_class: MessageClassOption,
                   message: Union[bytes, SupportsBytes],
                   remove_action: ActionOption = None,
                   set_action: ActionOption = None,
                   ):
        '''Instruct the SPAMD service to to mark the message

        :param message_class:
            An enumeration to classify the message as 'spam' or 'ham.'
        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.
        :param remove_action:
            Remove message class for message in database.
        :param set_action:
            Set message class for message in database.

        :return: Will contain a 'Spam' header if the message is marked as spam as
            well as the score and threshold.

            The body will contain a report composed by the SPAMD service only if
            message is marked as being spam.

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

        request = Request(verb='TELL',
                          headers=[MessageClass(message_class)],
                          body=message)
        if remove_action:
            request.headers['Remove'] = Remove(remove_action)
        if set_action:
            request.headers['Set'] = Set(set_action)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response
