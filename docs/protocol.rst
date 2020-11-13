.. highlight:: none

###################################################
SPAMC/SPAMD Protocol As Implemented by SpamAssassin
###################################################

**********************
Requests and Responses
**********************

The structure of a request is similar to an HTTP request. [1]_  The method/verb,
protocol name and version are listed followed by headers separated by newline
characters (carriage return and linefeed or ``\r\n``).  Following the headers
is a blank line with a newline (``\r\n``).  If there is a message body it will
be added after all headers.

The current requests are :ref:`check_request`, :ref:`headers_request`,
:ref:`ping_request`, :ref:`process_request`, :ref:`report_request`,
:ref:`report_ifspam_request`, :ref:`skip_request`, :ref:`symbols_request`, and
:ref:`tell_request`::

    METHOD SPAMC/1.5\r\n
    HEADER_NAME1: HEADER_VALUE1\r\n
    HEADER_NAME2: HEADER_VALUE2\r\n
    ...
    \r\n
    REQUEST_BODY


The structure of responses are also similar to HTTP responses.  The protocol
name, version, status code, and message are listed on the first line.  Any
headers are also listed and all are separated by newline characters.  Following
the headers is a newline.  If there is a message body it’s included after all
headers::

    SPAMD/1.5 STATUS_CODE MESSAGE\r\n
    HEADER_NAME1: HEADER_VALUE1\r\n
    HEADER_NAME2: HEADER_VALUE2\r\n
    ...
    \r\n
    RESPONSE_BODY

.. note::
    The header name and value are separated by a `:` character.  For built-in
    headers the name must not have any whitespace surrounding it.  It will be
    parsed exactly as it's represented.

The following are descriptions of the requests that can be sent and examples of
the responses that you can expect to receive.

.. _check_request:

CHECK
=====

Instruct SpamAssassin to process the included message.

Request
-------

Required Headers
^^^^^^^^^^^^^^^^

* :ref:`content-length_header`

Optional Headers
^^^^^^^^^^^^^^^^

* :ref:`compress_header`
* :ref:`user_header`

Required body
^^^^^^^^^^^^^

An email based on the :rfc:`5322` standard.

Response
--------

Will include a Spam header with a “True” or “False” value, followed by the
score and threshold.
Example::

    SPAMD/1.1 0 EX_OK
    Spam: True ; 1000.0 / 5.0

.. _headers_request:

HEADERS
=======

Process the included message and return only the modified headers.

Request
-------

Required Headers
^^^^^^^^^^^^^^^^

* :ref:`content-length_header`

Optional Headers
^^^^^^^^^^^^^^^^

* :ref:`compress_header`
* :ref:`user_header`

Required Body
^^^^^^^^^^^^^

An email based on the :rfc:`5322` standard.

Response
--------

Will return the modified headers of the message in the body.  The
:ref:`spam_header` header is also included.
::

    SPAMD/1.1 0 EX_OK
    Spam: True ; 1000.0 / 5.0
    Content-length: 654
    
    Received: from localhost by debian
        with SpamAssassin (version 3.4.0);
        Tue, 10 Jan 2017 11:09:26 -0500
    From: Sender <sender@example.net>
    To: Recipient <recipient@example.net>
    Subject: Test spam mail (GTUBE)
    Date: Wed, 23 Jul 2003 23:30:00 +0200
    Message-Id: <GTUBE1.1010101@example.net>
    X-Spam-Checker-Version: SpamAssassin 3.4.0 (2014-02-07) on debian
    X-Spam-Flag: YES
    X-Spam-Level: **************************************************
    X-Spam-Status: Yes, score=1000.0 required=5.0 tests=GTUBE,NO_RECEIVED,
        NO_RELAYS autolearn=no autolearn_force=no version=3.4.0
    MIME-Version: 1.0Content-Type: multipart/mixed; boundary="----------=_58750736.8D9F70BC"
    

.. _ping_request:

PING
====

