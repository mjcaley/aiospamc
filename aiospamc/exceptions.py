#!/usr/bin/env python3

'''Collection of exceptions.'''


class HeaderCantParse(Exception):
    '''Header is unable to parse the given string.'''
    pass

class BadResponse(Exception):
    '''Response is not in the expected format.'''
    pass

class SPAMDConnectionRefused(Exception):
    '''Server refused connection.'''
    pass
