"""CLI commands."""

import asyncio
import json
import ssl
import sys
from enum import Enum
from typing import Any, Optional

import typer
from loguru import logger

from aiospamc.exceptions import AIOSpamcConnectionFailed, ParseError
from aiospamc.header_values import (
    ActionOption,
    MessageClassOption,
    MessageClassValue,
    SetOrRemoveValue,
)

from . import __version__
from .client import Client, Request
from .connections import Timeout
from .responses import Response, ResponseException


def run():
    try:
        from .cli import app
    except ImportError:
        print("The optional 'cli' needed")
        sys.exit(-1)

    app()


app = typer.Typer()


class Output(str, Enum):
    """Output formats."""

    Json = "json"
    Text = "text"


# Exit codes
SUCCESS = 0
IS_SPAM = 1
PARSE_ERROR = 3
TIMEOUT_ERROR = 4
CONNECTION_ERROR = 5
UNEXPECTED_ERROR = 6


class CommandRunner:
    def __init__(
        self,
        request: Request,
        debug: bool = False,
        output: Output = Output.Text,
    ):
        self.request = request
        self.response: Optional[Response] = None
        self.debug = debug
        self.output = output
        self.client = Client()

        self.exception: Optional[Exception] = None
        self.exit_code = SUCCESS

        self._logger = logger.bind(request=request)

    async def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        socket_path: Optional[str] = None,
        timeout: Optional[Timeout] = None,
        verify: Any = None,
    ) -> Response:
        ssl_context = self.client.ssl_context_factory(verify)
        connection = self.client.connection_factory(
            host, port, socket_path, timeout, ssl_context
        )
        parser = self.client.parser_factory()
        self._logger = self._logger.bind(host=host, port=port, socket_path=socket_path)
        self._logger.info("Sending request")

        ssl_context = self.client.ssl_context_factory(verify)
        connection = self.client.connection_factory(
            host, port, socket_path, timeout, ssl_context
        )
        parser = self.client.parser_factory()
        try:
            response = await self.client.request(self.request, connection, parser)
        except ResponseException as e:
            self._logger = self._logger.bind(response=e.response)
            self._logger.exception(e)
            self.response = e.response
            self.exit_code = int(self.response.status_code)
            self.exception = e
            self.exit(self.response.message, True)
        except ParseError as e:
            self._logger.exception(e)
            self.exit_code = PARSE_ERROR
            self.exception = e
            self.exit("Error parsing response", True)
        except asyncio.TimeoutError as e:
            self._logger.exception(e)
            self.exit_code = TIMEOUT_ERROR
            self.exception = e
            self.exit("Error: timeout", True)
        except (AIOSpamcConnectionFailed, OSError, ConnectionError, ssl.SSLError) as e:
            self._logger.exception(e)
            self.exit_code = CONNECTION_ERROR
            self.exception = e
            self.exit("Error: Connection error", True)

        self._logger = self._logger.bind(response=response)
        self._logger.info("Successfully recieved request")
        self.response = response

        return response

    def to_json(self) -> str:
        obj = {
            "request": self.request.to_json(),
            "response": self.response.to_json() if self.response is not None else None,
            "exit_code": self.exit_code,
        }

        return json.dumps(obj, indent=4)

    def exit(self, message: str, err=False):
        if self.output == Output.Text:
            typer.echo(message, err=err)
        else:
            typer.echo(self.to_json())
        raise typer.Exit(self.exit_code)


@app.command()
def ping(
    host: str = typer.Option(
        "localhost", help="Hostname to use when connecting using TCP"
    ),
    port: int = typer.Option(783, help="Port to use when connecting using TCP"),
    socket_path: str = typer.Option(
        None, help="Path to use when connecting using Unix sockets"
    ),
    ssl: bool = typer.Option(
        None,
        help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
        envvar="AIOSPAMC_CERT_FILE",
    ),
    timeout: float = typer.Option(10, help="Timeout in seconds"),
    out: Output = typer.Option(Output.Text.value, help="Output format for stdout"),
    debug: bool = typer.Option(False, help="Debug information"),
):
    """Pings the SpamAssassin daemon.

    A successful pong exits with code 0.
    """

    request = Request("PING")
    runner = CommandRunner(request, debug, out)
    response = asyncio.run(runner.run(host, port, socket_path, Timeout(timeout), ssl))
    runner.exit(response.message)


