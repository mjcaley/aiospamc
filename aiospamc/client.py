#!/usr/bin/env python3

'''Contains the Client class that is used to interact with SPAMD.'''

import asyncio
from functools import wraps
import logging

from aiospamc.exceptions import (BadResponse, ResponseException,
                                 UsageException, DataErrorException, NoInputException, NoUserException,
                                 NoHostException, UnavailableException, InternalSoftwareException, OSErrorException,
                                 OSFileException, CantCreateException, IOErrorException, TemporaryFailureException,
                                 ProtocolException, NoPermissionException, ConfigException, TimeoutException)
from aiospamc.headers import Compress, MessageClass, Remove, Set, User
from aiospamc.parser import parse, ParseError
from aiospamc.requests import Request
from aiospamc.responses import Status


def _add_compress_header(func):
    '''If the class instance's :attribute:`compress` boolean is `True` then the
    :class:`aiospamc.headers.Compress` header is added to the
    :class:`aiospamc.requests.Request` object.'''

    @wraps(func)
    async def wrapper(cls, request):
        if cls.compress and cls.body:
            cls.logger.debug('Added Compress header to request (%s)', id(request))
            request.add_header(Compress())
        return await func(cls, request)

    return wrapper


def _add_user_header(func):
    '''If the class instance's :attribute:`user` boolean is `True` then the
    :class:`aiospamc.headers.User` header is added to the
    :class:`aiospamc.requests.Request` object.'''

    @wraps(func)
    async def wrapper(cls, request):
        if cls.user:
            cls.logger.debug('Added user header for \'%s\' to request (%s)',
                             cls.user,
                             id(request))
            request.add_header(User(cls.user))
        return await func(cls, request)

    return wrapper


