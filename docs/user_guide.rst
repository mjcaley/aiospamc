##########
User Guide
##########

************
Requirements
************

* Python 3.5 or later is required to use the new async/await syntax provided by the asyncio library.
* SpamAssassin running as a service.

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

Instantiating the :class:`aiospamc.client.Client` class will be the primary way
to interact with aiospamc.

Parameters are available to specify how to connect to the SpamAssassin SPAMD
service including host, port, and whether SSL is enabled.  They default to
``localhost``, ``783``, and SSL being disabled.  Additional optional parameters
are the username that requests will be sent as (no user by default) and whether
to compress the request body (disabled by default).

A coroutine method is available for each type of request that can be sent to
SpamAssassin.

An example using the :meth:`aiospamc.client.Client.check` method:

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
    
    loop = asyncio.get_event_loop()
    client = aiospamc.Client()
    response = loop.run_until_complete(client.check(example_message))
    print(response)

Other requests can be seen in the :class:`aiospamc.client.Client` class.

************************
Making your own requests
************************

If a request that isn't built into aiospamc is needed a new request can be
created and sent.

A new request can be made by instantiating the
:class:`aiospamc.requests.Request` class.  The
:attr:`aiospamc.requests.Request.verb` defines the method/verb of the request.

Standard headers or the :class:`aiospamc.headers.XHeader` extension header are
available in the :mod:`aiospamc.headers` module. The
:class:`aiospamc.requests.Request` class provides a headers attribute that has
a dictionary-like interface.

Once a request is composed, it can be sent through the
:meth:`aiospamc.client.Client.send` method as-is.  The method will automatically
add the :class:`aiospamc.headers.User` and :class:`aiospamc.headers.Compress`
headers if required.

For example:

.. code-block::

    import asyncio

    import aiospamc
    from aiospamc import Client
    from aiospamc.exceptions import ResponseException
    from aiospamc.requests import Request
    
    example_message = ('From: John Doe <jdoe@machine.example>'
                       'To: Mary Smith <mary@example.net>'
                       'Subject: Saying Hello'
                       'Date: Fri, 21 Nov 1997 09:55:06 -0600'
                       'Message-ID: <1234@local.machine.example>'
                       ''
                       'This is a message just to say hello.'
                       'So, "Hello".').encode('ascii')

    loop = asyncio.get_event_loop()
    client = aiospamc.Client(host='localhost')

    async def is_spam(message):
        request = Request(verb='CHECK', body=message.encode())
        try:
            response = await client.send(request)
            return response.get_header('Spam').value
        except aiospamc.ResponseException:
            raise

    spam_result = loop.run_until_complete(is_spam(example_message))
    print('Example message is spam:', spam_result)

********************
Interpreting results
********************

Responses are encapsulated in the :class:`aiospamc.responses.Response` class.
It includes the status code, headers and body.
