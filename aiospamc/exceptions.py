#!/usr/bin/env python3

'''Collection of exceptions.'''


class ClientException(Exception):
    '''Base class for exceptions raised from the client.'''
    pass

class HeaderCantParse(ClientException):
    '''Header is unable to parse the given string.'''
    pass

class BadRequest(ClientException):
    '''Request is not in the expected format.'''
    pass

class BadResponse(ClientException):
    '''Response is not in the expected format.'''
    pass

class SPAMDConnectionRefused(ClientException):
    '''Server refused connection.'''
    pass


class ResponseException(Exception):
    '''Base class for exceptions raised from a response.'''
    pass

class ExUsage(ResponseException):
    '''Command line usage error.'''
    code = 64

class ExDataErr(ResponseException):
    '''Data format error.'''
    code = 65

class ExNoInput(ResponseException):
    '''Cannot open input.'''
    code = 66

class ExNoUser(ResponseException):
    '''Addressee unknown.'''
    code = 67

class ExNoHost(ResponseException):
    '''Hostname unknown.'''
    code = 68

class ExUnavailable(ResponseException):
    '''Service unavailable.'''
    code = 69

class ExSoftware(ResponseException):
    '''Internal software error.'''
    code = 70

class ExOSErr(ResponseException):
    '''System error (e.g. can't fork the process).'''
    code = 71

class ExOSFile(ResponseException):
    '''Critical operating system file missing.'''
    code = 72

class ExCantCreat(ResponseException):
    '''Can't create (user) output file.'''
    code = 73

class ExIOErr(ResponseException):
    '''Input/output error.'''
    code = 74

class ExTempFail(ResponseException):
    '''Temporary failure, user is invited to try again.'''
    code = 75

class ExProtocol(ResponseException):
    '''Remote error in protocol.'''
    code = 76

class ExNoPerm(ResponseException):
    '''Permission denied.'''
    code = 77

class ExConfig(ResponseException):
    '''Configuration error.'''
    code = 78

class ExTimeout(ResponseException):
    '''Read timeout.'''
    code = 79
