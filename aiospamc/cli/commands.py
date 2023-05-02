"""CLI commands."""

import asyncio
import ssl
import sys
from enum import Enum, auto
from typing import Optional

import typer

from aiospamc.exceptions import ParseError
from aiospamc.header_values import (
    ActionOption,
    MessageClassOption,
    MessageClassValue,
    SetOrRemoveValue,
)

from ..client import Client, Request
from ..connections import Timeout
from ..responses import Response, ResponseException

app = typer.Typer()


class ResultKind(Enum):
    Success = auto()
    ParseError = auto()
    ResponseError = auto()
    TimeoutError = auto()


class Output(str, Enum):
    """Output formats."""

    Json = "json"
    Text = "text"


class CLIRunner:
    def __init__(
        self,
        request: Request,
        debug: bool = False,
        output: Output = Output.Text,
        client: Client = None,
    ):
        self.request = request
        self.debug = debug
        self.output = output
        self.client = client or Client()

        self.response: Optional[Response] = None
        self.exception: Optional[Exception] = None

    async def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        socket_path: Optional[str] = None,
        verify=None,
    ):
        try:
            ssl_context = self.client.ssl_context_factory(verify)
            connection = self.client.connection_factory(
                host, port, socket_path, ssl_context
            )
            parser = self.client.parser_factory()
            self.response = await self.client.request_new(
                self.request, connection, parser
            )

            return ResultKind.Success

        except ResponseException as e:
            self.response = e.response
            self.exception = e
            return ResultKind.ResponseError
        except ParseError as e:
            self.exception = e
            return ResultKind.ParseError
        except asyncio.TimeoutError as e:
            self.exception = e
            return ResultKind.TimeoutError
        except (OSError, ConnectionError, ssl.SSLError) as e:
            self.exception = e
            return ConnectionError


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
    runner = CLIRunner(request, debug, out)
    result = asyncio.run(runner.run(host, port, socket_path, ssl))
    if result == ResultKind.Success:
        typer.echo(runner.response.message)
    elif result == ResultKind.ResponseError:
        typer.echo(runner.response.message)
        typer.Exit(runner.response.status_code)
    else:
        typer.Exit(1)


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
    message_data = read_message(message)
    request = Request("PROCESS", body=message_data)
    runner = CLIRunner(request, debug, out)
    result = asyncio.run(runner.run(host, port, socket_path, ssl))
    if result == ResultKind.Success:
        spam_header = runner.response.headers["Spam"]
        typer.echo(f"{spam_header.score}/{spam_header.threshold}")
        if spam_header.value:
            typer.Exit(code=1)
    elif result == ResultKind.ResponseError:
        typer.echo(runner.response.message)
        typer.Exit(runner.response.status_code)
    else:
        typer.echo
        typer.Exit(1)


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
    runner = CLIRunner(request, debug, out)
    result = asyncio.run(runner.run(host, port, socket_path, ssl))
    if result == ResultKind.Success:
        if "DidSet" in runner.response.headers:
            typer.echo("Message successfully learned")
        else:
            typer.echo("Message was already learned")
    elif result == ResultKind.ResponseError:
        typer.echo(runner.response.message)
        typer.Exit(runner.response.status_code)
    else:
        typer.echo("Unknown error occurred", err=True)
        typer.Exit(1)


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
    runner = CLIRunner(request, debug, out)
    result = asyncio.run(runner.run(host, port, socket_path, ssl))
    if result == ResultKind.Success:
        if "DidRemove" in runner.response.headers:
            typer.echo("Message successfully forgotten")
        else:
            typer.echo("Message was already forgotten")
    elif result == ResultKind.ResponseError:
        typer.echo(runner.response.message)
        typer.Exit(runner.response.status_code)
    else:
        typer.echo("Unknown error occurred", err=True)
        typer.Exit(1)


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
    runner = CLIRunner(request, debug, out)
    result = asyncio.run(runner.run(host, port, socket_path, ssl))
    if result == ResultKind.Success:
        if didset := runner.response.headers.get("DidSet") and didset.action.remote:
            typer.echo("Message successfully reported")
        else:
            typer.echo("Unable to report message")
            typer.Exit(1)
    elif result == ResultKind.ResponseError:
        typer.echo(runner.response.message)
        typer.Exit(runner.response.status_code)
    else:
        typer.echo("Unknown error occurred", err=True)
        typer.Exit(1)


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
    runner = CLIRunner(request, debug, out)
    result = asyncio.run(runner.run(host, port, socket_path, ssl))
    if result == ResultKind.Success:
        if (
            didremove := runner.response.headers.get("DidRemove")
            and didremove.action.remote
        ):
            typer.echo("Message successfully revoked")
        else:
            typer.echo("Unable to report revoked")
            typer.Exit(1)
    elif result == ResultKind.ResponseError:
        typer.echo(runner.response.message)
        typer.Exit(runner.response.status_code)
    else:
        typer.echo("Unknown error occurred", err=True)
        typer.Exit(1)
