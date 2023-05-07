from functools import partial

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from aiospamc.cli import app
from aiospamc.client import Client
from aiospamc.incremental_parser import ResponseParser

runner = CliRunner()


def test_ping(mock_client, ip_address, tcp_port):
    result = runner.invoke(app, ["ping", "--host", ip_address, "--port", tcp_port])

    assert 0 == result.exit_code
    assert "EX_OK\n" == result.stdout
