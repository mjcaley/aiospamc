#!/usr/bin/env python3

import pytest

import asynctest


@pytest.fixture
def stub_connection():
    def inner(return_value=None, side_effect=None):
        connection = asynctest.Mock()
        connection.send = asynctest.CoroutineMock()
        connection.receive = asynctest.CoroutineMock(return_value=return_value, side_effect=side_effect)

        return connection
    return inner


@pytest.fixture
def stub_connection_manager(stub_connection):
    def inner(return_value=None, side_effect=None):
        stub = stub_connection(return_value=return_value, side_effect=side_effect)
        context_manager = asynctest.MagicMock()
        context_manager.__aenter__ = asynctest.CoroutineMock(
            return_value=stub
        )
        context_manager.__aexit__ = asynctest.CoroutineMock()

        manager = asynctest.MagicMock()
        manager.new_connection = asynctest.Mock(return_value=context_manager)
        manager.connection_stub = stub

        return manager

    return inner
