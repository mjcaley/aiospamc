#!/usr/bin/env python3

import pytest

from aiospamc.parser import remove_empty


@pytest.mark.parametrize('test_input,expected',
    [(None, False),
     ('',   False),
     (' ',  False),
     ('\r', False),
     ('\n', False),
     ('a',  True),
     (3,    True)])
def test_none(test_input, expected):
    result = remove_empty([1, test_input, 2])

    assert (test_input in result) == expected
