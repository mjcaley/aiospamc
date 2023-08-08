"""CLI commands."""

import asyncio
import json
import ssl
import sys
from enum import Enum
from getpass import getuser
from io import BufferedReader
from typing import Any, Optional, Union

import typer
from loguru import logger
from typing_extensions import Annotated

from aiospamc.exceptions import AIOSpamcConnectionFailed, ParseError
from aiospamc.header_values import (
    ActionOption,
    Headers,
    MessageClassOption,
    MessageClassValue,
    SetOrRemoveValue,
)

from . import __version__
from .client import Client, Request
from .connections import Timeout
from .responses import Response, ResponseException

app = typer.Typer(no_args_is_help=True)


class Output(str, Enum):
    """Output formats."""

    Json = "json"
    Text = "text"

    def __str__(self) -> str:
        return self.value


# Exit codes
SUCCESS = NOT_SPAM = PING_SUCCESS = 0
IS_SPAM = REPORT_FAILED = REVOKE_FAILED = 1
PARSE_ERROR = 3
TIMEOUT_ERROR = 4
CONNECTION_ERROR = 5
UNEXPECTED_ERROR = 6
FILE_NOT_FOUND_ERROR = 7


class CommandRunner:
    """Object to execute requests and handle exceptions."""

    def __init__(
        self,
        request: Request,
        output: Output = Output.Text,
    ):
        """CommandRunner constructor.

        :param request: Request to send.
        :param response: Response if returned from server.
        :param output: Output format when printing to console.
        """

        self.request = request
        self.response: Optional[Response] = None
        self.output = output
        self.exception: Optional[Exception] = None
        self.exit_code = SUCCESS

        self._client = Client()
        self._logger = logger.bind(request=request)

    async def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        socket_path: Optional[str] = None,
        timeout: Optional[Timeout] = None,
        verify: Any = None,
    ) -> Response:
        """Send the request, get the response and handle common exceptions.

        :param host: Hostname or IP address of the SPAMD service, defaults to localhost.
        :param port: Port number for the SPAMD service, defaults to 783.
        :param socket_path: Path to Unix socket.
        :param timeout: Timeout settings.
        :param verify:
            Enable SSL. `True` will use the root certificates from the :py:mod:`certifi` package.
            `False` will use SSL, but not verify the root certificates. Passing a string to a filename
            will use the path to verify the root certificates.
        """

        ssl_context = self._client.ssl_context_factory(verify)
        connection = self._client.connection_factory(
            host, port, socket_path, timeout, ssl_context
        )
        parser = self._client.parser_factory()
        self._logger = self._logger.bind(host=host, port=port, socket_path=socket_path)
        self._logger.info("Sending request")

        ssl_context = self._client.ssl_context_factory(verify)
        connection = self._client.connection_factory(
            host, port, socket_path, timeout, ssl_context
        )
        parser = self._client.parser_factory()
        try:
            response = await self._client.request(self.request, connection, parser)
        except ResponseException as e:
            self._logger = self._logger.bind(response=e.response)
            self._logger.exception(e)
            self.response = e.response
            self.exit_code = int(self.response.status_code)
            self.exception = e
            self.exit(f"Response error from server: {self.response.message}", True)
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
        self._logger.success("Successfully recieved request")
        self.response = response

        return response

    def to_json(self) -> str:
        """Converts the object to a JSON string.

        :returns: JSON string.
        """

        obj = {
            "request": self.request.to_json(),
            "response": self.response.to_json() if self.response is not None else None,
            "exit_code": self.exit_code,
        }

        return json.dumps(obj, indent=4)

    def exit(self, message: str, err=False):
        """Exits the program, echoing the message if outputting text.
        Otherwise prints the JSON object.

        :param message: Message text to print.
        :param err: Flag if message is an error.
        """

        if self.output == Output.Text:
            typer.echo(message, err=err)
        else:
            typer.echo(self.to_json())
        raise typer.Exit(self.exit_code)


