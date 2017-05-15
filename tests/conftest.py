#!/usr/bin/env python3

import asyncio
from asynctest import patch, MagicMock

import pytest


@pytest.fixture
def spam():
    '''Example spam message using SpamAssassin's GTUBE message.'''

    return ('Subject: Test spam mail (GTUBE)\n'
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
    return b'SPAMD/1.5 0 PONG\r\n\r\n'


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
    return b'SPAMD/1.5 0 EX_OK\r\nContent-length: 0\r\n'


@pytest.fixture
def response_invalid():
    '''Invalid response in bytes.'''
    return b'Invalid response'


# Response exceptions
@pytest.fixture
def ex_usage():
    '''Command line usage error.'''
    return b'SPAMD/1.5 64 EX_USAGE\r\n'


@pytest.fixture
def ex_data_err():
    '''Data format error.'''
    return b'SPAMD/1.5 65 EX_DATAERR\r\n'


@pytest.fixture
def ex_no_input():
    '''No input response in bytes.'''
    return b'SPAMD/1.5 66 EX_NOINPUT\r\n'


@pytest.fixture
def ex_no_user():
    '''No user response in bytes.'''
    return b'SPAMD/1.5 67 EX_NOUSER\r\n'


@pytest.fixture
def ex_no_host():
    '''No host response in bytes.'''
    return b'SPAMD/1.5 68 EX_NOHOST\r\n'


@pytest.fixture
def ex_unavailable():
    '''Unavailable response in bytes.'''
    return b'SPAMD/1.5 69 EX_UNAVAILABLE\r\n'


@pytest.fixture
def ex_software():
    '''Software exception response in bytes.'''
    return b'SPAMD/1.5 70 EX_SOFTWARE\r\n'


@pytest.fixture
def ex_os_err():
    '''Operating system error response in bytes.'''
    return b'SPAMD/1.5 71 EX_OSERR\r\n'


@pytest.fixture
def ex_os_file():
    '''Operating system file error in bytes.'''
    return b'SPAMD/1.5 72 EX_OSFILE\r\n'


@pytest.fixture
def ex_cant_create():
    '''Can't create response error in bytes.'''
    return b'SPAMD/1.5 73 EX_CANTCREAT\r\n'


@pytest.fixture
def ex_io_err():
    '''Input/output error response in bytes.'''
    return b'SPAMD/1.5 74 EX_IOERR\r\n'


@pytest.fixture
def ex_temp_fail():
    '''Temporary failure error response in bytes.'''
    return b'SPAMD/1.5 75 EX_TEMPFAIL\r\n'


@pytest.fixture
def ex_protocol():
    '''Protocol error response in bytes.'''
    return b'SPAMD/1.5 76 EX_PROTOCOL\r\n'


@pytest.fixture
def ex_no_perm():
    '''No permission error response in bytes.'''
    return b'SPAMD/1.5 77 EX_NOPERM\r\n'


@pytest.fixture
def ex_config():
    '''Configuration error response in bytes.'''
    return b'SPAMD/1.5 78 EX_CONFIG\r\n'


@pytest.fixture
def ex_timeout():
    '''Timeout error response in bytes.'''
    return b'SPAMD/1.5 79 EX_TIMEOUT\r\n'


# Mock fixtures for asyncio objects/functions

@pytest.fixture
def connection_refused():
    with patch('asyncio.open_connection', side_effect=[ConnectionRefusedError()]), \
         patch('asyncio.open_unix_connection', side_effect=[ConnectionRefusedError()]):
        yield


@pytest.fixture
def mock_connection(response_ok):
    from itertools import cycle

    reader = MagicMock(spec=asyncio.StreamReader)
    reader.read.side_effect = cycle([response_ok])
    writer = MagicMock(spec=asyncio.StreamWriter)

    with patch('aiospamc.connections.Connection.connection_string',
               return_value='MockConnectionString'), \
         patch('aiospamc.connections.Connection.open',
               return_value=(reader, writer)), \
         patch('aiospamc.connections.tcp_connection.TcpConnection.open',
               return_value=(reader, writer)), \
         patch('aiospamc.connections.unix_connection.UnixConnection.open',
               return_value=(reader, writer)):
        yield reader.read
