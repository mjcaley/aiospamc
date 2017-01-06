#!/usr/bin/env python3

import asyncio

import pytest

from aiospamc import Client
from aiospamc.options import Action, MessageClassOption
from aiospamc.responses import SPAMDResponse


GTUBE=('Subject: Test spam mail (GTUBE)\n'
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

HOST='localhost'
PORT=7830

class SimpleServer:
    def __init__(self, response):
        self.response = response

    async def run(self, reader, writer):
        self.reader = reader
        self.writer = writer
        await self.read_request()

    async def read_request(self):
        data = await self.reader.read()
        self.request = data.decode()
        await self.send_response()

    async def send_response(self):
        self.writer.write(self.response.encode())
        self.writer.close()

def new_server(loop, address=(HOST, PORT)):
    server = SimpleServer('SPAMD/1.5 0 EX_OK\r\nSpam: True ; 2.0 / 4.0\r\n\r\n')
    coro = asyncio.start_server(server.run, host=address[0], port=address[1], loop=loop)
    return server, coro

def valid_response(func):
    def inner(unused_tcp_port):
        server = SimpleServer('SPAMD/1.5 0 EX_OK\r\nSpam: True ; 2.0 / 4.0\r\n\r\n')
        coro = asyncio.start_server(server.run, host=address[0], port=address[1], loop=loop)
        return server, coro

def test_check_valid_response(unused_tcp_port):
    event_loop = asyncio.get_event_loop()
    server, server_coro = new_server(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    check_coro = client.check(GTUBE)
    response, server_result = event_loop.run_until_complete(asyncio.gather(check_coro, server_coro))

    assert isinstance(response, SPAMDResponse)

def test_headers_valid_response(unused_tcp_port):
    event_loop = asyncio.get_event_loop()
    server, server_coro = new_server(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    headers_coro = client.headers(GTUBE)
    response, server_result = event_loop.run_until_complete(asyncio.gather(headers_coro, server_coro))

    assert isinstance(response, SPAMDResponse)

def test_ping_valid_response(unused_tcp_port):
    event_loop = asyncio.get_event_loop()
    server, server_coro = new_server(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    ping_coro = client.ping()
    response, server_result = event_loop.run_until_complete(asyncio.gather(ping_coro, server_coro))

    assert isinstance(response, SPAMDResponse)

def test_process_valid_response(unused_tcp_port):
    event_loop = asyncio.get_event_loop()
    server, server_coro = new_server(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    process_coro = client.process(GTUBE)
    response, server_result = event_loop.run_until_complete(asyncio.gather(process_coro, server_coro))

    assert isinstance(response, SPAMDResponse)

def test_report_valid_response(unused_tcp_port):
    event_loop = asyncio.get_event_loop()
    server, server_coro = new_server(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    report_coro = client.report(GTUBE)
    response, server_result = event_loop.run_until_complete(asyncio.gather(report_coro, server_coro))

    assert isinstance(response, SPAMDResponse)

def test_report_if_spam_valid_response(unused_tcp_port):
    event_loop = asyncio.get_event_loop()
    server, server_coro = new_server(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    report_if_spam_coro = client.report_if_spam(GTUBE)
    response, server_result = event_loop.run_until_complete(asyncio.gather(report_if_spam_coro, server_coro))

    assert isinstance(response, SPAMDResponse)

def test_symbols_valid_response(unused_tcp_port):
    event_loop = asyncio.get_event_loop()
    server, server_coro = new_server(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    symbols_coro = client.symbols(GTUBE)
    response, server_result = event_loop.run_until_complete(asyncio.gather(symbols_coro, server_coro))

    assert isinstance(response, SPAMDResponse)

def test_tell_valid_response(unused_tcp_port):
    event_loop = asyncio.get_event_loop()
    server, server_coro = new_server(event_loop, (HOST, unused_tcp_port))
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    tell_coro = client.tell(MessageClassOption.spam,
                            GTUBE,
                            set_action=Action(local=True, remote=True),
                            remove_action=Action(local=False, remote=False),
                           )
    response, server_result = event_loop.run_until_complete(asyncio.gather(tell_coro, server_coro))

    assert isinstance(response, SPAMDResponse)