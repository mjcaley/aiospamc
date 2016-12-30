#!/usr/bin/env python3

import asyncio

from aiospamc.headers import MessageClass, MessageClassOption, Remove, Set, User
from aiospamc.requests import (Check, Headers, Ping, Process, 
                            Report, ReportIfSpam, Symbols, Tell)
from aiospamc.responses import SpamdResponse


class Client():
    def __init__(self,
                 host='localhost',
                 port=783,
                 user=None,
                 compress=False,
                 ssl=False,
                 loop=None):
        self.host = host
        self.port = port
        self.user = user
        self.compress = compress
        self.ssl = ssl
        self.loop = loop

    async def connect(self):
        reader, writer = await asyncio.open_connection(self.host,
                                                       self.port,
                                                       loop=self.loop,
                                                       ssl=self.ssl)
        return reader, writer

    async def send(self, request):
        reader, writer = await self.connect()
        writer.write(bytes(request))
        data = await reader.read()
        response = SpamdResponse.parse(data.decode())

        return response

    async def check(self, message):
        request = Check(message=message, compress=self.compress)
        if self.user:
            request.headers.append(User(self.user))
        response = await self.send(request)

        return response

    async def headers(self, message):
        request = Headers(message=message, compress=self.compress)
        if self.user:
            request.headers.append(User(self.user))
        response = await self.send(request)

        return response

    async def ping(self):
        request = Ping()
        if self.user:
            request.headers.append(User(self.user))
        response = await self.send(request)

        return response

    async def process(self, message):
        request = Process(message=message, compress=self.compress)
        if self.user:
            request.headers.append(User(self.user))
        response = await self.send(request)

        return response

    async def report(self, message):
        request = Report(message=message, compress=self.compress)
        if self.user:
            request.headers.append(User(self.user))
        response = await self.send(request)

        return response

    async def report_if_spam(self, message):
        request = ReportIfSpam(message=message, compress=self.compress)
        if self.user:
            request.headers.append(User(self.user))
        response = await self.send(request)

        return response

    async def symbols(self, message):
        request = Symbols(message=message, compress=self.compress)
        if self.user:
            request.headers.append(User(self.user))
        response = await self.send(request)

        return response

    async def tell(self,
                   message_class: MessageClassOption,
                   message,
                   set_destinations={'local': False, 'remote': False},
                   remove_destinations={'local': False, 'remote': False}
                  ):
        request = Tell(message,
                       [MessageClass(message_class),
                        Set(**set_destinations),
                        Remove(**remove_destinations)
                       ],
                       compress=self.compress
                      )
        if self.user:
            request.headers.append(User(self.user))
        response = await self.send(request)

        return response