def read_message(file) -> bytes:
    if not file.isatty():
        return file.read()

    raise IOError


@app.command()
def check(
    message: Optional[typer.FileBinaryRead] = typer.Argument(
        sys.stdin.buffer, help="Message to check, [default: stdin]"
    ),
    host: str = typer.Option(
        "localhost", help="Hostname to use when connecting using TCP"
    ),
    port: int = typer.Option(783, help="Port to use when connecting using TCP"),
    socket_path: str = typer.Option(
        None, help="Path to use when connecting using Unix sockets"
    ),
    ssl: bool = typer.Option(
        None,
        help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
        envvar="AIOSPAMC_CERT_FILE",
    ),
    timeout: float = typer.Option(10, help="Timeout in seconds"),
    out: Output = typer.Option(Output.Text.value, help="Output format for stdout"),
    debug: bool = typer.Option(False, help="Debug information"),
):
    """Submits a message to SpamAssassin and returns the processed message."""

    message_data = read_message(message)
    request = Request("PROCESS", body=message_data)
    runner = CommandRunner(request, debug, out)
    response = asyncio.run(runner.run(host, port, socket_path, Timeout(timeout), ssl))

    if spam_header := response.headers.spam:
        if spam_header.value:
            runner.exit_code = IS_SPAM
        runner.exit(f"{spam_header.score}/{spam_header.threshold}")
    else:
        typer.echo("Could not find 'Spam' header", err=True)
        raise typer.Exit(UNEXPECTED_ERROR)


@app.command()
def learn(
    message: Optional[typer.FileBinaryRead] = typer.Argument(
        sys.stdin.buffer, help="Message to check, [default: stdin]"
    ),
    host: str = typer.Option(
        "localhost", help="Hostname to use when connecting using TCP"
    ),
    port: int = typer.Option(783, help="Port to use when connecting using TCP"),
    socket_path: str = typer.Option(
        None, help="Path to use when connecting using Unix sockets"
    ),
    ssl: bool = typer.Option(
        None,
        help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
        envvar="AIOSPAMC_CERT_FILE",
    ),
    timeout: float = typer.Option(10, help="Timeout in seconds"),
    message_class: MessageClassOption = typer.Option(
        MessageClassOption.spam, help="Message class to classify the message"
    ),
    out: Output = typer.Option(Output.Text.value, help="Output format for stdout"),
    debug: bool = typer.Option(False, help="Debug information"),
):
    message_data = read_message(message)
    request = Request(
        "TELL",
        headers={
            "Message-class": MessageClassValue(message_class),
            "Set": SetOrRemoveValue(ActionOption(local=True, remote=False)),
        },
        body=message_data,
    )
    runner = CommandRunner(request, debug, out)
    response = asyncio.run(runner.run(host, port, socket_path, Timeout(timeout), ssl))
    if response.headers.did_set:
        runner.exit("Message successfully learned")
    else:
        runner.exit("Message was already learned")