class Client:
    '''Client object for interacting with SPAMD.

    Attributes
    ----------
    connection : :class:`aiospamc.connections.ConnectionManager`
        Manager instance to open connections.
    user : :obj:`str`
        Name of the user that SPAMD will run the checks under.
    compress : :obj:`bool`
        If true, the request body will be compressed.
    loop : :class:`asyncio.AbstractEventLoop`
        The asyncio event loop.
    logger : :class:`logging.Logger`
        Logging instance, logs to 'aiospamc.client'
    '''

    def __init__(self,
                 socket_path='/var/run/spamassassin/spamd.sock',
                 host=None,
                 port=783,
                 user=None,
                 compress=False,
                 ssl=False,
                 loop=None):
        '''Client constructor.

        Parameters
        ----------
        socket_path : :obj:`str`, optional
            The path to the Unix socket for the SPAMD service.
        host : :obj:`str`, optional
            Hostname or IP address of the SPAMD service, defaults to localhost.
        port : :obj:`int`, optional
            Port number for the SPAMD service, defaults to 783.
        user : :obj:`str`, optional
            Name of the user that SPAMD will run the checks under.
        compress : :obj:`bool`, optional
            If true, the request body will be compressed.
        ssl : :obj:`bool`, optional
            If true, will enable SSL/TLS for the connection.
        loop : :class:`asyncio.AbstractEventLoop`
            The asyncio event loop.

        Raises
        ------
        ValueError
            Raised if the constructor can't tell if it's using a TCP or a Unix
            domain socket connection.
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

    def __repr__(self):
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

    @staticmethod
    def _raise_response_exception(response):
        if response.status_code is Status.EX_OK:
            return
        elif response.status_code is Status.EX_USAGE:
            raise UsageException(response)
        elif response.status_code is Status.EX_DATAERR:
            raise DataErrorException(response)
        elif response.status_code is Status.EX_NOINPUT:
            raise NoInputException(response)
        elif response.status_code is Status.EX_NOUSER:
            raise NoUserException(response)
        elif response.status_code is Status.EX_NOHOST:
            raise NoHostException(response)
        elif response.status_code is Status.EX_UNAVAILABLE:
            raise UnavailableException(response)
        elif response.status_code is Status.EX_SOFTWARE:
            raise InternalSoftwareException(response)
        elif response.status_code is Status.EX_OSERR:
            raise OSErrorException(response)
        elif response.status_code is Status.EX_OSFILE:
            raise OSFileException(response)
        elif response.status_code is Status.EX_CANTCREAT:
            raise CantCreateException(response)
        elif response.status_code is Status.EX_IOERR:
            raise IOErrorException(response)
        elif response.status_code is Status.EX_TEMPFAIL:
            raise TemporaryFailureException(response)
        elif response.status_code is Status.EX_PROTOCOL:
            raise ProtocolException(response)
        elif response.status_code is Status.EX_NOPERM:
            raise NoPermissionException(response)
        elif response.status_code is Status.EX_CONFIG:
            raise ConfigException(response)
        elif response.status_code is Status.EX_TIMEOUT:
            raise TimeoutException(response)
        else:
            raise ResponseException(response)

    @_add_compress_header
    @_add_user_header
    async def send(self, request):
        '''Sends a request to the SPAMD service.

        If the SPAMD service gives a temporary failure response, then

        Parameters
        ----------
        request : :class:`aiospamc.requests.Request`
            Request object to send.

        Returns
        -------
        :class:`aiospamc.responses.Response`

        Raises
        ------
        :class:`aiospamc.exceptions.BadResponse`
            If the response from SPAMD is ill-formed this exception will be
            raised.
        :class:`aiospamc.exceptions.AIOSpamcConnectionFailed`
            Raised if an error occurred when trying to connect.
        :class:`aiospamc.exceptions.UsageException`
            Error in command line usage.
        :class:`aiospamc.exceptions.DataErrorException`
            Error with data format.
        :class:`aiospamc.exceptions.NoInputException`
            Cannot open input.
        :class:`aiospamc.exceptions.NoUserException`
            Addressee unknown.
        :class:`aiospamc.exceptions.NoHostException`
            Hostname unknown.
        :class:`aiospamc.exceptions.UnavailableException`
            Service unavailable.
        :class:`aiospamc.exceptions.InternalSoftwareException`
            Internal software error.
        :class:`aiospamc.exceptions.OSErrorException`
            System error.
        :class:`aiospamc.exceptions.OSFileException`
            Operating system file missing.
        :class:`aiospamc.exceptions.CantCreateException`
            Cannot create output file.
        :class:`aiospamc.exceptions.IOErrorException`
            Input/output error.
        :class:`aiospamc.exceptions.TemporaryFailureException`
            Temporary failure, may reattempt.
        :class:`aiospamc.exceptions.ProtocolException`
            Error in the protocol.
        :class:`aiospamc.exceptions.NoPermissionException`
            Permission denied.
        :class:`aiospamc.exceptions.ConfigException`
            Error in configuration.
        :class:`aiospamc.exceptions.TimeoutException`
            Timeout during connection.
        '''

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
            self._raise_response_exception(response)
        except ResponseException as error:
            self.logger.exception('Exception for request (%s)when composing response: %s',
                                  id(request),
                                  error)
            raise

        self.logger.debug('Received response (%s) for request (%s)',
            id(response),
            id(request))
        return response

    async def check(self, message):
        '''Request the SPAMD service to check a message with a CHECK request.

        The response will contain a 'Spam' header if the message is marked
        as spam as well as the score and threshold.

        SPAMD will perform a scan on the included message.  SPAMD expects an
        RFC 822 or RFC 2822 formatted email.

        Parameters
        ----------
        message : :obj:`str`
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        :class:`aiospamc.responses.Response`
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

        Raises
        ------
        :class:`aiospamc.exceptions.BadResponse`
            If the response from SPAMD is ill-formed this exception will be
            raised.
        :class:`aiospamc.exceptions.AIOSpamcConnectionFailed`
            Raised if an error occurred when trying to connect.
        :class:`aiospamc.exceptions.UsageException`
            Error in command line usage.
        :class:`aiospamc.exceptions.DataErrorException`
            Error with data format.
        :class:`aiospamc.exceptions.NoInputException`
            Cannot open input.
        :class:`aiospamc.exceptions.NoUserException`
            Addressee unknown.
        :class:`aiospamc.exceptions.NoHostException`
            Hostname unknown.
        :class:`aiospamc.exceptions.UnavailableException`
            Service unavailable.
        :class:`aiospamc.exceptions.InternalSoftwareException`
            Internal software error.
        :class:`aiospamc.exceptions.OSErrorException`
            System error.
        :class:`aiospamc.exceptions.OSFileException`
            Operating system file missing.
        :class:`aiospamc.exceptions.CantCreateException`
            Cannot create output file.
        :class:`aiospamc.exceptions.IOErrorException`
            Input/output error.
        :class:`aiospamc.exceptions.TemporaryFailureException`
            Temporary failure, may reattempt.
        :class:`aiospamc.exceptions.ProtocolException`
            Error in the protocol.
        :class:`aiospamc.exceptions.NoPermissionException`
            Permission denied.
        :class:`aiospamc.exceptions.ConfigException`
            Error in configuration.
        :class:`aiospamc.exceptions.TimeoutException`
            Timeout during connection.
        '''

        request = Request('CHECK', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def headers(self, message):
        '''Request the SPAMD service to check a message with a HEADERS request.

        Parameters
        ----------
        message : :obj:`str`
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        :class:`aiospamc.responses.Response`
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain the modified headers of the message.

        Raises
        ------
        :class:`aiospamc.exceptions.BadResponse`
            If the response from SPAMD is ill-formed this exception will be
            raised.
        :class:`aiospamc.exceptions.AIOSpamcConnectionFailed`
            Raised if an error occurred when trying to connect.
        :class:`aiospamc.exceptions.UsageException`
            Error in command line usage.
        :class:`aiospamc.exceptions.DataErrorException`
            Error with data format.
        :class:`aiospamc.exceptions.NoInputException`
            Cannot open input.
        :class:`aiospamc.exceptions.NoUserException`
            Addressee unknown.
        :class:`aiospamc.exceptions.NoHostException`
            Hostname unknown.
        :class:`aiospamc.exceptions.UnavailableException`
            Service unavailable.
        :class:`aiospamc.exceptions.InternalSoftwareException`
            Internal software error.
        :class:`aiospamc.exceptions.OSErrorException`
            System error.
        :class:`aiospamc.exceptions.OSFileException`
            Operating system file missing.
        :class:`aiospamc.exceptions.CantCreateException`
            Cannot create output file.
        :class:`aiospamc.exceptions.IOErrorException`
            Input/output error.
        :class:`aiospamc.exceptions.TemporaryFailureException`
            Temporary failure, may reattempt.
        :class:`aiospamc.exceptions.ProtocolException`
            Error in the protocol.
        :class:`aiospamc.exceptions.NoPermissionException`
            Permission denied.
        :class:`aiospamc.exceptions.ConfigException`
            Error in configuration.
        :class:`aiospamc.exceptions.TimeoutException`
            Timeout during connection.
        '''

        request = Request('HEADERS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def ping(self):
        '''Sends a ping request to the SPAMD service and will receive a
        response if the serivce is alive.

        Returns
        -------
        :class:`aiospamc.responses.Response`
            Response message will contain 'PONG' if successful.

        Raises
        ------
        :class:`aiospamc.exceptions.BadResponse`
            If the response from SPAMD is ill-formed this exception will be
            raised.
        :class:`aiospamc.exceptions.AIOSpamcConnectionFailed`
            Raised if an error occurred when trying to connect.
        :class:`aiospamc.exceptions.UsageException`
            Error in command line usage.
        :class:`aiospamc.exceptions.DataErrorException`
            Error with data format.
        :class:`aiospamc.exceptions.NoInputException`
            Cannot open input.
        :class:`aiospamc.exceptions.NoUserException`
            Addressee unknown.
        :class:`aiospamc.exceptions.NoHostException`
            Hostname unknown.
        :class:`aiospamc.exceptions.UnavailableException`
            Service unavailable.
        :class:`aiospamc.exceptions.InternalSoftwareException`
            Internal software error.
        :class:`aiospamc.exceptions.OSErrorException`
            System error.
        :class:`aiospamc.exceptions.OSFileException`
            Operating system file missing.
        :class:`aiospamc.exceptions.CantCreateException`
            Cannot create output file.
        :class:`aiospamc.exceptions.IOErrorException`
            Input/output error.
        :class:`aiospamc.exceptions.TemporaryFailureException`
            Temporary failure, may reattempt.
        :class:`aiospamc.exceptions.ProtocolException`
            Error in the protocol.
        :class:`aiospamc.exceptions.NoPermissionException`
            Permission denied.
        :class:`aiospamc.exceptions.ConfigException`
            Error in configuration.
        :class:`aiospamc.exceptions.TimeoutException`
            Timeout during connection.
        '''

        request = Request('PING')
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def process(self, message):
        '''Request the SPAMD service to check a message with a PROCESS request.

        Parameters
        ----------
        message : :obj:`str`
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        :class:`aiospamc.responses.Response`
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a modified version of the message.

        Raises
        ------
        :class:`aiospamc.exceptions.BadResponse`
            If the response from SPAMD is ill-formed this exception will be
            raised.
        :class:`aiospamc.exceptions.AIOSpamcConnectionFailed`
            Raised if an error occurred when trying to connect.
        :class:`aiospamc.exceptions.UsageException`
            Error in command line usage.
        :class:`aiospamc.exceptions.DataErrorException`
            Error with data format.
        :class:`aiospamc.exceptions.NoInputException`
            Cannot open input.
        :class:`aiospamc.exceptions.NoUserException`
            Addressee unknown.
        :class:`aiospamc.exceptions.NoHostException`
            Hostname unknown.
        :class:`aiospamc.exceptions.UnavailableException`
            Service unavailable.
        :class:`aiospamc.exceptions.InternalSoftwareException`
            Internal software error.
        :class:`aiospamc.exceptions.OSErrorException`
            System error.
        :class:`aiospamc.exceptions.OSFileException`
            Operating system file missing.
        :class:`aiospamc.exceptions.CantCreateException`
            Cannot create output file.
        :class:`aiospamc.exceptions.IOErrorException`
            Input/output error.
        :class:`aiospamc.exceptions.TemporaryFailureException`
            Temporary failure, may reattempt.
        :class:`aiospamc.exceptions.ProtocolException`
            Error in the protocol.
        :class:`aiospamc.exceptions.NoPermissionException`
            Permission denied.
        :class:`aiospamc.exceptions.ConfigException`
            Error in configuration.
        :class:`aiospamc.exceptions.TimeoutException`
            Timeout during connection.
        '''

        request = Request('PROCESS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def report(self, message):
        '''Request the SPAMD service to check a message with a REPORT request.

        Parameters
        ----------
        message : :obj:`str`
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        :class:`aiospamc.responses.Response`
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a report composed by the SPAMD service.

        Raises
        ------
        :class:`aiospamc.exceptions.BadResponse`
            If the response from SPAMD is ill-formed this exception will be
            raised.
        :class:`aiospamc.exceptions.AIOSpamcConnectionFailed`
            Raised if an error occurred when trying to connect.
        :class:`aiospamc.exceptions.UsageException`
            Error in command line usage.
        :class:`aiospamc.exceptions.DataErrorException`
            Error with data format.
        :class:`aiospamc.exceptions.NoInputException`
            Cannot open input.
        :class:`aiospamc.exceptions.NoUserException`
            Addressee unknown.
        :class:`aiospamc.exceptions.NoHostException`
            Hostname unknown.
        :class:`aiospamc.exceptions.UnavailableException`
            Service unavailable.
        :class:`aiospamc.exceptions.InternalSoftwareException`
            Internal software error.
        :class:`aiospamc.exceptions.OSErrorException`
            System error.
        :class:`aiospamc.exceptions.OSFileException`
            Operating system file missing.
        :class:`aiospamc.exceptions.CantCreateException`
            Cannot create output file.
        :class:`aiospamc.exceptions.IOErrorException`
            Input/output error.
        :class:`aiospamc.exceptions.TemporaryFailureException`
            Temporary failure, may reattempt.
        :class:`aiospamc.exceptions.ProtocolException`
            Error in the protocol.
        :class:`aiospamc.exceptions.NoPermissionException`
            Permission denied.
        :class:`aiospamc.exceptions.ConfigException`
            Error in configuration.
        :class:`aiospamc.exceptions.TimeoutException`
            Timeout during connection.
        '''

        request = Request('REPORT', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def report_if_spam(self, message):
        '''Request the SPAMD service to check a message with a REPORT_IFSPAM
        request.

        Parameters
        ----------
        message : :obj:`str`
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        :class:`aiospamc.responses.Response`
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a report composed by the SPAMD service only if
            message is marked as being spam.

        Raises
        ------
        :class:`aiospamc.exceptions.BadResponse`
            If the response from SPAMD is ill-formed this exception will be
            raised.
        :class:`aiospamc.exceptions.AIOSpamcConnectionFailed`
            Raised if an error occurred when trying to connect.
        :class:`aiospamc.exceptions.UsageException`
            Error in command line usage.
        :class:`aiospamc.exceptions.DataErrorException`
            Error with data format.
        :class:`aiospamc.exceptions.NoInputException`
            Cannot open input.
        :class:`aiospamc.exceptions.NoUserException`
            Addressee unknown.
        :class:`aiospamc.exceptions.NoHostException`
            Hostname unknown.
        :class:`aiospamc.exceptions.UnavailableException`
            Service unavailable.
        :class:`aiospamc.exceptions.InternalSoftwareException`
            Internal software error.
        :class:`aiospamc.exceptions.OSErrorException`
            System error.
        :class:`aiospamc.exceptions.OSFileException`
            Operating system file missing.
        :class:`aiospamc.exceptions.CantCreateException`
            Cannot create output file.
        :class:`aiospamc.exceptions.IOErrorException`
            Input/output error.
        :class:`aiospamc.exceptions.TemporaryFailureException`
            Temporary failure, may reattempt.
        :class:`aiospamc.exceptions.ProtocolException`
            Error in the protocol.
        :class:`aiospamc.exceptions.NoPermissionException`
            Permission denied.
        :class:`aiospamc.exceptions.ConfigException`
            Error in configuration.
        :class:`aiospamc.exceptions.TimeoutException`
            Timeout during connection.
        '''

        request = Request('REPORT_IFSPAM', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def symbols(self, message):
        '''Request the SPAMD service to check a message with a SYMBOLS request.

        The response will contain a 'Spam' header if the message is marked
        as spam as well as the score and threshold.

        Parameters
        ----------
        message : :obj:`str`
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        :class:`aiospamc.responses.Response`
            Will contain a 'Spam' header if the message is marked as spam as
            well as the score and threshold.

            The body will contain a comma separated list of all the rule names.

        Raises
        ------
        :class:`aiospamc.exceptions.BadResponse`
            If the response from SPAMD is ill-formed this exception will be
            raised.
        :class:`aiospamc.exceptions.AIOSpamcConnectionFailed`
            Raised if an error occurred when trying to connect.
        :class:`aiospamc.exceptions.UsageException`
            Error in command line usage.
        :class:`aiospamc.exceptions.DataErrorException`
            Error with data format.
        :class:`aiospamc.exceptions.NoInputException`
            Cannot open input.
        :class:`aiospamc.exceptions.NoUserException`
            Addressee unknown.
        :class:`aiospamc.exceptions.NoHostException`
            Hostname unknown.
        :class:`aiospamc.exceptions.UnavailableException`
            Service unavailable.
        :class:`aiospamc.exceptions.InternalSoftwareException`
            Internal software error.
        :class:`aiospamc.exceptions.OSErrorException`
            System error.
        :class:`aiospamc.exceptions.OSFileException`
            Operating system file missing.
        :class:`aiospamc.exceptions.CantCreateException`
            Cannot create output file.
        :class:`aiospamc.exceptions.IOErrorException`
            Input/output error.
        :class:`aiospamc.exceptions.TemporaryFailureException`
            Temporary failure, may reattempt.
        :class:`aiospamc.exceptions.ProtocolException`
            Error in the protocol.
        :class:`aiospamc.exceptions.NoPermissionException`
            Permission denied.
        :class:`aiospamc.exceptions.ConfigException`
            Error in configuration.
        :class:`aiospamc.exceptions.TimeoutException`
            Timeout during connection.
        '''

        request = Request('SYMBOLS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def tell(self,
                   message_class,
                   message,
                   remove_action=None,
                   set_action=None,
                  ):
        '''Instruct the SPAMD service to to mark the message

        Parameters
        ----------
        message_class : :class:`aiospamc.options.MessageClassOption`
            An enumeration to classify the message as 'spam' or 'ham.'
        message : :obj:`str`
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.
        remove_action : :class:`aiospamc.options.ActionOption`
            Remove message class for message in database.
        set_action : :class:`aiospamc.options.ActionOption`
            Set message class for message in database.

        Returns
        -------
        :class:`aiospamc.responses.Response`
            Will contain a 'Spam' header if the message is marked as spam as
            well as the score and threshold.

            The body will contain a report composed by the SPAMD service only if
            message is marked as being spam.

        Raises
        ------
        :class:`aiospamc.exceptions.BadResponse`
            If the response from SPAMD is ill-formed this exception will be
            raised.
        :class:`aiospamc.exceptions.AIOSpamcConnectionFailed`
            Raised if an error occurred when trying to connect.
        :class:`aiospamc.exceptions.UsageException`
            Error in command line usage.
        :class:`aiospamc.exceptions.DataErrorException`
            Error with data format.
        :class:`aiospamc.exceptions.NoInputException`
            Cannot open input.
        :class:`aiospamc.exceptions.NoUserException`
            Addressee unknown.
        :class:`aiospamc.exceptions.NoHostException`
            Hostname unknown.
        :class:`aiospamc.exceptions.UnavailableException`
            Service unavailable.
        :class:`aiospamc.exceptions.InternalSoftwareException`
            Internal software error.
        :class:`aiospamc.exceptions.OSErrorException`
            System error.
        :class:`aiospamc.exceptions.OSFileException`
            Operating system file missing.
        :class:`aiospamc.exceptions.CantCreateException`
            Cannot create output file.
        :class:`aiospamc.exceptions.IOErrorException`
            Input/output error.
        :class:`aiospamc.exceptions.TemporaryFailureException`
            Temporary failure, may reattempt.
        :class:`aiospamc.exceptions.ProtocolException`
            Error in the protocol.
        :class:`aiospamc.exceptions.NoPermissionException`
            Permission denied.
        :class:`aiospamc.exceptions.ConfigException`
            Error in configuration.
        :class:`aiospamc.exceptions.TimeoutException`
            Timeout during connection.
        '''

        request = Request(verb='TELL',
                          headers=(MessageClass(message_class),),
                          body=message)
        if remove_action:
            request.add_header(Set(remove_action))
        if set_action:
            request.add_header(Remove(set_action))
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response
