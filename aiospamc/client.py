#!/usr/bin/env python3

'''Contains the Client class that is used to interact with SPAMD.'''

import asyncio
from functools import wraps
import logging

from aiospamc.exceptions import BadResponse, ResponseException, TemporaryFailureException
from aiospamc.headers import Compress, MessageClass, Remove, Set, User
from aiospamc.options import RemoveOption, SetOption
from aiospamc.requests import Request
from aiospamc.responses import Response


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
    user : str
        Name of the user that SPAMD will run the checks under.
    compress : bool
        If true, the request body will be compressed.
    sleep_len : float
        Length of time to wait to retry a connection in seconds.
    retry_attempts : float
        Number of times to retry a connection.
    loop : asyncio.AbstractEventLoop
        The asyncio event loop.
    logger : logging.Logger
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
        loop : :obj:`asyncio.AbstractEventLoop`
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

        self.sleep_len = 3
        self.retry_attempts = 4
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

    @_add_compress_header
    @_add_user_header
    async def send(self, request):
        '''Sends a request to the SPAMD service.

        If the SPAMD service gives a temporary failure response, then

        Parameters
        ----------
        request : aiospamc.requests.Request
            Request object to send.

        Returns
        -------
        aiospamc.responses.Response

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        aiospamc.exceptions.AIOSpamcConnectionFailed
            Raised if an error occurred when trying to connect.
        aiospamc.exceptions.UsageException
            Error in command line usage.
        aiospamc.exceptions.DataErrorException
            Error with data format.
        aiospamc.exceptions.NoInputException
            Cannot open input.
        aiospamc.exceptions.NoUserException
            Addressee unknown.
        aiospamc.exceptions.NoHostException
            Hostname unknown.
        aiospamc.exceptions.UnavailableException
            Service unavailable.
        aiospamc.exceptions.InternalSoftwareException
            Internal software error.
        aiospamc.exceptions.OSErrorException
            System error.
        aiospamc.exceptions.OSFileException
            Operating system file missing.
        aiospamc.exceptions.CantCreateException
            Cannot create output file.
        aiospamc.exceptions.IOErrorException
            Input/output error.
        aiospamc.exceptions.TemporaryFailureException
            Temporary failure, may reattempt.
        aiospamc.exceptions.ProtocolException
            Error in the protocol.
        aiospamc.exceptions.NoPermissionException
            Permission denied.
        aiospamc.exceptions.ConfigException
            Error in configuration.
        aiospamc.exceptions.TimeoutException
            Timeout during connection.
        '''

        for attempt in range(1, self.retry_attempts):
            self.logger.debug('Sending request (%s) attempt #%s', id(request), attempt)
            async with self.connection.new_connection() as connection:
                await connection.send(bytes(request))
                self.logger.debug('Request (%s) successfully sent', id(request))

                data = await connection.receive()
                try:
                    response = Response.parse(data)
                except TemporaryFailureException:
                    self.logger.exception('Exception reporting temporary failure, retying in %i seconds',
                                          self.sleep_len)
                    await asyncio.sleep(self.sleep_len)
                    continue
                except (BadResponse, ResponseException) as error:
                    self.logger.exception('Exception when composing response: %s', error)
                    raise
                else:
                    # Success! return the response
                    break

        self.logger.debug('Received repsonse (%s) for request (%s)',
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
        message : str
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        aiospamc.responses.Response
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        aiospamc.exceptions.AIOSpamcConnectionFailed
            Raised if an error occurred when trying to connect.
        aiospamc.exceptions.UsageException
            Error in command line usage.
        aiospamc.exceptions.DataErrorException
            Error with data format.
        aiospamc.exceptions.NoInputException
            Cannot open input.
        aiospamc.exceptions.NoUserException
            Addressee unknown.
        aiospamc.exceptions.NoHostException
            Hostname unknown.
        aiospamc.exceptions.UnavailableException
            Service unavailable.
        aiospamc.exceptions.InternalSoftwareException
            Internal software error.
        aiospamc.exceptions.OSErrorException
            System error.
        aiospamc.exceptions.OSFileException
            Operating system file missing.
        aiospamc.exceptions.CantCreateException
            Cannot create output file.
        aiospamc.exceptions.IOErrorException
            Input/output error.
        aiospamc.exceptions.TemporaryFailureException
            Temporary failure, may reattempt.
        aiospamc.exceptions.ProtocolException
            Error in the protocol.
        aiospamc.exceptions.NoPermissionException
            Permission denied.
        aiospamc.exceptions.ConfigException
            Error in configuration.
        aiospamc.exceptions.TimeoutException
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
        message : str
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        aiospamc.responses.Response
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain the modified headers of the message.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        aiospamc.exceptions.AIOSpamcConnectionFailed
            Raised if an error occurred when trying to connect.
        aiospamc.exceptions.UsageException
            Error in command line usage.
        aiospamc.exceptions.DataErrorException
            Error with data format.
        aiospamc.exceptions.NoInputException
            Cannot open input.
        aiospamc.exceptions.NoUserException
            Addressee unknown.
        aiospamc.exceptions.NoHostException
            Hostname unknown.
        aiospamc.exceptions.UnavailableException
            Service unavailable.
        aiospamc.exceptions.InternalSoftwareException
            Internal software error.
        aiospamc.exceptions.OSErrorException
            System error.
        aiospamc.exceptions.OSFileException
            Operating system file missing.
        aiospamc.exceptions.CantCreateException
            Cannot create output file.
        aiospamc.exceptions.IOErrorException
            Input/output error.
        aiospamc.exceptions.TemporaryFailureException
            Temporary failure, may reattempt.
        aiospamc.exceptions.ProtocolException
            Error in the protocol.
        aiospamc.exceptions.NoPermissionException
            Permission denied.
        aiospamc.exceptions.ConfigException
            Error in configuration.
        aiospamc.exceptions.TimeoutException
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
        aiospamc.responses.Response
            Response message will contain 'PONG' if successful.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        aiospamc.exceptions.AIOSpamcConnectionFailed
            Raised if an error occurred when trying to connect.
        aiospamc.exceptions.UsageException
            Error in command line usage.
        aiospamc.exceptions.DataErrorException
            Error with data format.
        aiospamc.exceptions.NoInputException
            Cannot open input.
        aiospamc.exceptions.NoUserException
            Addressee unknown.
        aiospamc.exceptions.NoHostException
            Hostname unknown.
        aiospamc.exceptions.UnavailableException
            Service unavailable.
        aiospamc.exceptions.InternalSoftwareException
            Internal software error.
        aiospamc.exceptions.OSErrorException
            System error.
        aiospamc.exceptions.OSFileException
            Operating system file missing.
        aiospamc.exceptions.CantCreateException
            Cannot create output file.
        aiospamc.exceptions.IOErrorException
            Input/output error.
        aiospamc.exceptions.TemporaryFailureException
            Temporary failure, may reattempt.
        aiospamc.exceptions.ProtocolException
            Error in the protocol.
        aiospamc.exceptions.NoPermissionException
            Permission denied.
        aiospamc.exceptions.ConfigException
            Error in configuration.
        aiospamc.exceptions.TimeoutException
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
        message : str
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        aiospamc.responses.Response
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a modified version of the message.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        aiospamc.exceptions.AIOSpamcConnectionFailed
            Raised if an error occurred when trying to connect.
        aiospamc.exceptions.UsageException
            Error in command line usage.
        aiospamc.exceptions.DataErrorException
            Error with data format.
        aiospamc.exceptions.NoInputException
            Cannot open input.
        aiospamc.exceptions.NoUserException
            Addressee unknown.
        aiospamc.exceptions.NoHostException
            Hostname unknown.
        aiospamc.exceptions.UnavailableException
            Service unavailable.
        aiospamc.exceptions.InternalSoftwareException
            Internal software error.
        aiospamc.exceptions.OSErrorException
            System error.
        aiospamc.exceptions.OSFileException
            Operating system file missing.
        aiospamc.exceptions.CantCreateException
            Cannot create output file.
        aiospamc.exceptions.IOErrorException
            Input/output error.
        aiospamc.exceptions.TemporaryFailureException
            Temporary failure, may reattempt.
        aiospamc.exceptions.ProtocolException
            Error in the protocol.
        aiospamc.exceptions.NoPermissionException
            Permission denied.
        aiospamc.exceptions.ConfigException
            Error in configuration.
        aiospamc.exceptions.TimeoutException
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
        message : str
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        aiospamc.responses.Response
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a report composed by the SPAMD service.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        aiospamc.exceptions.AIOSpamcConnectionFailed
            Raised if an error occurred when trying to connect.
        aiospamc.exceptions.UsageException
            Error in command line usage.
        aiospamc.exceptions.DataErrorException
            Error with data format.
        aiospamc.exceptions.NoInputException
            Cannot open input.
        aiospamc.exceptions.NoUserException
            Addressee unknown.
        aiospamc.exceptions.NoHostException
            Hostname unknown.
        aiospamc.exceptions.UnavailableException
            Service unavailable.
        aiospamc.exceptions.InternalSoftwareException
            Internal software error.
        aiospamc.exceptions.OSErrorException
            System error.
        aiospamc.exceptions.OSFileException
            Operating system file missing.
        aiospamc.exceptions.CantCreateException
            Cannot create output file.
        aiospamc.exceptions.IOErrorException
            Input/output error.
        aiospamc.exceptions.TemporaryFailureException
            Temporary failure, may reattempt.
        aiospamc.exceptions.ProtocolException
            Error in the protocol.
        aiospamc.exceptions.NoPermissionException
            Permission denied.
        aiospamc.exceptions.ConfigException
            Error in configuration.
        aiospamc.exceptions.TimeoutException
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
        message : str
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        aiospamc.responses.Response
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a report composed by the SPAMD service only if
            message is marked as being spam.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        aiospamc.exceptions.AIOSpamcConnectionFailed
            Raised if an error occurred when trying to connect.
        aiospamc.exceptions.UsageException
            Error in command line usage.
        aiospamc.exceptions.DataErrorException
            Error with data format.
        aiospamc.exceptions.NoInputException
            Cannot open input.
        aiospamc.exceptions.NoUserException
            Addressee unknown.
        aiospamc.exceptions.NoHostException
            Hostname unknown.
        aiospamc.exceptions.UnavailableException
            Service unavailable.
        aiospamc.exceptions.InternalSoftwareException
            Internal software error.
        aiospamc.exceptions.OSErrorException
            System error.
        aiospamc.exceptions.OSFileException
            Operating system file missing.
        aiospamc.exceptions.CantCreateException
            Cannot create output file.
        aiospamc.exceptions.IOErrorException
            Input/output error.
        aiospamc.exceptions.TemporaryFailureException
            Temporary failure, may reattempt.
        aiospamc.exceptions.ProtocolException
            Error in the protocol.
        aiospamc.exceptions.NoPermissionException
            Permission denied.
        aiospamc.exceptions.ConfigException
            Error in configuration.
        aiospamc.exceptions.TimeoutException
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
        message : str
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        Returns
        -------
        aiospamc.responses.Response
            Will contain a 'Spam' header if the message is marked as spam as
            well as the score and threshold.

            The body will contain a comma separated list of all the rule names.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        aiospamc.exceptions.AIOSpamcConnectionFailed
            Raised if an error occurred when trying to connect.
        aiospamc.exceptions.UsageException
            Error in command line usage.
        aiospamc.exceptions.DataErrorException
            Error with data format.
        aiospamc.exceptions.NoInputException
            Cannot open input.
        aiospamc.exceptions.NoUserException
            Addressee unknown.
        aiospamc.exceptions.NoHostException
            Hostname unknown.
        aiospamc.exceptions.UnavailableException
            Service unavailable.
        aiospamc.exceptions.InternalSoftwareException
            Internal software error.
        aiospamc.exceptions.OSErrorException
            System error.
        aiospamc.exceptions.OSFileException
            Operating system file missing.
        aiospamc.exceptions.CantCreateException
            Cannot create output file.
        aiospamc.exceptions.IOErrorException
            Input/output error.
        aiospamc.exceptions.TemporaryFailureException
            Temporary failure, may reattempt.
        aiospamc.exceptions.ProtocolException
            Error in the protocol.
        aiospamc.exceptions.NoPermissionException
            Permission denied.
        aiospamc.exceptions.ConfigException
            Error in configuration.
        aiospamc.exceptions.TimeoutException
            Timeout during connection.
        '''

        request = Request('SYMBOLS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response

    async def tell(self,
                   message_class,
                   message,
                   action
                  ):
        '''Instruct the SPAMD service to to mark the message

        Parameters
        ----------
        message_class : aiospamc.options.MessageClassOption
            An enumeration to classify the message as 'spam' or 'ham.'
        message : str
            A string containing the contents of the message to be scanned.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.
        action : Union[aiospamc.options.RemoveOption, aiospamc.options.SetOption]
            Contains 'local' and 'remote' options.  Depending on which type
            is passed with determine what headers are added to the request.

        Returns
        -------
        aiospamc.responses.Response
            Will contain a 'Spam' header if the message is marked as spam as
            well as the score and threshold.

            The body will contain a report composed by the SPAMD service only if
            message is marked as being spam.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        aiospamc.exceptions.AIOSpamcConnectionFailed
            Raised if an error occurred when trying to connect.
        aiospamc.exceptions.UsageException
            Error in command line usage.
        aiospamc.exceptions.DataErrorException
            Error with data format.
        aiospamc.exceptions.NoInputException
            Cannot open input.
        aiospamc.exceptions.NoUserException
            Addressee unknown.
        aiospamc.exceptions.NoHostException
            Hostname unknown.
        aiospamc.exceptions.UnavailableException
            Service unavailable.
        aiospamc.exceptions.InternalSoftwareException
            Internal software error.
        aiospamc.exceptions.OSErrorException
            System error.
        aiospamc.exceptions.OSFileException
            Operating system file missing.
        aiospamc.exceptions.CantCreateException
            Cannot create output file.
        aiospamc.exceptions.IOErrorException
            Input/output error.
        aiospamc.exceptions.TemporaryFailureException
            Temporary failure, may reattempt.
        aiospamc.exceptions.ProtocolException
            Error in the protocol.
        aiospamc.exceptions.NoPermissionException
            Permission denied.
        aiospamc.exceptions.ConfigException
            Error in configuration.
        aiospamc.exceptions.TimeoutException
            Timeout during connection.
        '''

        request = Request('TELL',
                          message,
                          MessageClass(message_class))
        if isinstance(action, RemoveOption):
            request.add_header(Remove(action))
        elif isinstance(action, SetOption):
            request.add_header(Set(action))
        self.logger.debug('Composed %s request (%s)', request.verb, id(request))
        response = await self.send(request)

        return response
