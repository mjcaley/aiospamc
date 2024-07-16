########
aiospamc
########

|pypi| |docs| |license| |unit| |integration| |python|

.. |pypi| image:: https://img.shields.io/pypi/v/aiospamc
    :target: https://pypi.org/project/aiospamc/

.. |unit| image:: https://github.com/mjcaley/aiospamc/actions/workflows/unit-tests.yml/badge.svg
    :target: https://github.com/mjcaley/aiospamc/actions/workflows/unit-tests.yml

.. |integration| image:: https://github.com/mjcaley/aiospamc/actions/workflows/integration-tests.yml/badge.svg
    :target: https://github.com/mjcaley/aiospamc/actions/workflows/integration-tests.yml

.. |docs| image:: https://readthedocs.org/projects/aiospamc/badge/?version=latest
    :target: https://aiospamc.readthedocs.io/en/latest/

.. |license| image:: https://img.shields.io/github/license/mjcaley/aiospamc
    :target: ./LICENSE

.. |python| image:: https://img.shields.io/pypi/pyversions/aiospamc
    :target: https://python.org

**aiospamc** is a client for SpamAssassin that you can use as a library or command line tool.

The implementation is based on asyncio; so you can use it in your applications for asynchronous calls.

The command line interface provides user-friendly access to SpamAssassin server commands and provides both JSON
and user-consumable outputs.

*************
Documentation
*************

Detailed documentation can be found at: https://aiospamc.readthedocs.io/

************
Requirements
************

* Python 3.9 or higher
* `certifi` for updated certificate authorities
* `loguru` for structured logging
* `typer` for the command line interface

********
Examples
********

Command-Line Tool
=================

`aiospamc` is your interface to SpamAssassin through CLI. To submit a message
for a score, use:

.. code-block:: console

    # Take the output of gtube.msg and have SpamAssasin return a score
    $ cat ./gtube.msg | aiospamc check
    1000.0/5.0

    # Ping the server
    $ aiospamc ping
    PONG

Library
=======

.. code-block:: python

    import asyncio
    import aiospamc


    GTUBE = """Subject: Test spam mail (GTUBE)
    Message-ID: <GTUBE1.1010101@example.net>
    Date: Wed, 23 Jul 2003 23:30:00 +0200
    From: Sender <sender@example.net>
    To: Recipient <recipient@example.net>
    Precedence: junk
    MIME-Version: 1.0
    Content-Type: text/plain; charset=us-ascii
    Content-Transfer-Encoding: 7bit

    This is the GTUBE, the
        Generic
        Test for
        Unsolicited
        Bulk
        Email

    If your spam filter supports it, the GTUBE provides a test by which you
    can verify that the filter is installed correctly and is detecting incoming
    spam. You can send yourself a test mail containing the following string of
    characters (in upper case and with no white spaces and line breaks):

    XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X

    You should send this test mail from an account outside of your network.
    """.encode("ascii")


    # Ping the SpamAssassin server
    async def is_alive():
        pong = await aiospamc.ping()
        return True if pong.status_code == 0 else False

    asyncio.run(is_alive())
    # True


    # Get the spam score of a message
    async def get_score(message):
        response = await aiospamc.check(message)
        return response.headers.spam.score, response.headers.spam.threshold

    asyncio.run(get_score(GTUBE))
    # (1000.0, 5.0)


    # List the modified headers
    async def list_headers(message):
        response = await aiospamc.headers(message)
        for line in response.body.splitlines():
            print(line.decode())

    asyncio.run(list_headers(GTUBE))
    # Received: from localhost by DESKTOP.
    #         with SpamAssassin (version 4.0.0);
    #         Wed, 30 Aug 2023 20:11:34 -0400
    # From: Sender <sender@example.net>
    # To: Recipient <recipient@example.net>
    # Subject: Test spam mail (GTUBE)
    # Date: Wed, 23 Jul 2003 23:30:00 +0200
    # Message-Id: <GTUBE1.1010101@example.net>
    # X-Spam-Checker-Version: SpamAssassin 4.0.0 (2022-12-14) on DESKTOP.
    # X-Spam-Flag: YES
    # X-Spam-Level: **************************************************
    # X-Spam-Status: Yes, score=1000.0 required=5.0 tests=GTUBE,NO_RECEIVED,
    #         NO_RELAYS,T_SCC_BODY_TEXT_LINE autolearn=no autolearn_force=no
    #         version=4.0.0
    # MIME-Version: 1.0
    # Content-Type: multipart/mixed; boundary="----------=_64EFDAB6.3640FAEF"
