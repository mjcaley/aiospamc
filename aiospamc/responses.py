#!/usr/bin/env python3

'''Contains classes used for responses.'''

import enum
import re

from aiospamc.content_man import BodyHeaderManager
from aiospamc.exceptions import BadResponse
from aiospamc.headers import header_from_string
from aiospamc.transport import Inbound


class Status(enum.IntEnum):
    '''Enumeration of status codes that the SPAMD will accompany with a
    response.

    Reference: https://svn.apache.org/repos/asf/spamassassin/trunk/spamd/spamd.raw
    Look for the %resphash variable.
    '''

    #pylint: disable=C0326
    def __new__(cls, value, description=''):
        #pylint: disable=protected-access
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.description = description

        return obj

    EX_OK           = 0,  'No problems'
    EX_USAGE        = 64, 'Command line usage error'
    EX_DATAERR      = 65, 'Data format error'
    EX_NOINPUT      = 66, 'Cannot open input'
    EX_NOUSER       = 67, 'Addressee unknown'
    EX_NOHOST       = 68, 'Host name unknown'
    EX_UNAVAILABLE  = 69, 'Service unavailable'
    EX_SOFTWARE     = 70, 'Internal software error'
    EX_OSERR        = 71, 'System error (e.g., can\'t fork)'
    EX_OSFILE       = 72, 'Critical OS file missing'
    EX_CANTCREAT    = 73, 'Can\'t create (user) output file'
    EX_IOERR        = 74, 'Input/output error'
    EX_TEMPFAIL     = 75, 'Temp failure; user is invited to retry'
    EX_PROTOCOL     = 76, 'Remote error in protocol'
    EX_NOPERM       = 77, 'Permission denied'
    EX_CONFIG       = 78, 'Configuration error'
    EX_TIMEOUT      = 79, 'Read timeout'

class Response(BodyHeaderManager, Inbound):
    '''Class to encapsulate response.

    Attributes
    ----------
    protocol_version : str
        Protocol version given by the response.
    status_code : aiospamc.responess.Status
        Status code give by the response.
    message : str
        Message accompanying the status code.
    body : str
        Contents of the response body.
    headers : tuple of aiospamc.headers.Header
        Collection of headers to be added.  If it contains an instance of
        aiospamc.headers.Compress then the body is automatically
        compressed.
    '''

    #pylint: disable=too-few-public-methods
    _response_pattern = re.compile(r'^\s*'
                                   r'(?P<protocol>SPAMD)/(?P<version>\d+\.\d+)'
                                   r'\s+'
                                   r'(?P<status>\d+)'
                                   r'\s+'
                                   r'(?P<message>.*)')
    '''Regular expression pattern to match the response.  Protocol will match
    the phrase 'SPAMD', version will match with the style '1.0', status will
    match an integer.  The message will match all characters up until the next
    newline.
    '''
    _response_string = 'SPAMD/{version} {status} {message}\r\n{headers}\r\n{body}'
    '''String used for composing a response.'''

    @classmethod
    def parse(cls, response):
        request, *body = response.split('\r\n\r\n', 1)
        request, *headers = request.split('\r\n')

        # Process request
        match = cls._response_pattern.match(request)
        if match:
            response_match = match.groupdict()
        else:
            # Not a SPAMD response
            raise BadResponse

        protocol_version = response_match['version'].strip()
        status_code = Status(int(response_match['status']))
        message = response_match['message'].strip()

        header_tuple = cls._parse_headers(headers)

        obj = cls(protocol_version, status_code, message, body[0] if body else None, *header_tuple)

        return obj

    @staticmethod
    def _parse_headers(headers):
        if not headers:
            return ()
        if headers[-1] == '':
            headers.pop()
        return tuple(header_from_string(header) for header in headers)

    def __init__(self, protocol_version, status_code, message, body=None, *headers):
        '''Response constructor.

        Parameters
        ----------
        protocol_version : str
            Version reported by the SPAMD service response.
        status_code : aiospamc.responses.Status
            Success or error code.
        message : str
            Message associated with status code.
        body : str
            String representation of the body.  An instance of the
            aiospamc.headers.ContentLength will be automatically added.
        headers : tuple of aiospamc.headers.Header
            Collection of headers to be added.  If it contains an instance of
            aiospamc.headers.Compress then the body is automatically
            compressed.
        '''

        self.protocol_version = protocol_version
        self.status_code = status_code
        self.message = message
        super().__init__(body, *headers)

    def __repr__(self):
        resp_format = ('{}(protocol_version=\'{}\', '
                       'status_code={}, '
                       'message=\'{}\', '
                       'headers={}, '
                       'body={})')

        return resp_format.format(self.__class__.__name__,
                                  self.protocol_version,
                                  str(self.status_code),
                                  self.message,
                                  tuple(self._headers.values()),
                                  self.body)

    def __str__(self):
        return self._response_string.format(version=self.protocol_version,
                                            status=self.status_code,
                                            message=self.message,
                                            headers=''.join(map(str, self._headers)),
                                            body=''.join([self.body[:80], '...\n']) if self.body else '')