@app.command()
def ping(
    host: Annotated[
        str,
        typer.Option(
            "-h",
            "--host",
            metavar="HOSTNAME",
            help="Hostname to use when connecting using TCP",
        ),
    ] = "localhost",
    port: Annotated[
        int,
        typer.Option(
            "-p", "--port", metavar="PORT", help="Port to use when connecting using TCP"
        ),
    ] = 783,
    socket_path: Annotated[
        str,
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = "",
    ssl: Annotated[
        Optional[bool],
        typer.Option(
            help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
):
    """Pings the SpamAssassin daemon.

    A successful pong exits with code 0.
    """

    request = Request("PING")
    runner = CommandRunner(request, out)
    response = asyncio.run(runner.run(host, port, socket_path, Timeout(timeout), ssl))
    runner.exit(response.message)


def read_message(file: Optional[BufferedReader]) -> bytes:
    """Utility function to read data from stdin.

    :param file: File-like object.
    """

    if not file:
        return sys.stdin.buffer.read()
    return file.read()


@app.command()
def check(
    message: Annotated[
        Optional[typer.FileBinaryRead],
        typer.Argument(show_default=False, help="Filename of message"),
    ] = None,
    host: Annotated[
        str,
        typer.Option(
            "-h",
            "--host",
            metavar="HOSTNAME",
            help="Hostname to use when connecting using TCP",
        ),
    ] = "localhost",
    port: Annotated[
        int,
        typer.Option(
            "-p",
            "--port",
            metavar="PORT",
            help="Port to use when connecting using TCP",
        ),
    ] = 783,
    socket_path: Annotated[
        str,
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = "",
    ssl: Annotated[
        Optional[bool],
        typer.Option(
            help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    user: Annotated[str, typer.Option(help="User to send the request as.")] = getuser(),
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
):
    """Submits a message to SpamAssassin and returns the processed message."""

    message_data = read_message(message)
    headers = Headers()
    headers.user = user
    request = Request("PROCESS", headers=headers, body=message_data)
    runner = CommandRunner(request, out)
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
    message: Annotated[
        Optional[typer.FileBinaryRead],
        typer.Argument(help="Filename of message"),
    ] = None,
    message_class: Annotated[
        MessageClassOption, typer.Option(help="Message class to classify the message")
    ] = MessageClassOption.spam,
    host: Annotated[
        str,
        typer.Option(
            "-h",
            "--host",
            metavar="HOSTNAME",
            help="Hostname to use when connecting using TCP",
        ),
    ] = "localhost",
    port: Annotated[
        int,
        typer.Option(
            "-p",
            "--port",
            metavar="PORT",
            help="Port to use when connecting using TCP",
        ),
    ] = 783,
    socket_path: Annotated[
        str,
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = "",
    ssl: Annotated[
        Optional[bool],
        typer.Option(
            help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    user: Annotated[str, typer.Option(help="User to send the request as.")] = getuser(),
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
):
    """Ask server to learn the message as spam or ham."""

    message_data = read_message(message)
    headers = Headers()
    headers.user = user
    headers.message_class = message_class
    headers.set_ = ActionOption(local=True, remote=False)
    request = Request(
        "TELL",
        headers=headers,
        body=message_data,
    )
    runner = CommandRunner(request, out)
    response = asyncio.run(runner.run(host, port, socket_path, Timeout(timeout), ssl))

    if response.headers.did_set:
        runner.exit("Message successfully learned")
    else:
        runner.exit("Message was already learned")


@app.command()
def forget(
    message: Annotated[
        Optional[typer.FileBinaryRead],
        typer.Argument(help="Filename of message"),
    ] = None,
    host: Annotated[
        str,
        typer.Option(
            "-h",
            "--host",
            metavar="HOSTNAME",
            help="Hostname to use when connecting using TCP",
        ),
    ] = "localhost",
    port: Annotated[
        int,
        typer.Option(
            "-p",
            "--port",
            metavar="PORT",
            help="Port to use when connecting using TCP",
        ),
    ] = 783,
    socket_path: Annotated[
        str,
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = "",
    ssl: Annotated[
        Optional[bool],
        typer.Option(
            help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    user: Annotated[str, typer.Option(help="User to send the request as.")] = getuser(),
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
):
    """Forgets the classification of a message."""

    message_data = read_message(message)
    headers = Headers()
    headers.user = user
    headers.remove = ActionOption(local=True, remote=False)
    request = Request(
        "TELL",
        headers=headers,
        body=message_data,
    )
    runner = CommandRunner(request, out)
    response = asyncio.run(runner.run(host, port, socket_path, Timeout(timeout), ssl))

    if response.headers.did_remove:
        runner.exit("Message successfully forgotten")
    else:
        runner.exit("Message was already forgotten")


@app.command()
def report(
    message: Annotated[
        Optional[typer.FileBinaryRead],
        typer.Argument(help="Filename of message"),
    ] = None,
    host: Annotated[
        str,
        typer.Option(
            "-h",
            "--host",
            metavar="HOSTNAME",
            help="Hostname to use when connecting using TCP",
        ),
    ] = "localhost",
    port: Annotated[
        int,
        typer.Option(
            "-p",
            "--port",
            metavar="PORT",
            help="Port to use when connecting using TCP",
        ),
    ] = 783,
    socket_path: Annotated[
        str,
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = "",
    ssl: Annotated[
        Optional[bool],
        typer.Option(
            help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    user: Annotated[str, typer.Option(help="User to send the request as.")] = getuser(),
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
):
    """Report a message to collaborative filtering databases as spam."""

    message_data = read_message(message)
    headers = Headers()
    headers.user = user
    headers.message_class = MessageClassOption.spam
    request = Request(
        "TELL",
        headers=headers,
        body=message_data,
    )
    runner = CommandRunner(request, out)
    response = asyncio.run(runner.run(host, port, socket_path, Timeout(timeout), ssl))

    if response.headers.did_set and response.headers.did_set.remote is True:
        runner.exit("Message successfully reported")
    else:
        runner.exit_code = REPORT_FAILED
        runner.exit("Unable to report message")


@app.command()
def revoke(
    message: Annotated[
        Optional[typer.FileBinaryRead],
        typer.Argument(help="Filename of message"),
    ] = None,
    host: Annotated[
        str,
        typer.Option(
            "-h",
            "--host",
            metavar="HOSTNAME",
            help="Hostname to use when connecting using TCP",
        ),
    ] = "localhost",
    port: Annotated[
        int,
        typer.Option(
            "-p",
            "--port",
            metavar="PORT",
            help="Port to use when connecting using TCP",
        ),
    ] = 783,
    socket_path: Annotated[
        str,
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = "",
    ssl: Annotated[
        Optional[bool],
        typer.Option(
            help="Use SSL to communicate with the daemon. Setting the environment variable to a certificate file will use that to verify the server certificates.",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    user: Annotated[str, typer.Option(help="User to send the request as.")] = getuser(),
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
):
    """Revoke a message to collaborative filtering databases."""

    message_data = read_message(message)
    headers = Headers()
    headers.user = user
    headers.message_class = MessageClassOption.ham
    request = Request(
        "TELL",
        headers={
            "Message-class": MessageClassValue(MessageClassOption.ham),
            "Remove": SetOrRemoveValue(ActionOption(local=True, remote=True)),
        },
        body=message_data,
    )
    runner = CommandRunner(request, out)
    response = asyncio.run(runner.run(host, port, socket_path, Timeout(timeout), ssl))
    if response.headers.did_remove and response.headers.did_remove.remote:
        runner.exit("Message successfully revoked")
    else:
        runner.exit_code = REVOKE_FAILED
        runner.exit("Unable to revoke message")


def version_callback(version: bool):
    """Callback to print the version.

    :param version: Switch on whether to print and exit.
    """

    if version:
        typer.echo(__version__)
        raise typer.Exit()


def debug_callback(debug: bool):
    """Callback to enable debug logging.

    :param debug: Switch on whether to enable debug logging.
    """

    if debug:
        logger.enable(__package__)


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            is_flag=True,
            callback=version_callback,
            help="Output format for stdout",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            is_flag=True,
            callback=debug_callback,
            help="Enable debug logging",
        ),
    ] = False,
):
    pass
