#!/usr/bin/env python3

import asyncio


GTUBE = ('Subject: Test spam mail (GTUBE)\n'
         'Message-ID: <GTUBE1.1010101@example.net>\n'
         'Date: Wed, 23 Jul 2003 23:30:00 +0200\n'
         'From: Sender <sender@example.net>\n'
         'To: Recipient <recipient@example.net>\n'
         'Precedence: junk\n'
         'MIME-Version: 1.0\n'
         'Content-Type: text/plain; charset=us-ascii\n'
         'Content-Transfer-Encoding: 7bit\n\n'

         'This is the GTUBE, the\n'
         '\tGeneric\n'
         '\tTest for\n'
         '\tUnsolicited\n'
         '\tBulk\n'
         '\tEmail\n\n'

         'If your spam filter supports it, the GTUBE provides a test by which you\n'
         'can verify that the filter is installed correctly and is detecting incoming\n'
         'spam. You can send yourself a test mail containing the following string of\n'
         'characters (in upper case and with no white spaces and line breaks):\n\n'

         'XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X\n\n'

         'You should send this test mail from an account outside of your network.\n\n')

HOST = 'localhost'
PORT = 7830

class SimpleServer:
    def __init__(self, response):
        self.response = response

    async def run(self, reader, writer):
        self.reader = reader
        self.writer = writer
        await self.read_request()

    async def read_request(self):
        data = await self.reader.read()
        self.request = data
        await self.send_response()

    async def send_response(self):
        self.writer.write(self.response.encode())
        self.writer.close()

async def valid_response(loop, address=(HOST, PORT)):
    server = SimpleServer('SPAMD/1.5 0 EX_OK\r\nSpam: True ; 2.0 / 4.0\r\n\r\n')
    await asyncio.start_server(server.run, host=address[0], port=address[1], loop=loop)
    return server

async def invalid_response(loop, address=(HOST, PORT)):
    server = SimpleServer('Invalid data\r\n\r\n')
    await asyncio.start_server(server.run, host=address[0], port=address[1], loop=loop)
    return server
