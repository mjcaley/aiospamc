#!/usr/bin/env python3

import pytest
from fixtures import *

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
@pytest.mark.usefixtures('mock_stream')
@pytest.mark.responses(response_pong())
async def test_client_send(request_ping):
    client = Client()
    client.sleep_len = 0.1
    response = await client.send(request_ping)

    assert isinstance(response, Response)

@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_stream')
@pytest.mark.responses(ex_temp_fail(), ex_temp_fail(), response_pong())
async def test_client_send_tempfail(request_ping):
    client = Client()
    client.sleep_len = 0.1
    response = await client.send(request_ping)

    assert isinstance(response, Response)