Send a request to test if the server is alive.

Request
--------

Required Headers
^^^^^^^^^^^^^^^^

None.

Optional Headers
^^^^^^^^^^^^^^^^

None.

Response
--------

Example::

    SPAMD/1.5 0 PONG

.. _process_request:

PROCESS
=======

Instruct SpamAssassin to process the message and return the modified message.

Request
-------

Required Headers
^^^^^^^^^^^^^^^^

* :ref:`content-length_header`

Optional Headers
^^^^^^^^^^^^^^^^

* :ref:`compress_header`
* :ref:`user_header`

Required Body
^^^^^^^^^^^^^

An email based on the :rfc:`5322` standard.

Response
--------

Will return a modified message in the body.  The :ref:`spam_header` header is
also included.
Example::

    SPAMD/1.1 0 EX_OK
    Spam: True ; 1000.0 / 5.0
    Content-length: 2948
    
    Received: from localhost by debian
        with SpamAssassin (version 3.4.0);
        Tue, 10 Jan 2017 10:57:02 -0500
    From: Sender <sender@example.net>
    To: Recipient <recipient@example.net>
    Subject: Test spam mail (GTUBE)
    Date: Wed, 23 Jul 2003 23:30:00 +0200
    Message-Id: <GTUBE1.1010101@example.net>
    X-Spam-Checker-Version: SpamAssassin 3.4.0 (2014-02-07) on debian
    X-Spam-Flag: YES
    X-Spam-Level: **************************************************
    X-Spam-Status: Yes, score=1000.0 required=5.0 tests=GTUBE,NO_RECEIVED,
        NO_RELAYS autolearn=no autolearn_force=no version=3.4.0
    MIME-Version: 1.0
    Content-Type: multipart/mixed; boundary="----------=_5875044E.D4EFFFD7"
    
    This is a multi-part message in MIME format.
    
    ------------=_5875044E.D4EFFFD7
    Content-Type: text/plain; charset=iso-8859-1
    Content-Disposition: inline
    Content-Transfer-Encoding: 8bit
    
    Spam detection software, running on the system "debian",
    has identified this incoming email as possible spam.  The original
    message has been attached to this so you can view it or label
    similar future email.  If you have any questions, see
    @@CONTACT_ADDRESS@@ for details.
    
    Content preview:  This is the GTUBE, the Generic Test for Unsolicited Bulk Email
    If your spam filter supports it, the GTUBE provides a test by which you can
    verify that the filter is installed correctly and is detecting incoming spam.
    You can send yourself a test mail containing the following string of characters
    (in upper case and with no white spaces and line breaks): [...] 
    
    Content analysis details:   (1000.0 points, 5.0 required)
    
    pts rule name              description
    ---- ---------------------- --------------------------------------------------
    1000 GTUBE                  BODY: Generic Test for Unsolicited Bulk Email
    -0.0 NO_RELAYS              Informational: message was not relayed via SMTP
    -0.0 NO_RECEIVED            Informational: message has no Received headers
    
    
    
    ------------=_5875044E.D4EFFFD7
    Content-Type: message/rfc822; x-spam-type=original
    Content-Description: original message before SpamAssassin
    Content-Disposition: inline
    Content-Transfer-Encoding: 8bit
    
    Subject: Test spam mail (GTUBE)
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
    
    
    ------------=_5875044E.D4EFFFD7--
    
    

.. _report_request:

REPORT
======

Send a request to process a message and return a report.

Request
-------

Required Headers
^^^^^^^^^^^^^^^^

* :ref:`content-length_header`

Optional Headers
^^^^^^^^^^^^^^^^

* :ref:`compress_header`
* :ref:`user_header`

Required body
^^^^^^^^^^^^^

An email based on the :rfc:`5322` standard.

Response
--------

Response returns the :ref:`spam_header` header and the body containing a
report of the message scanned.

