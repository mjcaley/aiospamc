#!/usr/bin/env python3

import pytest
from asynctest import CoroutineMock, MagicMock


@pytest.fixture
def address():
    return 'localhost', 783


@pytest.fixture
def open_connection(mocker):
    yield mocker.patch('asyncio.open_connection', CoroutineMock(return_value=(MagicMock(), MagicMock())))


@pytest.fixture
def connection_refused(mocker):
    yield mocker.patch('asyncio.open_connection', CoroutineMock(side_effect=ConnectionRefusedError))


@pytest.fixture
def os_error(mocker):
    yield mocker.patch('asyncio.open_connection', CoroutineMock(side_effect=OSError))


@pytest.fixture
def unix_socket():
    return '/var/run/spamassassin/spamd.sock'


@pytest.fixture
def open_unix_connection(mocker):
    yield mocker.patch('asyncio.open_unix_connection', CoroutineMock(return_value=(MagicMock(), MagicMock())))


@pytest.fixture
def unix_connection_refused(mocker):
    yield mocker.patch('asyncio.open_unix_connection', CoroutineMock(side_effect=ConnectionRefusedError))


@pytest.fixture
def unix_os_error(mocker):
    yield mocker.patch('asyncio.open_unix_connection', CoroutineMock(side_effect=OSError))
