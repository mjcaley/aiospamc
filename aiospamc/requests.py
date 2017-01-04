#!/usr/bin/env python3

'''Contains all requests that can be made to the SPAMD service.'''

from aiospamc.content_man import BodyHeaderManager
from aiospamc.transport import Outbound


class SPAMCRequest(BodyHeaderManager, Outbound):
    '''SPAMC request object.

    Attributes
    ----------
    verb : str
        Method name of the request.
    body : str
        String representation of the body.  An instance of the
        aiospamc.headers.ContentLength will be automatically added.
    headers : tuple of aiospamc.headers.Header
        Collection of headers to be added.  If it contains an instance of
        aiospamc.headers.Compress then the body is automatically
        compressed.
    '''

    protocol = b'SPAMC/1.5'
    request = b'%(verb)b %(protocol)b\r\n%(headers)b\r\n%(body)b'

    def __init__(self, verb, body=None, *headers):
        '''SPAMCRequest constructor.

        Parameters
        ----------
        verb : str
            Method name of the request.
        body : str
            String representation of the body.  An instance of the
            aiospamc.headers.ContentLength will be automatically added.
        headers : tuple of aiospamc.headers.Header
            Collection of headers to be added.  If it contains an instance of
            aiospamc.headers.Compress then the body is automatically
            compressed.
        '''

        self.verb = verb.encode()
        super().__init__(body, *headers)

    def __bytes__(self):
        return self.compose()

    def __repr__(self):
        return '{}({}, {}, {})'.format(self.__class__.__name__,
                                       self.verb,
                                       self._headers,
                                       self.body)

    def compose(self):
        request = self.request % {b'verb': self.verb,
                                  b'protocol': self.protocol,
                                  b'headers': b''.join(map(bytes, self._headers.values())),
                                  b'body' : self.body if self.body else b''}

        return request

class Check(SPAMCRequest):
    '''CHECK request.  Send a message to be checked whether it's spam or not.
    The response will contain a Spam header.
    '''

    def __init__(self, message, *headers):
        super().__init__('CHECK', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class Headers(SPAMCRequest):
    '''HEADERS request.  Send a message to be checked whether it's spam or not.
    Response will contain a Spam header and the body will contain the modified
    email headers.
    '''

    def __init__(self, message, *headers):
        super().__init__('HEADERS', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class Ping(SPAMCRequest):
    '''PING request.  Send a request to see if the SPAMD service is alive.'''

    def __init__(self, *headers):
        super().__init__('PING', body=None, *headers)

    def __repr__(self):
        return '{}(headers={})'.format(self.__class__.__name__, self._headers)

class Process(SPAMCRequest):
    '''PROCESS request.  Send a message to be checked whether it's spam or not.
    Response will contain a Spam header and the body will contain the modified
    message.
    '''

    def __init__(self, message, *headers):
        super().__init__('PROCESS', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class Report(SPAMCRequest):
    '''REPORT request.  Send a message to be checked whether it's spam or not.
    Response will contain a Spam header and the body will contain a report.
    '''

    def __init__(self, message, *headers):
        super().__init__('REPORT', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class ReportIfSpam(SPAMCRequest):
    '''REPORT_IFSPAM request.  Send a message to be checked whether it's spam
    or not.  Response will contain a Spam header and the body will contain a
    report if it is spam.
    '''

    def __init__(self, message, *headers):
        super().__init__('REPORT_IFSPAM', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class Symbols(SPAMCRequest):
    '''SYMBOLS request.  Send a message to be checked whether it's spam or not.
    Response will contain a Spam header and the body will contain a comma
    separated list of SpamAssassin rules that were hit.
    '''

    def __init__(self, message, *headers):
        super().__init__('SYMBOLS', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)

class Tell(SPAMCRequest):
    '''TELL request.  Instruct the SPAMD service to perform an action on a
    message (learning, reporting, forgetting, and/or revoking).  The SPAMD
    service must have --allow-tell.
    '''

    def __init__(self, message, *headers):
        super().__init__('TELL', message, *headers)

    def __repr__(self):
        return '{}(message={}, headers={})'.format(self.__class__.__name__,
                                                   self.body,
                                                   self._headers)
