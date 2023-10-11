"""CLI commands."""

import asyncio
import json
import ssl
import sys
from enum import Enum
from getpass import getpass, getuser
from io import BufferedReader
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from typing_extensions import Annotated

from aiospamc.exceptions import (
    AIOSpamcConnectionFailed,
    BadResponse,
    ClientTimeoutException,
)
from aiospamc.header_values import (
    ActionOption,
    Headers,
    MessageClassOption,
    MessageClassValue,
    SetOrRemoveValue,
)

from . import __version__
from .client import Client, Request
from .connections import ConnectionManagerBuilder, SSLContextBuilder, Timeout
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
BAD_RESPONSE = 3
TIMEOUT_ERROR = 4
CONNECTION_ERROR = 5
UNEXPECTED_ERROR = 6
FILE_NOT_FOUND_ERROR = 7


class CliClientBuilder:
    """Client builder for CLI arguments."""

    def __init__(self):
        """Constructor for the CliClientBuilder."""

        self._connection_builder = ConnectionManagerBuilder()
        self._ssl = False
        self._ssl_builder = SSLContextBuilder()

    def build(self) -> Client:
        """Builds the :class:`aiospamc.client.Client`.

        :return: An instance of :class:`aiospamc.client.Client`.
        """

        if self._ssl:
            ssl_context = self._ssl_builder.build()
            self._connection_builder.add_ssl_context(ssl_context)
        connection_manager = self._connection_builder.build()

        return Client(connection_manager)

    def with_connection(
        self,
        host: str = "localhost",
        port: int = 783,
        socket_path: Optional[Path] = None,
    ) -> "CliClientBuilder":
        """Sets the type of connection manager to use.

        Defaults to TCP, but if a Unix socket is provided it will be used.

        :param host: TCP hostname to use.
        :param port: TCP port to use.
        :param socket_path: Path to the Unix socket.

        :return: This builder instance.
        """

        if socket_path:
            self._connection_builder = self._connection_builder.with_unix_socket(
                socket_path
            )
        else:
            self._connection_builder = self._connection_builder.with_tcp(host, port)

        return self

    def set_timeout(self, timeout: Timeout) -> "CliClientBuilder":
        """Sets the timeout for the connection.

        :param timeout: Timeout object.

        :return: This builder instance.
        """

        self._connection_builder.set_timeout(timeout)

        return self

    def add_verify(self, verify: bool) -> "CliClientBuilder":
        """Adds an SSL context to the connection manager.

        :param verify: How to configure the SSL context. If `True`, add the default
            certificate authorities. If `False`, accept any certificate.

        :return: This builder instance.
        """

        self._ssl = True
        self._ssl_builder.add_default_ca()
        if not verify:
            self._ssl_builder.dont_verify()

        return self

    def add_ca_cert(self, ca_cert: Optional[Path]) -> "CliClientBuilder":
        """Adds trusted certificate authorities.

        :param ca_cert: Path to the cerficiate file or directory.

        :return: This builder instance.
        """

        if ca_cert is None:
            return self

        self._ssl = True
        if ca_cert.is_dir():
            self._ssl_builder.add_ca_dir(ca_cert)
        elif ca_cert.is_file():
            self._ssl_builder.add_ca_file(ca_cert)
        else:
            raise FileNotFoundError(
                f"Unable to find CA certificate file/directory {ca_cert}"
            )

        return self

    def add_client_cert(
        self,
        cert: Optional[Path],
        key: Optional[Path] = None,
        password: Optional[str] = None,
    ) -> "CliClientBuilder":
        """Add a client certificate to authenticate to the server.

        :param cert: Path to the client certificate and optionally the key.
        :param key: Path to the client key.
        :param password: Password of the client key.

        :return: This builder instance.
        """

        if cert is None:
            return self

        if self._ssl is False:
            self._ssl = True
            self.add_verify(True)
        self._ssl_builder.add_client(
            cert, key, lambda: password or getpass("Private key password")
        )

        return self


