#!/usr/bin/env python3

import pytest

from aiospamc.incremental_parser import Parser, States


@pytest.fixture
def delimiter():
    return b'\r\n'


def test_default_state(delimiter, mocker):
    p = Parser(delimiter=delimiter, status_parser=mocker.stub(), header_parser=mocker.stub(), body_parser=mocker.stub())

    assert p.state == States.Status


def test_status(delimiter, mocker):
    p = Parser(
        delimiter=delimiter,
        status_parser=mocker.Mock(return_value='test value'),
        header_parser=mocker.stub(),
        body_parser=mocker.stub()
    )
    p.buffer = b'left\r\nright'
    p.status()

    assert p.result['status'] == 'test value'
    assert p.state == States.Header
