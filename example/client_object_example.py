import asyncio
from aiospamc import Client


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


async def tell_spamd_message_is_spam(message):
    client = Client(host='localhost')

    response = await client.tell(message, message_class='spam', set_action='local, remote')
    response.raise_for_status()

    return True

loop = asyncio.get_event_loop()
result = loop.run_until_complete(
    tell_spamd_message_is_spam(GTUBE)
)
print('Message reported as spam:', result)
