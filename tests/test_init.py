#!/usr/bin/env python

import aiospamc

import pytest


@pytest.mark.parametrize(
    "func_name",
    [
        "check",
        "headers",
        "ping",
        "process",
        "report",
        "report_if_spam",
        "symbols",
        "tell",
    ],
)
def test_functions(func_name):
    assert hasattr(aiospamc, func_name)
