#!/usr/bin/env python3

'''Collection of exceptions.'''


# Exceptions raised from the Client object
class ClientException(Exception):
    '''Base class for exceptions raised from the client.'''
    pass


class BadRequest(ClientException):
    '''Request is not in the expected format.'''
    pass


class BadResponse(ClientException):
    '''Response is not in the expected format.'''
    pass


# ConnectionManager and Connection object exceptions
class AIOSpamcConnectionException(Exception):
    '''Base class for exceptions from the connection.'''
    pass


class AIOSpamcConnectionFailed(AIOSpamcConnectionException):
    '''Connection failed.'''
    pass


class ResponseException(Exception):
    '''Base class for exceptions raised from a response.'''
    pass


class UsageException(ResponseException):
    '''Command line usage error.'''
    code = 64


class DataErrorException(ResponseException):
    '''Data format error.'''
    code = 65


class NoInputException(ResponseException):
    '''Cannot open input.'''
    code = 66


class NoUserException(ResponseException):
    '''Addressee unknown.'''
    code = 67


class NoHostException(ResponseException):
    '''Hostname unknown.'''
    code = 68


class UnavailableException(ResponseException):
    '''Service unavailable.'''
    code = 69


class InternalSoftwareException(ResponseException):
    '''Internal software error.'''
    code = 70


class OSErrorException(ResponseException):
    '''System error (e.g. can't fork the process).'''
    code = 71


class OSFileException(ResponseException):
    '''Critical operating system file missing.'''
    code = 72


class CantCreateException(ResponseException):
    '''Can't create (user) output file.'''
    code = 73


class IOErrorException(ResponseException):
    '''Input/output error.'''
    code = 74


class TemporaryFailureException(ResponseException):
    '''Temporary failure, user is invited to try again.'''
    code = 75


class ProtocolException(ResponseException):
    '''Remote error in protocol.'''
    code = 76


class NoPermissionException(ResponseException):
    '''Permission denied.'''
    code = 77


class ConfigException(ResponseException):
    '''Configuration error.'''
    code = 78


class TimeoutException(ResponseException):
    '''Read timeout.'''
    code = 79
