#######
Library
#######

:mod:`aiospamc` provides top-level functions for all request types.

For example, to ask SpamAssassin to check and score a message you can use the
:func:`aiospamc.check` function.  Just give it a bytes-encoded copy of the
message, specify the host and await on the request.  In this case, the response
will contain a header called `Spam` with a boolean if the message is considered
spam as well as the score.

.. code-block:: python

    import asyncio
    import aiospamc

    example_message = (
        "From: John Doe <jdoe@machine.example>"
        "To: Mary Smith <mary@example.net>"
        "Subject: Saying Hello"
        "Date: Fri, 21 Nov 1997 09:55:06 -0600"
        "Message-ID: <1234@local.machine.example>"
        ""
        "This is a message just to say hello."
        "So, 'Hello'.").encode("ascii")

    response = asyncio.run(aiospamc.check(message, host="localhost"))
    print(
        f"Is the message spam? {response.headers.spam.value}\n",
        f"The score and threshold is {response.headers.spam.score} ",
        f"/ {response.headers.spam.threshold}",
        sep=""
    )

*****************
Connect using SSL
*****************

Each frontend function has a `verify` parameter which allows configuring an SSL
connection.

If `True` is supplied, then root certificates from the `certifi` project
will be used to verify the connection.

If a path is supplied as a string or :class:`pathlib.Path` object then the path
is used to load certificates to verify the connection.

If `False` then an SSL connection is established, but the server certificate
is not verified.

*********************************
Client Certificate Authentication
*********************************

Client certificate authentication can be used with SSL. It's driven through the `cert`
parameter on frontend functions. The parameter value takes three forms:

* A path to a file expecting the certificate and key in the PEM format
* A tuple of certificate and key files
* A tuple of certificate file, key file, and password if the key is encrypted

.. code:: python

    import aiospamc

    # Client certificate and key in one file
    response = await aiospamc.ping("localhost", cert=cert_file)

    # Client certificate and key file
    response = await aiospamc.ping("localhost", cert=(cert_file, key_file))

    # Client certificate and key in one file
    response = await aiospamc.ping("localhost", cert=(cert_file, key_file, password))

****************
Setting timeouts
****************

`aiospamc` is configured by default to use a timeout of 600 seconds (or 10 minutes)
from the point when a connection is attempted until a response comes in.

If you would like more fine-grained control of timeouts then an
`aiospamc.connections.Timeout` object can be passed in.

You can configure any of the three optional parameters:
* total - maximum time in seconds to wait for a connection and response
* connection - time in seconds to wait for a connection to be established
* response - time in seconds to wait for a response after sending the request

.. code:: python

    import aiospamc

    my_timeout = aiospamc.Timeout(total=60, connection=10, response=10)

    await def check():
        response = await aiospamc.check(example_message, timeout=my_timeout)

        return response

*******
Logging
*******

Logging is provided using through the `loguru <https://github.com/Delgan/loguru>`_ package.

The `aiospamc` package disables logging by default. It can be enabled by calling the
function:

.. code-block:: python

    from loguru import logger
    logger.enable("aiospamc")

Modules log under their own logger names (for example, frontend functions will log under
`aiospamc.frontend`). Extra data like request and response objects are attached to log
records which can be used to trace through flow.

********************
Interpreting results
********************

Responses are encapsulated in the :class:`aiospamc.responses.Response` class.
It includes the status code, headers and body.

The :class:`aiospamc.headers.Headers` class provides properties for headers defined in the
protocol.
