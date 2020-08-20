#!/usr/bin/env python3

import asyncio
import sys

import pytest


def pytest_addoption(parser):
    parser.addoption('--spamd-process-timeout', action='store', default=10, type=int)


if sys.platform == 'win32':
    collect_ignore = ['connections/test_unix_connection.py', 'connections/test_unix_connection_manager.py']


@pytest.fixture
def x_headers():
    from aiospamc.header_values import GenericHeaderValue

    return {'A': GenericHeaderValue(value='a'), 'B': GenericHeaderValue(value='b')}


@pytest.fixture
def spam():
    '''Example spam message using SpamAssassin's GTUBE message.'''

    return (b'Subject: Test spam mail (GTUBE)\n'
            b'Message-ID: <GTUBE1.1010101@example.net>\n'
            b'Date: Wed, 23 Jul 2003 23:30:00 +0200\n'
            b'From: Sender <sender@example.net>\n'
            b'To: Recipient <recipient@example.net>\n'
            b'Precedence: junk\n'
            b'MIME-Version: 1.0\n'
            b'Content-Type: text/plain; charset=us-ascii\n'
            b'Content-Transfer-Encoding: 7bit\n\n'
            
            b'This is the GTUBE, the\n'
            b'\tGeneric\n'
            b'\tTest for\n'
            b'\tUnsolicited\n'
            b'\tBulk\n'
            b'\tEmail\n\n'
            
            b'If your spam filter supports it, the GTUBE provides a test by which you\n'
            b'can verify that the filter is installed correctly and is detecting incoming\n'
            b'spam. You can send yourself a test mail containing the following string of\n'
            b'characters (in upper case and with no white spaces and line breaks):\n\n'
            
            b'XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X\n\n'
            
            b'You should send this test mail from an account outside of your network.\n\n')


@pytest.fixture
def request_with_body():
    return b'CHECK SPAMC/1.5\r\nContent-length: 10\r\n\r\nTest body\n'


@pytest.fixture
def request_ping():
    '''PING request in bytes.'''
    return b'PING SPAMC/1.5\r\n\r\n'


@pytest.fixture
def response_empty():
    '''Empty response.'''
    return b''


@pytest.fixture
def response_ok():
    '''OK response in bytes.'''
    return b'SPAMD/1.5 0 EX_OK\r\n\r\n'


@pytest.fixture
def response_pong():
    '''PONG response in bytes.'''
    return b'SPAMD/1.5 0 PONG\r\n'


@pytest.fixture
def response_tell():
    '''Examplte TELL response.'''
    return b'SPAMD/1.1 0 EX_OK\r\n\r\n\r\n'


@pytest.fixture
def response_spam_header():
    '''Response with Spam header in bytes.'''
    return b'SPAMD/1.1 0 EX_OK\r\nSpam: True ; 1000.0 / 1.0\r\n\r\n'


@pytest.fixture
def response_with_body():
    '''Response with body and Content-length header in bytes.'''
    return b'SPAMD/1.5 0 EX_OK\r\nContent-length: 10\r\n\r\nTest body\n'


@pytest.fixture
def response_empty_body():
    '''Response with Content-length header, but empty body in bytes.'''
    return b'SPAMD/1.5 0 EX_OK\r\nContent-length: 0\r\n\r\n'


@pytest.fixture
def response_invalid():
    '''Invalid response in bytes.'''
    return b'Invalid response'


# Response exceptions
@pytest.fixture
def ex_usage():
    '''Command line usage error.'''
    return b'SPAMD/1.5 64 EX_USAGE\r\n\r\n'


@pytest.fixture
def ex_data_err():
    '''Data format error.'''
    return b'SPAMD/1.5 65 EX_DATAERR\r\n\r\n'


@pytest.fixture
def ex_no_input():
    '''No input response in bytes.'''
    return b'SPAMD/1.5 66 EX_NOINPUT\r\n\r\n'


