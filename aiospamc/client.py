#!/usr/bin/env python3

'''Contains the Client class that is used to interact with SPAMD.'''

import asyncio
import logging
from pathlib import Path
import ssl
from typing import SupportsBytes, Union

import certifi

from .exceptions import BadResponse, ResponseException
from .incremental_parser import ResponseParser, ParseError
from .options import ActionOption, MessageClassOption
from .requests import Request
from .responses import Response


class Client:
    '''Client object for interacting with SPAMD.'''

    def __init__(self,
                 socket_path: str = None,
                 host: str = 'localhost',
                 port: int = 783,
                 user: str = None,
                 compress: bool = False,
                 verify: Union[bool, str, Path] = None,
                 loop: asyncio.AbstractEventLoop = None) -> None:
        '''Client constructor.

        :param socket_path: The path to the Unix socket for the SPAMD service.
        :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
        :param port: Port number for the SPAMD service, defaults to 783.
        :param user: Name of the user that SPAMD will run the checks under.
        :param compress: If true, the request body will be compressed.
        :param verify: Use SSL for the connection.  If True, will use root certificates.
            If False, will not verify the certificate.  If a string to a path or a Path
            object, the connection will use the certificates found there.
        :param loop: The asyncio event loop.

        :raises ValueError: Raised if the constructor can't tell if it's using a TCP or a Unix domain socket connection.
        '''

        if socket_path:
            from aiospamc.connections.unix_connection import UnixConnectionManager
            self.connection = UnixConnectionManager(socket_path, loop=loop)
        elif host and port:
            from aiospamc.connections.tcp_connection import TcpConnectionManager
            if verify is not None:
                self.connection = TcpConnectionManager(host, port, self.new_ssl_context(verify), loop=loop)
            else:
                self.connection = TcpConnectionManager(host, port, loop=loop)
        else:
            raise ValueError('Either "host" and "port" or "socket_path" must be specified.')

        self._host = host
        self._port = port
        self._socket_path = socket_path
        self.user = user
        self.compress = compress

        self.logger = logging.getLogger(__name__)
        self.logger.debug('Created instance of %r', self)

    def __repr__(self) -> str:
        client_fmt = ('{}(socket_path={}, '
                      'host={}, '
                      'port={}, '
                      'user={}, '
                      'compress={})')
        return client_fmt.format(self.__class__.__name__,
                                 repr(self._socket_path),
                                 repr(self._host),
                                 repr(self._port),
                                 repr(self.user),
                                 repr(self.compress))

    @staticmethod
    def new_ssl_context(value: Union[bool, str, Path]) -> ssl.SSLContext:
        '''Creates an SSL context based on the supplied parameter.

        :param value: Use SSL for the connection.  If True, will use root certificates.
            If False, will not verify the certificate.  If a string to a path or a Path
            object, the connection will use the certificates found there.
        '''

        if value is True:
            return ssl.create_default_context(cafile=certifi.where())
        elif value is False:
            context = ssl.create_default_context(cafile=certifi.where())
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context

        cert_path = Path(value).absolute()
        if cert_path.is_dir():
            return ssl.create_default_context(capath=str(cert_path))
        elif cert_path.is_file():
            return ssl.create_default_context(cafile=str(cert_path))
        else:
            raise FileNotFoundError('Certificate path does not exist at {}'.format(value))

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
            request.headers['Compress'] = 'zlib'
        if self.user:
            request.headers['User'] = self.user

        self.logger.debug('Sending request (%s)', id(request))
        async with self.connection.new_connection() as connection:
            await connection.send(bytes(request))
            self.logger.debug('Request (%s) successfully sent', id(request))
            data = await connection.receive()

        try:
            try:
                parser = ResponseParser()
                parsed_response = parser.parse(data)
                response = Response(**parsed_response)
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
        '''Request the SPAMD service to check a message.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

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

        request = Request('HEADERS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def ping(self) -> Response:
        '''Sends a ping request to the SPAMD service and will receive a
        response if the service is alive.

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

        request = Request('PING')
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def process(self, message: Union[bytes, SupportsBytes]) -> Response:
        '''Process the message and return a modified copy of the message.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

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

        request = Request('PROCESS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def report(self, message: Union[bytes, SupportsBytes]) -> Response:
        '''Check if message is spam and return report.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

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

        request = Request('REPORT', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def report_if_spam(self, message: Union[bytes, SupportsBytes]) -> Response:
        '''Check if a message is spam and return a report if the message is spam.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

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

        request = Request('REPORT_IFSPAM', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def symbols(self, message: Union[bytes, SupportsBytes]) -> Response:
        '''Check if the message is spam and return a list of symbols that were hit.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

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

        request = Request('SYMBOLS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def tell(self,
                   message: Union[bytes, SupportsBytes],
                   message_class: Union[str, MessageClassOption],
                   remove_action: Union[str, ActionOption] = None,
                   set_action: Union[str, ActionOption] = None,
                   ):
        '''Instruct the SPAMD service to to mark the message.

        :param message:
            A byte string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.
        :param message_class: How to classify the message, either "ham" or "spam".
        :param remove_action: Remove message class for message in database.
        :param set_action:
            Set message class for message in database.  Either `ham` or `spam`.

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

        request = Request(verb='TELL', body=message)

        request.headers['Message-class'] = message_class

        if remove_action:
            request.headers['Remove'] = remove_action
        if set_action:
            request.headers['Set'] = set_action
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response