Example::

    SPAMD/1.1 0 EX_OK
    Content-length: 1071
    Spam: True ; 1000.0 / 5.0
    
    Spam detection software, running on the system "debian",
    has identified this incoming email as possible spam.  The original
    message has been attached to this so you can view it or label
    similar future email.  If you have any questions, see
    @@CONTACT_ADDRESS@@ for details.

    Content preview:  This is the GTUBE, the Generic Test for Unsolicited Bulk Email
       If your spam filter supports it, the GTUBE provides a test by which you can
       verify that the filter is installed correctly and is detecting incoming spam.
       You can send yourself a test mail containing the following string of characters
       (in upper case and with no white spaces and line breaks): [...] 

    Content analysis details:   (1000.0 points, 5.0 required)

     pts rule name              description
    ---- ---------------------- --------------------------------------------------
    1000 GTUBE                  BODY: Generic Test for Unsolicited Bulk Email
    -0.0 NO_RELAYS              Informational: message was not relayed via SMTP
    -0.0 NO_RECEIVED            Informational: message has no Received headers

.. _report_ifspam_request:

REPORT_IFSPAM
=============

Matches the :ref:`report_request` request, with the exception a report will not
be generated if the message is not spam.

.. _skip_request:

SKIP
====

Sent when a connection is made in error.  The SPAMD service will immediately
close the connection.

Request
-------

Required Headers
^^^^^^^^^^^^^^^^

None.

Optional Headers
^^^^^^^^^^^^^^^^

None.

.. _symbols_request:

SYMBOLS
=======

Instruct SpamAssassin to process the message and return the rules that were
matched.

Request
-------

Required Headers
^^^^^^^^^^^^^^^^

* :ref:`content-length_header`

Optional Headers
^^^^^^^^^^^^^^^^

* :ref:`compress_header`
* :ref:`user_header`

Required body
^^^^^^^^^^^^^

An email based on the :rfc:`5322` standard.

Response
--------

Response includes the :ref:`spam_header` header.  The body contains the
SpamAssassin rules that were matched.
Example::

    SPAMD/1.1 0 EX_OK
    Content-length: 27
    Spam: True ; 1000.0 / 5.0
    
    GTUBE,NO_RECEIVED,NO_RELAYS

.. _tell_request:

TELL
====

Send a request to classify a message and add or remove it from a database.  The
message type is defined by the :ref:`message-class_header`.  The
:ref:`remove_header` and :ref:`set_header` headers are used to choose the
location ("local" or "remote") to add or remove it.  SpamAssassin will return
an error if a request tries to apply a conflicting change (e.g. both setting
and removing to the same location).

.. note::

    The SpamAssassin daemon must have the ``--allow-tell`` option enabled to
    support this feature.

Request
-------

Required Headers
^^^^^^^^^^^^^^^^

* :ref:`content-length_header`
* :ref:`message-class_header`
* :ref:`remove_header` and/or :ref:`set_header`
* :ref:`user_header`

Optional Headers
^^^^^^^^^^^^^^^^

* :ref:`compress_header`

Required Body
^^^^^^^^^^^^^

An email based on the :rfc:`5322` standard.

Response
--------

If successful, the response will include the :ref:`didremove_header` and/or
:ref:`didset_header` headers depending on the request.

Response from a request that sent a :ref:`remove_header`::

    SPAMD/1.1 0 EX_OK
    DidRemove: local
    Content-length: 2
    

Response from a request that sent a :ref:`set_header`::

    SPAMD/1.1 0 EX_OK
    DidSet: local
    Content-length: 2
    

.. _headers:

*******
Headers
*******

Headers are structured very simply.  They have a name and value which are
separated by a colon (:).  All headers are followed by a newline.  The current
headers include :ref:`compress_header`, :ref:`content-length_header`,
:ref:`didremove_header`, :ref:`didset_header`, :ref:`message-class_header`,
:ref:`remove_header`, :ref:`set_header`, :ref:`spam_header`, and
:ref:`user_header`.

