#!/usr/bin/env python3

import pytest

from aiospamc.transport import Inbound, Outbound


def test_inbound_parse():
    with pytest.raises(NotImplementedError):
        Inbound.parse('')

def test_outbound_compose():
    outbound = Outbound()
    with pytest.raises(NotImplementedError):
        outbound.compose()
