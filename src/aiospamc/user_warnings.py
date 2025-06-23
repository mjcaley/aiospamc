"""Functions to raise warnings based on user inputs."""

from warnings import warn

from .connections import ConnectionManager, TcpConnectionManager
from .requests import Request


def raise_warnings(request: Request, connection: ConnectionManager):
    """Calls all warning functions.

    :param request: Instance of a request.
    :param connection: Connection manager instance.
    """

    warn_spamd_bug_7183(request, connection)


def warn_spamd_bug_7183(request: Request, connection: ConnectionManager):
    """Warn on spamd bug if using compression with an SSL connection.

    :param request: Instance of a request.
    :param connection: Connection manager instance.

    Bug: https://bz.apache.org/SpamAssassin/show_bug.cgi?id=7183
    """

    if (
        "Compress" in request.headers
        and isinstance(connection, TcpConnectionManager)
        and connection.ssl_context is not None
    ):
        message = (
            "spamd bug 1783: SpamAssassin hangs when using SSL and compression are used in combination. "
            "Disable compression as a workaround. "
            "More information available at: https://bz.apache.org/SpamAssassin/show_bug.cgi?id=7183"
        )
        warn(message)
