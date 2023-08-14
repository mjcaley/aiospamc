import asyncio
import json
from ssl import SSLError

import pytest
from loguru import logger
from pytest_mock import MockerFixture
from typer.testing import CliRunner

import aiospamc
from aiospamc.cli import (
    BAD_RESPONSE,
    CONNECTION_ERROR,
    IS_SPAM,
    NOT_SPAM,
    PING_SUCCESS,
    REPORT_FAILED,
    REVOKE_FAILED,
    SUCCESS,
    TIMEOUT_ERROR,
    UNEXPECTED_ERROR,
    CommandRunner,
    Output,
    app,
    read_message,
)
from aiospamc.client import Client
from aiospamc.connections import ConnectionManager
from aiospamc.exceptions import AIOSpamcConnectionFailed, ParseError
from aiospamc.incremental_parser import ResponseParser
from aiospamc.requests import Request
from aiospamc.responses import Response


@pytest.fixture
def gtube(spam, tmp_path):
    message = tmp_path / "gtube.msg"
    message.write_bytes(spam)

    return message


def test_cli_runner_init_defaults(fake_tcp_server):
    _, host, port = fake_tcp_server
    request = Request("PING")
    c = CommandRunner(
        Client(ConnectionManager.builder().with_tcp(host, port).build()), request
    )

    assert request == c.request
    assert None is c.response
    assert Output.Text == c.output
    assert None is c.exception
    assert SUCCESS == c.exit_code


async def test_cli_runner_run_success(fake_tcp_server, response_pong):
    resp, host, port = fake_tcp_server
    resp.response = response_pong
    expected = Response(**ResponseParser().parse(response_pong))

    request = Request("PING")
    c = CommandRunner(
        Client(ConnectionManager.builder().with_tcp(host, port).build()), request
    )
    result = await c.run()

    assert expected == result
    assert expected == c.response


def test_cli_runner_to_json(fake_tcp_server):
    _, host, port = fake_tcp_server
    request = Request("PING")
    expected = {
        "request": request.to_json(),
        "response": None,
        "exit_code": SUCCESS,
    }

    c = CommandRunner(
        Client(ConnectionManager.builder().with_tcp(host, port).build()), request
    )
    result = c.to_json()

    assert json.dumps(expected, indent=4) == result


def test_ping_json(mocker, fake_tcp_server, response_pong):
    resp, host, port = fake_tcp_server
    resp.response = response_pong
    request_spy = mocker.spy(Client, "request")
    runner = CliRunner()
    result = runner.invoke(
        app, ["ping", "--host", host, "--port", port, "--out", "json"]
    )
    expected = {
        "request": request_spy.call_args.args[1].to_json(),
        "response": request_spy.spy_return.to_json(),
        "exit_code": 0,
    }

    assert f"{json.dumps(expected, indent=4)}\n" == result.stdout


@pytest.mark.parametrize(
    "args",
    [
        ["forget"],
        ["learn", "--message-class", "spam"],
    ],
)
def test_command_with_message_json(mocker, fake_tcp_server, gtube, args):
    _, host, port = fake_tcp_server
    request_spy = mocker.spy(Client, "request")
    runner = CliRunner()
    result = runner.invoke(
        app, args + [str(gtube), "--host", host, "--port", port, "--out", "json"]
    )
    expected = {
        "request": request_spy.call_args.args[1].to_json(),
        "response": request_spy.spy_return.to_json(),
        "exit_code": 0,
    }

    assert f"{json.dumps(expected, indent=4)}\n" == result.stdout


def test_check_json(mocker: MockerFixture, fake_tcp_server, response_not_spam, gtube):
    resp, host, port = fake_tcp_server
    request_spy = mocker.spy(Client, "request")
    resp.response = response_not_spam
    runner = CliRunner()
    result = runner.invoke(
        app, ["check", str(gtube), "--host", host, "--port", port, "--out", "json"]
    )
    expected = {
        "request": request_spy.call_args.args[1].to_json(),
        "response": request_spy.spy_return.to_json(),
        "exit_code": 0,
    }

    assert f"{json.dumps(expected, indent=4)}\n" == result.stdout


