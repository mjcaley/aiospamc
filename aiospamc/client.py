#!/usr/bin/env python3

'''Contains the Client class that is used to interact with SPAMD.'''

import asyncio

from aiospamc.headers import Compress, MessageClass, Remove, Set, User
from aiospamc.options import Action, MessageClassOption
from aiospamc.requests import (Check, Headers, Ping, Process,
                               Report, ReportIfSpam, Symbols, Tell)
from aiospamc.responses import SPAMDResponse


class Client:
    '''Client object for interacting with SPAMD.'''

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

    async def connect(self):
        '''Opens a socket connection to the SPAMD service.

        Returns
        -------
        (asyncio.StreamReader, asyncio.StreamWriter)
        '''
        reader, writer = await asyncio.open_connection(self.host,
                                                       self.port,
                                                       loop=self.loop,
                                                       ssl=self.ssl)
        return reader, writer

    async def send(self, request):
        '''Sends a request to the SPAMD service.

        Parameters
        ----------
        request : SPAMCRequest
            Request object to send.

        Returns
        -------
        SPAMDResponse
        '''

        reader, writer = await self.connect()
        writer.write(bytes(request))
        data = await reader.read()
        response = SPAMDResponse.parse(data.decode())

        return response

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
        SPAMDResponse

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        OSError
        ConnectionRefusedError
        '''

        request = Check(message)
        if self.compress:
            request.add_header(Compress())
        if self.user:
            request.add_header(User(self.user))
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
        aiospamc.responses.SPAMDResponse
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain the modified headers of the message.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        OSError
        ConnectionRefusedError
        '''

        request = Headers(message)
        if self.compress:
            request.add_header(Compress())
        if self.user:
            request.add_header(User(self.user))
        response = await self.send(request)

        return response

    async def ping(self):
        '''Sends a ping request to the SPAMD service and will receive a
        response if the serivce is alive.

        Returns
        -------
        SPAMDResponse
            Response message will contain 'PONG' if successful.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        OSError
        ConnectionRefusedError
        '''

        request = Ping()
        if self.user:
            request.add_header(User(self.user))
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
        SPAMDResponse
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a modified version of the message.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        OSError
        ConnectionRefusedError
        '''

        request = Process(message)
        if self.compress:
            request.add_header(Compress())
        if self.user:
            request.add_header(User(self.user))
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
        SPAMDResponse
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a report composed by the SPAMD service.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        OSError
        ConnectionRefusedError
        '''

        request = Report(message)
        if self.compress:
            request.add_header(Compress())
        if self.user:
            request.add_header(User(self.user))
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
        SPAMDResponse
            The response will contain a 'Spam' header if the message is marked
            as spam as well as the score and threshold.

            The body will contain a report composed by the SPAMD service only if
            message is marked as being spam.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        OSError
        ConnectionRefusedError
        '''

        request = ReportIfSpam(message)
        if self.compress:
            request.add_header(Compress())
        if self.user:
            request.add_header(User(self.user))
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
        SPAMDResponse
            Will contain a 'Spam' header if the message is marked as spam as
            well as the score and threshold.

            The body will contain a comma separated list of all the rule names.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        OSError
        ConnectionRefusedError
        '''

        request = Symbols(message)
        if self.compress:
            request.add_header(Compress())
        if self.user:
            request.add_header(User(self.user))
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
        SPAMDResponse
            Will contain a 'Spam' header if the message is marked as spam as
            well as the score and threshold.

            The body will contain a report composed by the SPAMD service only if
            message is marked as being spam.

        Raises
        ------
        aiospamc.exceptions.BadResponse
            If the response from SPAMD is ill-formed this exception will be
            raised.
        OSError
        ConnectionRefusedError
        '''

        request = Tell(message,
                       [MessageClass(message_class),
                        Set(set_action),
                        Remove(remove_action)]
                      )
        if self.compress:
            request.add_header(Compress())
        if self.user:
            request.add_header(User(self.user))
        response = await self.send(request)

        return response
