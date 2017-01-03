#!/usr/bin/env python3

from aiospamc.content_man import BodyHeaderManager
from aiospamc.transport import Outbound


class SPAMCRequest(BodyHeaderManager, Outbound):
    '''SPAMC request object.'''

    protocol = b'SPAMC/1.5'
    request = b'%(verb)b %(protocol)b\r\n%(headers)b\r\n%(body)b'

    def __init__(self, verb, body=None, *headers):
        ''''''

        self.verb = verb.encode()
        super().__init__(body, *headers)

    def __bytes__(self):
        return self.compose()

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__, self.verb, self._headers, self.body)

    def compose(self):
        '''Composes a request based on the verb and headers that are currently set.'''

        request = self.request % {b'verb': self.verb,
                                  b'protocol': self.protocol,
                                  b'headers': b''.join(map(bytes, self._headers.values())),
                                  b'body' : self.body if self.body else b''}

        return request

class Check(SPAMCRequest):
    def __init__(self, message, *headers):
        super().__init__('CHECK', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class Headers(SPAMCRequest):
    def __init__(self, message, *headers):
        super().__init__('HEADERS', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class Ping(SPAMCRequest):
    def __init__(self, *headers):
        super().__init__('PING', body=None, *headers)

    def __repr__(self):
        return '{}(headers={})'.format(self.__class__.__name__, self._headers)

class Process(SPAMCRequest):
    def __init__(self, message, *headers):
        super().__init__('PROCESS', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class Report(SPAMCRequest):
    def __init__(self, message, *headers):
        super().__init__('REPORT', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class ReportIfSpam(SPAMCRequest):
    def __init__(self, message, *headers):
        super().__init__('REPORT_IFSPAM', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class Symbols(SPAMCRequest):
    def __init__(self, message, *headers):
        super().__init__('SYMBOLS', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class Tell(SPAMCRequest):
    def __init__(self, message, *headers):
        super().__init__('TELL', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)
