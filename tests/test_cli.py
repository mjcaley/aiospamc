import asyncio
import json
from functools import partial
from pathlib import Path
from ssl import SSLError

import pytest
from loguru import logger
from pytest_mock import MockerFixture
from typer.testing import CliRunner

import aiospamc
from aiospamc.cli import (
    CONNECTION_ERROR,
    IS_SPAM,
    NOT_SPAM,
    PARSE_ERROR,
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
from aiospamc.exceptions import AIOSpamcConnectionFailed, ParseError
from aiospamc.incremental_parser import ResponseParser
from aiospamc.requests import Request
from aiospamc.responses import Response


@pytest.fixture
def gtube(spam, tmp_path):
    message = tmp_path / "gtube.msg"
    message.write_bytes(spam)

    return message


def test_cli_runner_init_defaults():
    request = Request("PING")
    c = CommandRunner(request)

    assert request == c.request
    assert None is c.response
    assert Output.Text == c.output
    assert None is c.exception
    assert SUCCESS == c.exit_code


async def test_cli_runner_run_success(mock_client_response, response_pong, ip_address):
    mock_client_response(response_pong)
    expected = Response(**ResponseParser().parse(response_pong))

    request = Request("PING")
    c = CommandRunner(request)
    result = await c.run(ip_address)

    assert expected == result
    assert expected == c.response


def test_cli_runner_to_json():
    request = Request("PING")
    expected = {
        "request": request.to_json(),
        "response": None,
        "exit_code": SUCCESS,
    }

    c = CommandRunner(request)
    result = c.to_json()

    assert json.dumps(expected, indent=4) == result


def test_command_without_message_json(mock_client, response_ok):
    expected = {
        "request": {"verb": "PING", "version": "1.5", "headers": {}, "body": ""},
        "response": Response(**ResponseParser().parse(response_ok)).to_json(),
        "exit_code": 0,
    }
    runner = CliRunner()
    result = runner.invoke(app, ["ping", "--out", "json"])

    assert SUCCESS == result.exit_code
    assert f"{json.dumps(expected, indent=4)}\n" == result.stdout


@pytest.mark.parametrize(
    "args",
    [
        ["check"],
        ["forget"],
        ["learn", "--message-class", "spam"],
        ["report", "--message-class", "spam"],
        ["revoke", "--message-class", "spam"],
    ],
)
def test_command_with_message_response_exception(
    mock_client_response, ex_usage, spam, gtube, args
):
    runner = CliRunner()
    mock_client_response(ex_usage)
    result = runner.invoke(app, args + [str(gtube)])

    assert 64 == result.exit_code
    assert "Response error from server: EX_USAGE\n" == result.stdout


def test_command_without_message_response_exception(mock_client_response, ex_usage):
    runner = CliRunner()
    mock_client_response(ex_usage)
    result = runner.invoke(app, ["ping"])

    assert 64 == result.exit_code
    assert "Response error from server: EX_USAGE\n" == result.stdout


@pytest.mark.parametrize(
    "args",
    [
        ["check"],
        ["forget"],
        ["learn", "--message-class", "spam"],
        ["report", "--message-class", "spam"],
        ["revoke", "--message-class", "spam"],
    ],
)
def test_command_with_message_response_exception(
    mock_client_response, ex_usage, spam, gtube, args
):
    runner = CliRunner()
    mock_client_response(ex_usage)
    result = runner.invoke(app, args + [str(gtube)])

    assert 64 == result.exit_code
    assert "Response error from server: EX_USAGE\n" == result.stdout


def test_command_without_message_parser_exception(mock_client_raises):
    runner = CliRunner()
    mock_client_raises(ParseError())
    result = runner.invoke(app, ["ping"])

    assert PARSE_ERROR == result.exit_code
    assert "Error parsing response\n" == result.stdout


@pytest.mark.parametrize(
    "args",
    [
        ["check"],
        ["forget"],
        ["learn", "--message-class", "spam"],
        ["report", "--message-class", "spam"],
        ["revoke", "--message-class", "spam"],
    ],
)
def test_command_with_message_parser_exception(mock_client_raises, spam, gtube, args):
    runner = CliRunner()
    mock_client_raises(ParseError())
    result = runner.invoke(app, args + [str(gtube)])

    assert PARSE_ERROR == result.exit_code
    assert "Error parsing response\n" == result.stdout


def test_command_without_message_timeout_exception(mock_client_raises):
    runner = CliRunner()
    mock_client_raises(asyncio.TimeoutError())
    result = runner.invoke(app, ["ping"])

    assert TIMEOUT_ERROR == result.exit_code
    assert "Error: timeout\n" == result.stdout


@pytest.mark.parametrize(
    "args",
    [
        ["check"],
        ["forget"],
        ["learn", "--message-class", "spam"],
        ["report", "--message-class", "spam"],
        ["revoke", "--message-class", "spam"],
    ],
)
def test_command_with_message_timeout_exception(mock_client_raises, spam, gtube, args):
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
        ["report", "--message-class", "spam"],
        ["revoke", "--message-class", "spam"],
    ],
)
def test_command_with_message_connection_exception(
    mock_client_raises, raises, spam, gtube, args
):
    runner = CliRunner()
    mock_client_raises(raises)
    result = runner.invoke(app, args + [str(gtube)])

    assert CONNECTION_ERROR == result.exit_code
    assert "Error: Connection error\n" == result.stdout


