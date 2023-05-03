import pytest
from typer.testing import CliRunner

from aiospamc.cli.commands import app

runner = CliRunner()


@pytest.mark.integration
def test_ping(spamd, ip_address, tcp_port):
    result = runner.invoke(app, ["ping", "--host", ip_address, "--port", tcp_port])

    assert 0 == result.exit_code
    assert "PONG\n" == result.stdout
