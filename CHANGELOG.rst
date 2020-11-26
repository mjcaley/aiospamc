Aiospamc 0.7.0 (2020-11-26)
===========================

Features
--------

- Updated certifi dependency. (#212)
- Added support for Python 3.9. (#216)
- Added a timeout parameter.  Can now timeout on the total time, time to connect, and time to respond. (#222)
- Improved type hints and added verification into CI pipeline. (#228)
- Improved logging within the client and connection modules. (#235)
- Added BytesValue class to support header values that can't be decoded by UTF8. (#268)


Bugfixes
--------

- Messages that don't end with a newline result in the connection getting hung. Improved connection code to send an EOF when finished with a message. (#233)


Improved Documentation
----------------------

- Added documentation on the loggers available. (#235)


Deprecations and Removals
-------------------------

- Removed `loop` parameter from all calls since it was decprecated in Python 3.8. (#214)
- Removed support for Python 3.5. (#217)