def test_report_json(mocker, fake_tcp_server, response_reported, gtube):
    resp, host, port = fake_tcp_server
    resp.response = response_reported
    request_spy = mocker.spy(Client, "request")
    runner = CliRunner()
    result = runner.invoke(
        app, ["report", str(gtube), "--host", host, "--port", port, "--out", "json"]
    )
    expected = {
        "request": request_spy.call_args.args[1].to_json(),
        "response": request_spy.spy_return.to_json(),
        "exit_code": 0,
    }

    assert f"{json.dumps(expected, indent=4)}\n" == result.stdout


def test_revoke_json(mocker, fake_tcp_server, response_revoked, gtube):
    resp, host, port = fake_tcp_server
    resp.response = response_revoked
    request_spy = mocker.spy(Client, "request")
    runner = CliRunner()
    result = runner.invoke(
        app, ["revoke", str(gtube), "--host", host, "--port", port, "--out", "json"]
    )
    expected = {
        "request": request_spy.call_args.args[1].to_json(),
        "response": request_spy.spy_return.to_json(),
        "exit_code": 0,
    }

    assert f"{json.dumps(expected, indent=4)}\n" == result.stdout


def test_command_without_message_response_exception(fake_tcp_server, ex_usage):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = ex_usage
    result = runner.invoke(app, ["ping", "--host", host, "--port", port])

    assert 64 == result.exit_code
    assert "Response error from server: EX_USAGE\n" == result.stdout


@pytest.mark.parametrize(
    "args",
    [
        ["check"],
        ["forget"],
        ["learn", "--message-class", "spam"],
        ["report"],
        ["revoke"],
    ],
)
def test_command_with_message_response_exception(
    fake_tcp_server, ex_usage, gtube, args
):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = ex_usage
    result = runner.invoke(app, args + [str(gtube), "--host", host, "--port", port])

    assert 64 == result.exit_code
    assert "Response error from server: EX_USAGE\n" == result.stdout


def test_command_without_message_parser_exception(fake_tcp_server, response_invalid):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_invalid
    result = runner.invoke(app, ["ping", "--host", host, "--port", port])

    assert BAD_RESPONSE == result.exit_code
    assert "Error parsing response\n" == result.stdout


@pytest.mark.parametrize(
    "args",
    [
        ["check"],
        ["forget"],
        ["learn", "--message-class", "spam"],
        ["report"],
        ["revoke"],
    ],
)
def test_command_with_message_parser_exception(
    fake_tcp_server, gtube, args, response_invalid
):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_invalid
    result = runner.invoke(app, args + [str(gtube), "--host", host, "--port", port])

    assert BAD_RESPONSE == result.exit_code
    assert "Error parsing response\n" == result.stdout


def test_command_without_message_timeout_exception(fake_tcp_server):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.sleep = 10
    result = runner.invoke(
        app, ["ping", "--timeout", 0.1, "--host", host, "--port", port]
    )

    assert TIMEOUT_ERROR == result.exit_code
    assert "Error: timeout\n" == result.stdout


@pytest.mark.parametrize(
    "args",
    [
        ["check"],
        ["forget"],
        ["learn", "--message-class", "spam"],
        ["report"],
        ["revoke"],
    ],
)
def test_command_with_message_timeout_exception(mock_client_raises, gtube, args):
    runner = CliRunner()
    mock_client_raises(asyncio.TimeoutError())
    result = runner.invoke(app, args + [str(gtube)])

    assert TIMEOUT_ERROR == result.exit_code
    assert "Error: timeout\n" == result.stdout


@pytest.mark.parametrize(
    "raises", [AIOSpamcConnectionFailed(), OSError(), ConnectionError(), SSLError()]
)
def test_command_without_message_connection_exception(mock_client_raises, raises):
    runner = CliRunner()
    mock_client_raises(raises)
    result = runner.invoke(app, ["ping"])

    assert CONNECTION_ERROR == result.exit_code
    assert "Error: Connection error\n" == result.stdout


@pytest.mark.parametrize(
    "raises", [AIOSpamcConnectionFailed(), OSError(), ConnectionError(), SSLError()]
)
@pytest.mark.parametrize(
    "args",
    [
        ["check"],
        ["forget"],
        ["learn", "--message-class", "spam"],
        [
            "report",
        ],
        [
            "revoke",
        ],
    ],
)
def test_command_with_message_connection_exception(
    mock_client_raises, raises, gtube, args
):
    runner = CliRunner()
    mock_client_raises(raises)
    result = runner.invoke(app, args + [str(gtube)])

    assert CONNECTION_ERROR == result.exit_code
    assert "Error: Connection error\n" == result.stdout


