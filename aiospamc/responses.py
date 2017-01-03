#!/usr/bin/env python3

import enum
import re

from aiospamc.content_man import BodyHeaderManager
from aiospamc.exceptions import BadResponse
from aiospamc.headers import header_from_string
from aiospamc.transport import Inbound


class SPAMDStatus(enum.IntEnum):
    def __new__(cls, value, description=''):
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

class SPAMDResponse(Inbound):
    request_pattern = re.compile(r'^\s*'
                                 r'(?P<protocol>SPAMD)/(?P<version>\d+\.\d+)'
                                 r'\s+'
                                 r'(?P<status>\d+)'
                                 r'\s+'
                                 r'(?P<message>.*)')

    @classmethod
    def parse(cls, response):
        request, *body = response.split('\r\n\r\n', 1)
        request, *headers = request.split('\r\n')

        # Process request
        match = cls.request_pattern.match(request)
        if match:
            request_match = match.groupdict()
        else:
            # Not a SPAMD response
            raise BadResponse

        protocol_version = request_match['version'].strip()
        status_code = SPAMDStatus(int(request_match['status']))
        message = request_match['message'].strip()
        header_list = []
        for header in headers[:-1]: # drop last element since it'll be an empty string
            header_obj = header_from_string(header)
            if header_obj:
                header_list.append(header_obj)

        if body != []:
            obj = cls(protocol_version, status_code, message, header_list, body[0])
        else:
            obj = cls(protocol_version, status_code, message, header_list)

        return obj

    def __repr__(self):
        resp_format = '{}(protocol_version={}, status_code={}, message={}, headers={}, body={})'
        
        return resp_format.format(self.__class__.__name__,
                                  self.protocol_version,
                                  self.status_code,
                                  self.message,
                                  self.headers,
                                  self.body)

    def __str__(self):
        if self.body:
            return 'SPAMD/{} {} {}\n{}\n{}'.format(self.protocol_version, self.status_code, self.message, ''.join(map(str, self.headers)), ''.join([self.body[:80], '...\n']))
        else:
            return 'SPAMD/{} {} {}\n{}'.format(self.protocol_version, self.status_code, self.message, ''.join(map(str, self.headers)))

    def __init__(self, protocol_version, status_code, message, headers = [], body = None):
        self.protocol_version = protocol_version
        self.status_code = status_code
        self.message = message
        self.headers = headers
        self.body = body