For example::

    Content-length: 42\r\n

The following is a list of headers defined by SpamAssassin, although anything
is allowable as a header.  If an unrecognized header is included in the
request or response it should be ignored.

.. _compress_header:

Compress
========

Specifies that the body is compressed and what compression algorithm is used.
Contains a string of the compression algorithm.
Currently only ``zlib`` is supported.

.. _content-length_header:

Content-length
==============

The length of the body in bytes.  Contains an integer representing the body
length.

.. _didremove_header:

DidRemove
=========

Included in a response to a :ref:`tell_request` request.  Identifies which
databases a message was removed from.
Contains a string containing either ``local``, ``remote`` or both seprated by a
comma.

.. _didset_header:

DidSet
======

Included in a response to a :ref:`tell_request` request.  Identifies which
databases a message was set in.
Contains a string containing either ``local``, ``remote`` or both seprated by a
comma.

.. _message-class_header:

Message-class
=============

Classifies the message contained in the body.
Contains a string containing either ``local``, ``remote`` or both seprated by a
comma.

.. _remove_header:

Remove
======

Included in a :ref:`tell_request` request to remove the message from the
specified database.
Contains a string containing either ``local``, ``remote`` or both seprated by a
comma.

.. _set_header:

Set
===

Included in a :ref:`tell_request` request to remove the message from the
specified database.
Contains a string containing either ``local``, ``remote`` or both seprated by a
comma.

.. _spam_header:

Spam
====

Identify whether the message submitted was spam or not including the score and
threshold.
Contains a string containing a boolean if the message is spam (either ``True``,
``False``, ``Yes``, or ``No``), followed by a ``;``, a floating point number
representing the score, followed by a ``/``, and finally a floating point
number representing the threshold of which to consider it spam.

For example::

    Spam: True ; 1000.0 / 5.0

.. _user_header:

User
====

Specify which user the request will run under.  SpamAssassin will use the
configuration files for the user included in the header.
Contains a string containing the name of the user.

************
Status Codes
************

A status code is an integer detailing whether the request was successful or if
an error occurred.

The following status codes are defined in the SpamAssassin source repository
[2]_.

EX_OK
=====

Code: 0

Definition: No problems were found.

EX_USAGE
========

Code: 64

Definition: Command line usage error.

EX_DATAERR
==========

Code: 65

Definition: Data format error.

EX_NOINPUT
==========

Code: 66

Definition: Cannot open input.

EX_NOUSER
=========

Code: 67

Definition: Addressee unknown.

EX_NOHOST
=========

Code: 68

Definition: Hostname unknown.

EX_UNAVAILABLE
==============

Code: 69

Definition: Service unavailable.

EX_SOFTWARE
===========

Code: 70

Definition: Internal software error.

EX_OSERR
========

Code: 71

Definition: System error (e.g. can't fork the process).

EX_OSFILE
=========

Code: 72

Definition: Critical operating system file missing.

EX_CANTCREAT
============

Code: 73

Definition: Can't create (user) output file.

EX_IOERR
========

Code: 74

Definition: Input/output error.

EX_TEMPFAIL
===========

Code: 75

Definition: Temporary failure, user is invited to retry.

EX_PROTOCOL
===========

Code: 76

Definition: Remote error in protocol.

EX_NOPERM
=========

Code: 77

Definition: Permission denied.

EX_CONFIG
=========

Code: 78

Definition: Configuration error.

EX_TIMEOUT
==========

Code: 79

Definition: Read timeout.

****
Body
****

SpamAssassin will generally want the body of a request to be in a supported RFC
email format.  The response body will differ depending on the type of request
that was sent.

**********
References
**********

.. [1] https://svn.apache.org/viewvc/spamassassin/branches/3.4/spamd/PROTOCOL?revision=1676616&view=co
.. [2] https://svn.apache.org/viewvc/spamassassin/branches/3.4/spamd/spamd.raw?revision=1749346&view=co
