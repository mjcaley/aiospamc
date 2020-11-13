##########
User Guide
##########

************
Requirements
************

* Python 3.6 or later
* SpamAssassin running as a service

*******
Install
*******

With PIP
========

.. code-block:: bash

    pip install aiospamc

With GIT
========

.. code-block:: bash

    git clone https://github.com/mjcaley/aiospamc.git
    poetry install

.. note::
    aiospamc's build system uses Poetry which you can get from here: https://poetry.eustace.io/

*******************
How to use aiospamc
*******************

:mod:`aiospamc` provides top-level functions for basic functionality a lot like
the `requests` library.

For example, to ask SpamAssassin to check and score a message you can use the
:func:`aiospamc.check` function.  Just give it a bytes-encoded copy of the
message, specify the host and await on the request.  In this case, the response
will contain a header called `Spam` with a boolean if the message is considered
spam as well as the score.

.. code-block::

    import asyncio
    import aiospamc

    example_message = ('From: John Doe <jdoe@machine.example>'
                   'To: Mary Smith <mary@example.net>'
                   'Subject: Saying Hello'
                   'Date: Fri, 21 Nov 1997 09:55:06 -0600'
                   'Message-ID: <1234@local.machine.example>'
                   ''
                   'This is a message just to say hello.'
                   'So, "Hello".').encode('ascii')

    async def check_for_spam(message):
        response = await aiospamc.check(message, host='localhost')
        return response

    loop = asyncio.get_event_loop()

    response = loop.run_until_complete(check_for_spam(example_message))
    print(
        f'Is the message spam? {response.headers['Spam'].value}\n',
        f'The score and threshold is {response.headers['Spam'].score} ',
        f'/ {response.headers['Spam'].threshold}'),
        sep=''
    )

Connect using SSL
=================

Each frontend function has a `verify` parameter which allows configuring an SSL
connection.

If `True` is supplied, then root certificates from the `certifi` project
will be used to verify the connection.

If a path is supplied as a string or :class:`pathlib.Path` object then the path
is used to load certificates to verify the connection.

If `False` then an SSL connection is established, but the server certificate
is not verified.

Setting timeouts
================

`aiospamc` is configured by default to use a timeout of 600 seconds (or 10 minutes)
from the point when a connection is attempted until a response comes in.

If you would like more fine-grained control of timeouts then an
`aiospamc.connections.Timeout` object can be passed in.

You can configure any of the three optional parameters:
* total - maximum time in seconds to wait for a connection and response
* connection - time in seconds to wait for a connection to be established
* response - time in seconds to wait for a response after sending the request

Example
.. code-block::

    my_timeout = aiospamc.Timeout(total=60, connection=10, response=10)

    await def check():
        response = await aiospamc.check(example_message, timeout=my_timeout)

        return response

Logging
=======

`aiospamc` provides two loggers for monitoring.

`aiospamc` is the name of the logger for logs from the client.

`aiospamc.connections` is the name of the logger for logs that monitor TCP and
Unix connections.  This can be used to monitor for issues with connecting, sending,
and receiving data.

Extra data that can be logged with messages include object IDs so you can trace
log messages through the library.  These are named:

* client_id
* connection_id
* request_id
* response_id

Refer to Python's logging documentation on how to consume these loggers.

Interpreting results
====================

Responses are encapsulated in the :class:`aiospamc.responses.Response` class.
It includes the status code, headers and body.
