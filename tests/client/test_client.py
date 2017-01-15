#!/usr/bin/env python3

import pytest

from servers import *

from aiospamc import Client
from aiospamc.responses import Response


def test_client_repr():
    client = Client()
    assert repr(client) == ('Client(host=\'localhost\', '
                            'port=783, '
                            'user=\'None\', '
                            'compress=False, '
                            'ssl=False)')

@pytest.mark.asyncio
async def test_client_send(event_loop, unused_tcp_port):
    mock = MockServer(b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    client.sleep_len = 0.1
    response = await client.send(b'PING SPAMC/1.5\r\n\r\n')

    assert isinstance(response, Response)

@pytest.mark.asyncio
async def test_client_send_tempfail(event_loop, unused_tcp_port):
    mock = MockServer(b'SPAMD/1.5 75 EX_TEMPFAIL\r\n',
                      b'SPAMD/1.5 75 EX_TEMPFAIL\r\n',
                      b'SPAMD/1.5 0 EX_OK\r\n')
    server = await asyncio.start_server(mock.handle_connection,
                                        host=HOST,
                                        port=unused_tcp_port,
                                        loop=event_loop)
    client = Client(HOST, unused_tcp_port, loop=event_loop)
    client.sleep_len = 0.1
    response = await client.send(b'PING SPAMC/1.5\r\n\r\n')

    assert isinstance(response, Response)