def test_ping(fake_tcp_server, response_pong):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_pong
    result = runner.invoke(app, ["ping", "--host", host, "--port", port])

    assert PING_SUCCESS == result.exit_code
    assert "PONG\n" == result.stdout


def test_check_spam(fake_tcp_server, response_spam_header, gtube):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_spam_header
    result = runner.invoke(app, ["check", str(gtube), "--host", host, "--port", port])

    assert IS_SPAM == result.exit_code
    assert "1000.0/1.0\n" == result.stdout


def test_check_ham(fake_tcp_server, response_not_spam, gtube):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_not_spam
    result = runner.invoke(app, ["check", str(gtube), "--host", host, "--port", port])

    assert NOT_SPAM == result.exit_code
    assert "0.0/1.0\n" == result.stdout


def test_check_no_spam_header(fake_tcp_server, response_with_body, gtube):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_with_body
    result = runner.invoke(
        app,
        [
            "check",
            str(gtube),
            "--host",
            host,
            "--port",
            port,
        ],
    )

    assert UNEXPECTED_ERROR == result.exit_code
    assert "Could not find 'Spam' header\n" == result.stdout


def test_learn_success(fake_tcp_server, response_learned, gtube):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_learned
    result = runner.invoke(app, ["learn", str(gtube), "--host", host, "--port", port])

    assert SUCCESS == result.exit_code
    assert "Message successfully learned\n" == result.stdout


def test_learn_already_learned(fake_tcp_server, response_tell, gtube):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_tell
    result = runner.invoke(app, ["learn", str(gtube), "--host", host, "--port", port])

    assert SUCCESS == result.exit_code
    assert "Message was already learned\n" == result.stdout


def test_forget_success(fake_tcp_server, response_forgotten, gtube):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_forgotten
    result = runner.invoke(app, ["forget", str(gtube), "--host", host, "--port", port])

    assert SUCCESS == result.exit_code
    assert "Message successfully forgotten\n" == result.stdout


def test_learn_already_forgotten(fake_tcp_server, response_tell, gtube):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_tell
    result = runner.invoke(app, ["forget", str(gtube), "--host", host, "--port", port])

    assert SUCCESS == result.exit_code
    assert "Message was already forgotten\n" == result.stdout


def test_report_success(fake_tcp_server, response_reported, gtube):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_reported
    result = runner.invoke(app, ["report", str(gtube), "--host", host, "--port", port])

    assert SUCCESS == result.exit_code
    assert "Message successfully reported\n" == result.stdout


def test_report_failed(fake_tcp_server, response_tell, gtube):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_tell
    result = runner.invoke(app, ["report", str(gtube), "--host", host, "--port", port])

    assert REPORT_FAILED == result.exit_code
    assert "Unable to report message\n" == result.stdout


def test_revoke_success(fake_tcp_server, response_revoked, gtube):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_revoked
    result = runner.invoke(app, ["revoke", str(gtube), "--host", host, "--port", port])

    assert SUCCESS == result.exit_code
    assert "Message successfully revoked\n" == result.stdout


def test_revoke_failed(fake_tcp_server, response_tell, gtube):
    resp, host, port = fake_tcp_server
    runner = CliRunner()
    resp.response = response_tell
    result = runner.invoke(app, ["revoke", str(gtube), "--host", host, "--port", port])

    assert REVOKE_FAILED == result.exit_code
    assert "Unable to revoke message\n" == result.stdout


def test_version():
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])

    assert f"{aiospamc.__version__}\n" == result.stdout


def test_debug(mocker: MockerFixture):
    logger_spy = mocker.spy(logger, "enable")
    runner = CliRunner()
    runner.invoke(app, ["--debug"])

    assert ("aiospamc",) == logger_spy.call_args.args


def test_read_message_stdin(mocker):
    mock_buffer = mocker.patch("sys.stdin.buffer.read")
    mock_buffer.return_value = b"test"
    result = read_message(None)

    assert b"test" == result


def test_read_message_not_interactive(mocker: MockerFixture):
    mock_file = mocker.MagicMock()
    mock_file.read.return_value = b"test"
    result = read_message(mock_file)

    assert b"test" == result
