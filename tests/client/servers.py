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

class MockServer:
    def __init__(self, *responses):
        self.responses = self.yield_response(responses)
        self.requests = []

    async def handle_connection(self, reader, writer):
        request = await reader.read()
        self.requests.append(request)
        response = next(self.responses)
        writer.write(response)
        writer.write_eof()
        await writer.drain()

    def yield_response(self, responses):
        for response in responses:
            yield response
        while True:
            yield responses[-1]
