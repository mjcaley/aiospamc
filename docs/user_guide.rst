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
==========

::

    pip install aiospamc

With GIT
========

::

    git clone https://github.com/mjcaley/aiospamc.git
    python3 aiospamc/setup.py install

*******************
How to use aiospamc
*******************

Instantiating the :class:`aiospamc.client.Client` class will be the primary way to interact with aiospamc.

Parameters are available to specify how to connect to the SpamAssassin SPAMD service including host, port, and whether SSL is enabled.  They default to ``localhost``, ``783``, and SSL being disabled.  Additional optional parameters are the username that requests will be sent as (no user by default) and whether to compress the request body (disabled by default).

A coroutine method is available for each type of request that can be sent to SpamAssassin.

An example using the :meth:`aiospamc.client.Client.check` method:

.. code:: python

    import asyncio
    import aiospamc
    
    example_message = ('From: John Doe <jdoe@machine.example>'
                       'To: Mary Smith <mary@example.net>'
                       'Subject: Saying Hello'
                       'Date: Fri, 21 Nov 1997 09:55:06 -0600'
                       'Message-ID: <1234@local.machine.example>'
                       ''
                       'This is a message just to say hello.'
                       'So, "Hello".')
    
    loop = asyncio.get_event_loop()
    client = aiospamc.Client()
    response = loop.run_until_complete(client.check(example_message))
    print(response)

Other requests can be seen in the :class:`aiospamc.client.Client` class.

************************
Making your own requests
************************

If a request that isn't built into aiospamc is needed a new request can be created and sent.

A new request can be made by instantiating the :class:`aiospamc.requests.Request` class.  The :attr:`aiospamc.requests.Request.verb` defines the method/verb of the request.

Standard headers or the :class:`aiospamc.headers.XHeader` extension header is available in the :mod:`aiospamc.headers` module. Headers are managed on the request object with the methods:

* :meth:`aiospamc.content_man.BodyHeaderManager.add_header`
* :meth:`aiospamc.content_man.BodyHeaderManager.get_header`
* :meth:`aiospamc.content_man.BodyHeaderManager.delete_header`

Once a request is composed, it can be sent through the :meth:`aiospamc.client.Client.send` method as-is.  The method will automatically add the :class:`aiospamc.headers.User` and :class:`aiospamc.headers.Compress` headers if required.

For example:

.. code:: python

    import asyncio
    import aiospamc
    from aiospamc.requests import Request
    from aiospamc.headers import XHeader
    
    example_message = ('From: John Doe <jdoe@machine.example>'
                       'To: Mary Smith <mary@example.net>'
                       'Subject: Saying Hello'
                       'Date: Fri, 21 Nov 1997 09:55:06 -0600'
                       'Message-ID: <1234@local.machine.example>'
                       ''
                       'This is a message just to say hello.'
                       'So, "Hello".')
    
    loop = asyncio.get_event_loop()
    client = aiospamc.Client()
    
    request = Request('FAKE')
    fake_header1 = XHeader('fake_header', 'Fake values')
    request.add_header(fake_header1)
    request.body = example_message
    
    response = loop.run_until_complete(client.send(request))
    print(response)

********************
Interpreting results
********************

Responses are encapsulated in the :class:`aiospamc.responses.Response` class.  Any data will need to be additionally parsed by the user.
