#!/usr/bin/env python3

'''Contains the Client class that is used to interact with SPAMD.'''

import asyncio
import logging

from aiospamc.exceptions import BadResponse, SPAMDConnectionRefused
from aiospamc.headers import Compress, MessageClass, Remove, Set, User
from aiospamc.options import Action, MessageClassOption
from aiospamc.requests import Request
from aiospamc.responses import Response


class Client:
    '''Client object for interacting with SPAMD.

    Attributes
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
    loop : asyncio.AbstractEventLoop
        The asyncio event loop.
    logger : logging.Logger
        Logging instance, logs to 'aiospamc.client'
    '''

    def __init__(self,
                 host='localhost',
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
        loop : asyncio.AbstractEventLoop
            The asyncio event loop.
        '''

        self.host = host
        self.port = port
        self.user = user
        self.compress = compress
        self.ssl = ssl
        self.loop = loop or asyncio.get_event_loop()

        self.logger = logging.getLogger(__name__)
        self.logger.debug('Created instance of %r', self)

    def __repr__(self):
        client_fmt = ('{}(host=\'{}\', '
                      'port={}, '
                      'user=\'{}\', '
                      'compress={}, '
                      'ssl={})')
        return client_fmt.format(self.__class__.__name__,
                                 self.host,
                                 self.port,
                                 self.user,
                                 self.compress,
                                 self.ssl,
                                 self.loop)

    async def connect(self):
        '''Opens a socket connection to the SPAMD service.

        Returns
        -------
        (asyncio.StreamReader, asyncio.StreamWriter)

        Raises
        ------
        aiospamc.exceptions.SPAMDConnectionRefused
            Raised if an error occurred when trying to connect.
        '''

        self.logger.debug('Connecting to %s:%s', self.host, self.port)
        try:
            reader, writer = await asyncio.open_connection(self.host,
                                                           self.port,
                                                           loop=self.loop,
                                                           ssl=self.ssl)
        except (ConnectionRefusedError, OSError) as error:
            raised = SPAMDConnectionRefused(error)
            self.logger.exception('Exception occurred when connecting: %s', raised)
            raise raised

        self.logger.debug('Connected to %s:%i', self.host, self.port)

        return reader, writer

    async def send(self, request):
        '''Sends a request to the SPAMD service.

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
        aiospamc.exceptions.SPAMDConnectionRefused
            Raised if an error occurred when trying to connect.
        '''

        reader, writer = await self.connect()

        self.logger.debug('Sending request (%s)', id(request))
        writer.write(bytes(request))
        writer.write_eof()
        await writer.drain()
        self.logger.debug('Request (%s) successfully sent', id(request))

        data = await reader.read()
        try:
            response = Response.parse(data.decode())
        except BadResponse as error:
            self.logger.exception('Exception when composing response: %s', error)
            raise error
        self.logger.debug('Received repsonse (%s) for request (%s)',
                          id(response),
                          id(request))

        return response

    def _supplement_request(self, request):
        '''Adds User and Compress headers to the request if the client is
        configured to do so.  Object is modified in place.

        Returns
        -------
        aiospamc.requests.Request
            The modified request.
        '''

        if self.compress and request.body:
            self.logger.debug('Added Compress header to request (%s)', id(request))
            request.add_header(Compress())
        if self.user:
            self.logger.debug('Added user header for \'%s\' to request (%s)',
                              self.user,
                              id(request))
            request.add_header(User(self.user))

    async def check(self, message):
        '''Request the SPAMD service to check a message with a CHECK request.

        The response will contain a 'Spam' header if the message is marked
        as spam as well as the score and threshold.

        SPAMD will perform a scan on the included message.  SPAMD expects an
        RFC 822 or RFC 2822 formatted email.

        Parameters
        ----------
        message
            An object that can be convertable to a bytes object.

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
        aiospamc.exceptions.SPAMDConnectionRefused
            Raised if an error occurred when trying to connect.
        '''

        request = Request('CHECK', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb.decode(), id(request))
        self._supplement_request(request)
        response = await self.send(request)

        return response

    async def headers(self, message):
        '''Request the SPAMD service to check a message with a HEADERS request.

        Parameters
        ----------
        message
            An object that can be convertable to a bytes object.

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
        aiospamc.exceptions.SPAMDConnectionRefused
            Raised if an error occurred when trying to connect.
        '''

        request = Request('HEADERS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb.decode(), id(request))
        self._supplement_request(request)
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
        aiospamc.exceptions.SPAMDConnectionRefused
            Raised if an error occurred when trying to connect.
        '''

        request = Request('PING')
        self.logger.debug('Composed %s request (%s)', request.verb.decode(), id(request))
        self._supplement_request(request)
        response = await self.send(request)

        return response

    async def process(self, message):
        '''Request the SPAMD service to check a message with a PROCESS request.

        Parameters
        ----------
        message
            An object that can be convertable to a bytes object.

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
        aiospamc.exceptions.SPAMDConnectionRefused
            Raised if an error occurred when trying to connect.
        '''

        request = Request('PROCESS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb.decode(), id(request))
        self._supplement_request(request)
        response = await self.send(request)

        return response

    async def report(self, message):
        '''Request the SPAMD service to check a message with a REPORT request.

        Parameters
        ----------
        message
            An object that can be convertable to a bytes object.

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
        aiospamc.exceptions.SPAMDConnectionRefused
            Raised if an error occurred when trying to connect.
        '''

        request = Request('REPORT', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb.decode(), id(request))
        self._supplement_request(request)
        response = await self.send(request)

        return response

    async def report_if_spam(self, message):
        '''Request the SPAMD service to check a message with a REPORT_IFSPAM
        request.

        Parameters
        ----------
        message
            An object that can be convertable to a bytes object.

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
        aiospamc.exceptions.SPAMDConnectionRefused
            Raised if an error occurred when trying to connect.
        '''

        request = Request('REPORT_IFSPAM', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb.decode(), id(request))
        self._supplement_request(request)
        response = await self.send(request)

        return response

    async def symbols(self, message):
        '''Request the SPAMD service to check a message with a SYMBOLS request.

        The response will contain a 'Spam' header if the message is marked
        as spam as well as the score and threshold.

        Parameters
        ----------
        message
            An object that can be convertable to a bytes object.

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
        aiospamc.exceptions.SPAMDConnectionRefused
            Raised if an error occurred when trying to connect.
        '''

        request = Request('SYMBOLS', body=message)
        self.logger.debug('Composed %s request (%s)', request.verb.decode(), id(request))
        self._supplement_request(request)
        response = await self.send(request)

        return response

    async def tell(self,
                   message_class: MessageClassOption,
                   message,
                   set_action=Action(local=False, remote=False),
                   remove_action=Action(local=False, remote=False)
                  ):
        '''Instruct the SPAMD service to to mark the message

        Parameters
        ----------
        message_class : MessageClassOption
            An enumeration to classify the message as 'spam' or 'ham.'

        message
            An object that can be convertable to a bytes object.

            SPAMD will perform a scan on the included message.  SPAMD expects an
            RFC 822 or RFC 2822 formatted email.

        set_action : Action
            Contains 'local' and 'remote' options.

        remove_action : Action
            Contains 'local' and 'remote' options.

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
        aiospamc.exceptions.SPAMDConnectionRefused
            Raised if an error occurred when trying to connect.
        '''

        request = Request('TELL',
                               message,
                               MessageClass(message_class),
                               Set(set_action),
                               Remove(remove_action))
        self.logger.debug('Composed %s request (%s)', request.verb.decode(), id(request))
        self._supplement_request(request)
        response = await self.send(request)

        return response
