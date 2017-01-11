========
aiospamc
========

.. image:: https://travis-ci.org/mjcaley/aiospamc.svg?branch=master
    :target: https://travis-ci.org/mjcaley/aiospamc
.. image:: https://codecov.io/gh/mjcaley/aiospamc/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mjcaley/aiospamc
    
-----------
Description
-----------

Python asyncio-based library that implements the SPAMC/SPAMD client protocol used by SpamAssassin.

-------------
Documentation
-------------

Documentation can be found at: https://pythonhosted.org/aiospamc/

------------
Requirements
------------

* Python 3.5 or higher

-------
Example
-------

.. code:: python

    import asyncio
    import logging

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
    '''

    def example():
        import email
        gtube_msg = email.message_from_string(GTUBE)

        async def print_response(title, func, *opts):
            try:
                resp = await func(*opts)
                print('----------------------------------------------------------')
                print(title, ':', repr(resp))
            except Exception as e:
                logging.exception(' '.join(['Error:', str(e)]))

        loop = asyncio.new_event_loop()
        client = aiospamc.Client(loop=loop)

        loop.run_until_complete(
            asyncio.gather(
                print_response('Ping', client.ping),
                print_response('Check', client.check, str(gtube_msg)),
                print_response('Headers', client.headers, str(gtube_msg)),
                loop=loop)
        )

        loop.close()

    if __name__ == '__main__':
        example()
