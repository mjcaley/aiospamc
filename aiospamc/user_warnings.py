#!/usr/bin/env python

"""Functions to raise warnings based on user inputs."""

from warnings import warn

from .connections import ConnectionManager, TcpConnectionManager
from .requests import Request


def raise_warnings(request: Request, connection: ConnectionManager):
    warn_spamd_bug_7183(request, connection)
    warn_spamd_bug_7938(request, connection)


def warn_spamd_bug_7183(request: Request, connection: ConnectionManager):
    """Warn on spamd bug if using compression with an SSL connection.

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


def warn_spamd_bug_7938(request: Request, connection: ConnectionManager):
    """Warn on spamd bug if a newline character isn't at the end of the body.

    Bug: https://bz.apache.org/SpamAssassin/show_bug.cgi?id=7938
    """

    if (
        isinstance(connection, TcpConnectionManager)
        and connection.ssl_context is not None
        and request.body
        and request.body[-1] != "\n"
    ):
        message = (
            "spamd bug 7938: SpamAssassin hangs when using SSL and the body doesn't end with a newline."
            "Add a newline to the end of the body as a workaround. "
            "More information available at: https://bz.apache.org/SpamAssassin/show_bug.cgi?id=7938"
        )
        warn(message)
