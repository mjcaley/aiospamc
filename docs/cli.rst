######################
Command Line Interface
######################

***********
Description
***********

:program:`aiospamc` is the command line interface for the SpamAssassin client.

It provides common actions to interact with the SpamAssassin server.

**************
Global Options
**************

.. option:: --version

    Print the version of :program:`aiospamc` to the console.

.. option:: --debug

    Enable debug logging.

********
Commands
********

.. program:: aiospamc

.. option:: check [MESSAGE]

    Sends message to SpamAssassin and prints the score if there is any.

    If no message is given then it will read from `stdin`.

    The exit code will be 0 if the message is ham and 1 if it's spam.

    .. option:: --host HOSTNAME

        |host_description|

    .. option:: --port PORT

        |port_description|

    .. option:: --socket-path PATH

        |socket_description|

    .. option:: --ssl

        |ssl_description|

    .. option:: --timeout SECONDS

        |timeout_description|

    .. option:: --out [json|text]

        |out_description|

.. option:: forget [MESSAGE]

    Forgets the classification of a message.

    .. option:: --host HOSTNAME

        |host_description|

    .. option:: --port PORT

        |port_description|

    .. option:: --socket-path PATH

        |socket_description|

    .. option:: --ssl

        |ssl_description|

    .. option:: --timeout SECONDS

        |timeout_description|

    .. option:: --out [json|text]

        |out_description|

.. option:: learn [MESSAGE]

    Ask SpamAssassin to learn the message as spam or ham.

    .. option:: --host HOSTNAME

        |host_description|

    .. option:: --port PORT

        |port_description|

    .. option:: --socket-path PATH

        |socket_description|

    .. option:: --ssl

        |ssl_description|

    .. option:: --timeout SECONDS

        |timeout_description|

    .. option:: --out [json|text]

        |out_description|

.. option:: ping

    Pings SpamAssassin and prints the response.

    An exit code of 0 is successful, 1 is not successful.

    .. option:: --host HOSTNAME

        |host_description|

    .. option:: --port PORT

        |port_description|

    .. option:: --socket-path PATH

        |socket_description|

    .. option:: --ssl

        |ssl_description|

    .. option:: --timeout SECONDS

        |timeout_description|

    .. option:: --out [json|text]

        |out_description|

.. option:: report [MESSAGE]

    Report a message to collaborative filtering databases as spam.

    .. option:: --host HOSTNAME

        |host_description|

    .. option:: --port PORT

        |port_description|

    .. option:: --socket-path PATH

        |socket_description|

    .. option:: --ssl

        |ssl_description|

    .. option:: --timeout SECONDS

        |timeout_description|

    .. option:: --out [json|text]

        |out_description|

.. option:: revoke [MESSAGE]

    Revoke a message to collaborative filtering databases.

    .. option:: --host HOSTNAME

        |host_description|

    .. option:: --port PORT

        |port_description|

    .. option:: --socket-path PATH

        |socket_description|

    .. option:: --ssl

        |ssl_description|

    .. option:: --timeout SECONDS

        |timeout_description|

    .. option:: --out [json|text]

        |out_description|

.. |host_description| replace:: Hostname or IP address of the server.

.. |port_description| replace:: Port number of the server.

.. |socket_description| replace:: Path to UNIX domain socket.

.. |ssl_description| replace:: Enables or disables SSL when using a TCP connection. Will use the
                               system's root certificates by default.

.. |timeout_description| replace:: Set the connection timeout. Default is 10 seconds.

.. |out_description| replace:: Choose the output format to the console. `text` will print human friendly
                               output. `json` will display JSON formatted output. Default is `text`.

*********************
Environment Variables
*********************

.. envvar:: AIOSPAMC_CERT_FILE

    Path to the file containing trusted certificates. These will be used in place of
    the default root certificates when using the :option:`--ssl` option.
