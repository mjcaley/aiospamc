========
aiospamc
========

|pypi| |docs| |license| |build| |coverage| |python|

.. |pypi| image:: https://img.shields.io/pypi/v/aiospamc
    :target: https://pypi.org/project/aiospamc/

.. |build| image:: https://img.shields.io/azure-devops/build/mjcaley/aiospamc/2/master
    :target: https://dev.azure.com/mjcaley/aiospamc/_build?definitionId=8&_a=summary&repositoryFilter=2&branchFilter=20

.. |coverage| image:: https://img.shields.io/azure-devops/coverage/mjcaley/aiospamc/2/master
    :target: https://dev.azure.com/mjcaley/aiospamc/_build?definitionId=8&_a=summary&repositoryFilter=2&branchFilter=20

.. |docs| image:: https://img.shields.io/readthedocs/aiospamc
    :target: https://aiospamc.readthedocs.io/en/latest/

.. |license| image:: https://img.shields.io/github/license/mjcaley/aiospamc
    :target: ./LICENSE

.. |python| image:: https://img.shields.io/pypi/pyversions/aiospamc
    :target: https://python.org

-----------
Description
-----------

Python asyncio-based library that implements the SPAMC/SPAMD client protocol used by SpamAssassin.

-------------
Documentation
-------------

Documentation can be found at: https://aiospamc.readthedocs.io/

------------
Requirements
------------

* Python 3.6 or higher

-------
Example
-------

.. code:: python
    
    import asyncio
    import aiospamc


    GTUBE = '''Subject: Test spam mail (GTUBE)
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
    '''.encode('ascii')

    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(asyncio.gather(

        aiospamc.ping(host='localhost'),
        aiospamc.check(GTUBE, host='localhost'),
        aiospamc.headers(GTUBE, host='localhost')

    ))
    print(responses)