@app.command()
def forget(
    message: Optional[typer.FileBinaryRead] = typer.Argument(
        sys.stdin.buffer, help="Message to check, [default: stdin]"
    ),
    host: str = typer.Option(
        "localhost", help="Hostname to use when connecting using TCP"
    ),
    port: int = typer.Option(783, help="Port to use when connecting using TCP"),
    socket_path: str = typer.Option(
        None, help="Path to use when connecting using Unix sockets"
    ),
    ssl: bool = typer.Option(
        None,
        help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
        envvar="AIOSPAMC_CERT_FILE",
    ),
    timeout: float = typer.Option(10, help="Timeout in seconds"),
    out: Output = typer.Option(Output.Text.value, help="Output format for stdout"),
    debug: bool = typer.Option(False, help="Debug information"),
):
    message_data = read_message(message)
    request = Request(
        "TELL",
        headers={
            "Remove": SetOrRemoveValue(ActionOption(local=True, remote=False)),
        },
        body=message_data,
    )
    runner = CommandRunner(request, debug, out)
    response = asyncio.run(runner.run(host, port, socket_path, Timeout(timeout), ssl))

    if response.headers.did_remove:
        runner.exit("Message successfully forgotten")
    else:
        runner.exit("Message was already forgotten")


@app.command()
def report(
    message: Optional[typer.FileBinaryRead] = typer.Argument(
        sys.stdin.buffer, help="Message to check, [default: stdin]"
    ),
    host: str = typer.Option(
        "localhost", help="Hostname to use when connecting using TCP"
    ),
    port: int = typer.Option(783, help="Port to use when connecting using TCP"),
    socket_path: str = typer.Option(
        None, help="Path to use when connecting using Unix sockets"
    ),
    ssl: bool = typer.Option(
        None,
        help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
        envvar="AIOSPAMC_CERT_FILE",
    ),
    timeout: float = typer.Option(10, help="Timeout in seconds"),
    message_class: MessageClassOption = typer.Option(
        MessageClassOption.spam, help="Message class to classify the message"
    ),
    out: Output = typer.Option(Output.Text.value, help="Output format for stdout"),
    debug: bool = typer.Option(False, help="Debug information"),
):
    message_data = read_message(message)
    request = Request(
        "TELL",
        headers={
            "Message-class": MessageClassValue(message_class),
            "Set": SetOrRemoveValue(ActionOption(local=True, remote=True)),
        },
        body=message_data,
    )
    runner = CommandRunner(request, debug, out)
    response = asyncio.run(runner.run(host, port, socket_path, Timeout(timeout), ssl))

    if response.headers.did_set and response.headers.did_set.action.remote:
        runner.exit("Message successfully reported")
    else:
        runner.exit("Unable to report message")


@app.command()
def revoke(
    message: Optional[typer.FileBinaryRead] = typer.Argument(
        sys.stdin.buffer, help="Message to check, [default: stdin]"
    ),
    host: str = typer.Option(
        "localhost", help="Hostname to use when connecting using TCP"
    ),
    port: int = typer.Option(783, help="Port to use when connecting using TCP"),
    socket_path: str = typer.Option(
        None, help="Path to use when connecting using Unix sockets"
    ),
    ssl: bool = typer.Option(
        None,
        help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
        envvar="AIOSPAMC_CERT_FILE",
    ),
    timeout: float = typer.Option(10, help="Timeout in seconds"),
    message_class: MessageClassOption = typer.Option(
        MessageClassOption.spam, help="Message class to classify the message"
    ),
    out: Output = typer.Option(Output.Text.value, help="Output format for stdout"),
    debug: bool = typer.Option(False, help="Debug information"),
):
    message_data = read_message(message)
    request = Request(
        "TELL",
        headers={
            "Message-class": MessageClassValue(message_class),
            "Remove": SetOrRemoveValue(ActionOption(local=True, remote=True)),
        },
        body=message_data,
    )
    runner = CommandRunner(request, debug, out)
    response = asyncio.run(runner.run(host, port, socket_path, Timeout(timeout), ssl))
    if response.headers.did_remove and response.headers.did_remove.action.remote:
        runner.exit("Message successfully revoked")
    else:
        runner.exit("Unable to report revoked")


def version_callback(version: bool):
    if version:
        typer.echo(__version__)
        raise typer.Exit()


def debug_callback(debug: bool):
    if debug:
        logger.enable(__package__)


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", is_flag=True, callback=version_callback
    ),
    debug: bool = typer.Option(False, "--debug", is_flag=True, callback=debug_callback),
):
    pass