@pytest.fixture
def ex_no_user():
    '''No user response in bytes.'''
    return b'SPAMD/1.5 67 EX_NOUSER\r\n\r\n'


@pytest.fixture
def ex_no_host():
    '''No host response in bytes.'''
    return b'SPAMD/1.5 68 EX_NOHOST\r\n\r\n'


@pytest.fixture
def ex_unavailable():
    '''Unavailable response in bytes.'''
    return b'SPAMD/1.5 69 EX_UNAVAILABLE\r\n\r\n'


@pytest.fixture
def ex_software():
    '''Software exception response in bytes.'''
    return b'SPAMD/1.5 70 EX_SOFTWARE\r\n\r\n'


@pytest.fixture
def ex_os_err():
    '''Operating system error response in bytes.'''
    return b'SPAMD/1.5 71 EX_OSERR\r\n\r\n'


@pytest.fixture
def ex_os_file():
    '''Operating system file error in bytes.'''
    return b'SPAMD/1.5 72 EX_OSFILE\r\n\r\n'


@pytest.fixture
def ex_cant_create():
    '''Can't create response error in bytes.'''
    return b'SPAMD/1.5 73 EX_CANTCREAT\r\n\r\n'


@pytest.fixture
def ex_io_err():
    '''Input/output error response in bytes.'''
    return b'SPAMD/1.5 74 EX_IOERR\r\n\r\n'


@pytest.fixture
def ex_temp_fail():
    '''Temporary failure error response in bytes.'''
    return b'SPAMD/1.5 75 EX_TEMPFAIL\r\n\r\n'


@pytest.fixture
def ex_protocol():
    '''Protocol error response in bytes.'''
    return b'SPAMD/1.5 76 EX_PROTOCOL\r\n\r\n'


@pytest.fixture
def ex_no_perm():
    '''No permission error response in bytes.'''
    return b'SPAMD/1.5 77 EX_NOPERM\r\n\r\n'


@pytest.fixture
def ex_config():
    '''Configuration error response in bytes.'''
    return b'SPAMD/1.5 78 EX_CONFIG\r\n\r\n'


@pytest.fixture
def ex_timeout():
    '''Timeout error response in bytes.'''
    return b'SPAMD/1.5 79 EX_TIMEOUT\r\n\r\n'


@pytest.fixture
def ex_undefined():
    '''Undefined exception in bytes.'''
    return b'SPAMD/1.5 999 EX_UNDEFINED\r\n\r\n'


# Mock fixtures for asyncio objects/functions

@pytest.fixture
def connection_refused(mocker):
    tcp_open = mocker.patch('asyncio.open_connection', side_effect=[ConnectionRefusedError()])
    if sys.platform == 'win32':
        yield
    else:
        unix_open = mocker.patch('asyncio.open_unix_connection', side_effect=[ConnectionRefusedError()])
        yield


@pytest.fixture
def mock_connection(mocker, response_ok):
    from itertools import cycle

    reader = mocker.MagicMock(spec=asyncio.StreamReader)
    reader.read.side_effect = cycle([response_ok])
    writer = mocker.MagicMock(spec=asyncio.StreamWriter)

    conn_string = mocker.patch('aiospamc.connections.Connection.connection_string',
                        return_value='MockConnectionString')
    conn_open = mocker.patch('aiospamc.connections.Connection.open',
                      return_value=(reader, writer))
    tcp_open = mocker.patch('aiospamc.connections.tcp_connection.TcpConnection.open',
                     return_value=(reader, writer))
    unix_open = mocker.patch('aiospamc.connections.unix_connection.UnixConnection.open',
                      return_value=(reader, writer))

    if sys.platform == 'win32':
        yield reader.read
    else:
        yield reader.read


@pytest.fixture
def stub_connection_manager(mocker):
    def inner(return_value=None, side_effect=None):
        connection = mocker.Mock()
        connection.request = mocker.AsyncMock(return_value=return_value, side_effect=side_effect)

        return connection

    yield inner