class CommandRunner:
    """Object to execute requests and handle exceptions."""

    def __init__(
        self,
        client: Client,
        request: Request,
        output: Output = Output.Text,
    ):
        """CommandRunner constructor.

        :param request: Request to send.
        :param response: Response if returned from server.
        :param output: Output format when printing to console.
        """

        self.client = client
        self.request = request
        self.response: Optional[Response] = None
        self.output = output
        self.exception: Optional[Exception] = None
        self.exit_code = SUCCESS

        self._logger = logger.bind(request=request)

    async def run(self) -> Response:
        """Send the request, get the response and handle common exceptions.

        :return: The response.
        """

        self._logger.info("Sending request")

        try:
            response = await self.client.request(self.request)
        except BadResponse as e:
            self._logger.exception(e)
            self.exit_code = BAD_RESPONSE
            self.exception = e
            self.exit("Error parsing response", True)
        except ResponseException as e:
            self._logger = self._logger.bind(response=e.response)
            self._logger.exception(e)
            self.response = e.response
            self.exit_code = int(self.response.status_code)
            self.exception = e
            self.exit(f"Response error from server: {self.response.message}", True)
        except (asyncio.TimeoutError, ClientTimeoutException) as e:
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

        :return: JSON string.
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
        Optional[Path],
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = None,
    ssl: Annotated[
        bool, typer.Option(help="Use SSL to communicate with the daemon.")
    ] = False,
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
    ca_cert: Annotated[
        Optional[Path],
        typer.Option(
            help="Path to the CA certificates if overriding",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    client_cert: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate")
    ] = None,
    client_key: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate's key")
    ] = None,
    key_password: Annotated[
        Optional[str], typer.Option(help="Password for the client certificate key")
    ] = None,
):
    """Pings the SpamAssassin daemon.

    A successful pong exits with code 0.
    """

    client_builder = CliClientBuilder()
    client_builder.with_connection(host, port, socket_path).set_timeout(
        Timeout(timeout)
    )
    if ssl:
        client_builder.add_verify(True).add_ca_cert(ca_cert).add_client_cert(
            client_cert, client_key, key_password
        )
    client = client_builder.build()

    request = Request("PING")
    runner = CommandRunner(client, request, out)
    response = asyncio.run(runner.run())
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
        Optional[Path],
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = None,
    ssl: Annotated[
        bool, typer.Option(help="Use SSL to communicate with the daemon.")
    ] = False,
    user: Annotated[
        str, typer.Option(metavar="USERNAME", help="User to send the request as.")
    ] = getuser(),
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
    ca_cert: Annotated[
        Optional[Path],
        typer.Option(
            help="Path to the CA certificates if overriding",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    client_cert: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate")
    ] = None,
    client_key: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate's key")
    ] = None,
    key_password: Annotated[
        Optional[str], typer.Option(help="Password for the client certificate key")
    ] = None,
):
    """Submits a message to SpamAssassin and returns the processed message."""

    message_data = read_message(message)
    headers = Headers()
    headers.user = user
    request = Request("PROCESS", headers=headers, body=message_data)

    client_builder = CliClientBuilder()
    client_builder.with_connection(host, port, socket_path).set_timeout(
        Timeout(timeout)
    )
    if ssl:
        client_builder.add_verify(True).add_ca_cert(ca_cert).add_client_cert(
            client_cert, client_key, key_password
        )
    client = client_builder.build()

    runner = CommandRunner(client, request, out)
    response = asyncio.run(runner.run())

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
        Optional[Path],
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = None,
    ssl: Annotated[
        bool, typer.Option(help="Use SSL to communicate with the daemon.")
    ] = False,
    user: Annotated[
        str, typer.Option(metavar="USERNAME", help="User to send the request as.")
    ] = getuser(),
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
    ca_cert: Annotated[
        Optional[Path],
        typer.Option(
            help="Path to the CA certificates if overriding",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    client_cert: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate")
    ] = None,
    client_key: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate's key")
    ] = None,
    key_password: Annotated[
        Optional[str], typer.Option(help="Password for the client certificate key")
    ] = None,
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

    client_builder = CliClientBuilder()
    client_builder.with_connection(host, port, socket_path).set_timeout(
        Timeout(timeout)
    )
    if ssl:
        client_builder.add_verify(True).add_ca_cert(ca_cert).add_client_cert(
            client_cert, client_key, key_password
        )
    client = client_builder.build()

    runner = CommandRunner(client, request, out)
    response = asyncio.run(runner.run())

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
        Optional[Path],
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = None,
    ssl: Annotated[
        bool, typer.Option(help="Use SSL to communicate with the daemon.")
    ] = False,
    user: Annotated[
        str, typer.Option(metavar="USERNAME", help="User to send the request as.")
    ] = getuser(),
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
    ca_cert: Annotated[
        Optional[Path],
        typer.Option(
            help="Path to the CA certificates if overriding",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    client_cert: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate")
    ] = None,
    client_key: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate's key")
    ] = None,
    key_password: Annotated[
        Optional[str], typer.Option(help="Password for the client certificate key")
    ] = None,
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

    client_builder = CliClientBuilder()
    client_builder.with_connection(host, port, socket_path).set_timeout(
        Timeout(timeout)
    )
    if ssl:
        client_builder.add_verify(True).add_ca_cert(ca_cert).add_client_cert(
            client_cert, client_key, key_password
        )
    client = client_builder.build()

    runner = CommandRunner(client, request, out)
    response = asyncio.run(runner.run())

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
        Optional[Path],
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = None,
    ssl: Annotated[
        bool, typer.Option(help="Use SSL to communicate with the daemon.")
    ] = False,
    user: Annotated[
        str, typer.Option(metavar="USERNAME", help="User to send the request as.")
    ] = getuser(),
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
    ca_cert: Annotated[
        Optional[Path],
        typer.Option(
            help="Path to the CA certificates if overriding",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    client_cert: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate")
    ] = None,
    client_key: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate's key")
    ] = None,
    key_password: Annotated[
        Optional[str], typer.Option(help="Password for the client certificate key")
    ] = None,
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

    client_builder = CliClientBuilder()
    client_builder.with_connection(host, port, socket_path).set_timeout(
        Timeout(timeout)
    )
    if ssl:
        client_builder.add_verify(True).add_ca_cert(ca_cert).add_client_cert(
            client_cert, client_key, key_password
        )
    client = client_builder.build()

    runner = CommandRunner(client, request, out)
    response = asyncio.run(runner.run())

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
        Optional[Path],
        typer.Option(
            metavar="PATH", help="Path to use when connecting using Unix sockets"
        ),
    ] = None,
    ssl: Annotated[
        bool, typer.Option(help="Use SSL to communicate with the daemon.")
    ] = False,
    user: Annotated[
        str, typer.Option(metavar="USERNAME", help="User to send the request as.")
    ] = getuser(),
    timeout: Annotated[
        float, typer.Option(metavar="SECONDS", help="Timeout in seconds")
    ] = 10,
    out: Annotated[Output, typer.Option(help="Output format for stdout")] = Output.Text,
    ca_cert: Annotated[
        Optional[Path],
        typer.Option(
            help="Path to the CA certificates if overriding",
            envvar="AIOSPAMC_CERT_FILE",
        ),
    ] = None,
    client_cert: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate")
    ] = None,
    client_key: Annotated[
        Optional[Path], typer.Option(help="Filename of the client certificate's key")
    ] = None,
    key_password: Annotated[
        Optional[str], typer.Option(help="Password for the client certificate key")
    ] = None,
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

    client_builder = CliClientBuilder()
    client_builder.with_connection(host, port, socket_path).set_timeout(
        Timeout(timeout)
    )
    if ssl:
        client_builder.add_verify(True).add_ca_cert(ca_cert).add_client_cert(
            client_cert, client_key, key_password
        )
    client = client_builder.build()

    runner = CommandRunner(client, request, out)
    response = asyncio.run(runner.run())

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
            callback=version_callback,
            is_eager=True,
            help="Print version of aiospamc",
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
    """aiospamc sends messages to the SpamAssasin daemon."""

    pass