def test_ping(mock_client_response, response_pong):
    runner = CliRunner()
    mock_client_response(response_pong)
    result = runner.invoke(app, ["ping"])

    assert PING_SUCCESS == result.exit_code
    assert "PONG\n" == result.stdout


def test_check_spam(mock_client_response, response_spam_header, gtube):
    runner = CliRunner()
    mock_client_response(response_spam_header)
    result = runner.invoke(app, ["check", str(gtube)])

    assert IS_SPAM == result.exit_code
    assert "1000.0/1.0\n" == result.stdout


def test_check_ham(mock_client_response, response_not_spam, gtube):
    runner = CliRunner()
    mock_client_response(response_not_spam)
    result = runner.invoke(app, ["check", str(gtube)])

    assert NOT_SPAM == result.exit_code
    assert "0.0/1.0\n" == result.stdout


def test_check_no_spam_header(mock_client_response, response_with_body, gtube):
    runner = CliRunner()
    mock_client_response(response_with_body)
    result = runner.invoke(app, ["check", str(gtube)])

    assert UNEXPECTED_ERROR == result.exit_code
    assert "Could not find 'Spam' header\n" == result.stdout


def test_learn_success(mock_client_response, response_learned, gtube):
    runner = CliRunner()
    mock_client_response(response_learned)
    result = runner.invoke(app, ["learn", str(gtube)])

    assert SUCCESS == result.exit_code
    assert "Message successfully learned\n" == result.stdout


def test_learn_already_learned(mock_client_response, response_tell, gtube):
    runner = CliRunner()
    mock_client_response(response_tell)
    result = runner.invoke(app, ["learn", str(gtube)])

    assert SUCCESS == result.exit_code
    assert "Message was already learned\n" == result.stdout


def test_forget_success(mock_client_response, response_forgotten, gtube):
    runner = CliRunner()
    mock_client_response(response_forgotten)
    result = runner.invoke(app, ["forget", str(gtube)])

    assert SUCCESS == result.exit_code
    assert "Message successfully forgotten\n" == result.stdout


def test_learn_already_forgotten(mock_client_response, response_tell, gtube):
    runner = CliRunner()
    mock_client_response(response_tell)
    result = runner.invoke(app, ["forget", str(gtube)])

    assert SUCCESS == result.exit_code
    assert "Message was already forgotten\n" == result.stdout


def test_report_success(mock_client_response, response_reported, gtube):
    runner = CliRunner()
    mock_client_response(response_reported)
    result = runner.invoke(app, ["report", str(gtube)])

    assert SUCCESS == result.exit_code
    assert "Message successfully reported\n" == result.stdout


def test_report_failed(mock_client_response, response_tell, gtube):
    runner = CliRunner()
    mock_client_response(response_tell)
    result = runner.invoke(app, ["report", str(gtube)])

    assert REPORT_FAILED == result.exit_code
    assert "Unable to report message\n" == result.stdout


def test_revoke_success(mock_client_response, response_revoked, gtube):
    runner = CliRunner()
    mock_client_response(response_revoked)
    result = runner.invoke(app, ["revoke", str(gtube)])

    assert SUCCESS == result.exit_code
    assert "Message successfully revoked\n" == result.stdout


def test_revoke_failed(mock_client_response, response_tell, gtube):
    runner = CliRunner()
    mock_client_response(response_tell)
    result = runner.invoke(app, ["revoke", str(gtube)])

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


def test_read_message_interactive(mocker):
    mock_file = mocker.MagicMock()
    mock_file.isatty.return_value = False
    mock_file.read.return_value = b"test"
    result = read_message(mock_file)

    assert b"test" == result


def test_read_message_not_interactive(mocker):
    mock_file = mocker.MagicMock()
    mock_file.isatty.return_value = True

    with pytest.raises(IOError):
        read_message(mock_file)
