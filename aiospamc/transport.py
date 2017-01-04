#!/usr/bin/env python3
#pylint: disable=too-few-public-methods

'''Classes that define the interface for transport methods.'''


class Inbound:
    '''Object is able to create an instance from data coming in from the
    network.
    '''

    @classmethod
    def parse(cls, string):
        '''Parses a string and returns a class instance.

        Parameters
        ----------
        string : str
            The string object to be parsed.

        Returns
        -------
        object
            An instance of the class that inherits Inbound.
        '''

        raise NotImplementedError

class Outbound:
    '''Object is able to prepare itself to be sent out to the network.'''

    def __bytes__(self):
        return self.compose().encode()

    def __len__(self):
        return len(bytes(self))

    def compose(self):
        '''Create a bytes object representing the class instance.

        Returns
        -------
        bytes
            Bytes object of the class.
        '''

        raise NotImplementedError
