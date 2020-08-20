Reflection
==========

* Connection is one-time use and SPAMD will will close once a response is sent
* Manager should contain all the data to pass to a Connection
* Manager can have a single method for sending data and passing back
* Can we get rid of the context manager entirely?

API Design
==========

ConnectionManager base class
    init(timeout: Timeout)
    async request(data: bytes) -> bytes [final]
        reader, writer = await self.open() [total & connect timeouts]

        writer.write(data)
        await writer.drain() [total & send(?) timeouts]

        response = await reader.read() [total & response timeouts]

        return response

    async open() -> reader, writer [not implemented]

TcpConnectionManager(ConnectionManager)
    init(host, port, ssl, timeout)
    async open() -> reader, writer

