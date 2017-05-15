#!/usr/bin/env python3

import pytest

from aiospamc.connections import Connection


def test_instantiates():
    conn = Connection()

    assert 'conn' in locals()


@pytest.mark.asycio
async def test_open_not_implemented():
    conn = Connection()

    with pytest.raises(NotImplementedError):
        await conn.open()


@pytest.mark.asyncio
async def test_connection_string_not_implemented():
    conn = Connection()

    with pytest.raises(NotImplementedError):
        await conn.connection_string


@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_connection')
async def test_close():
    conn = Connection()
    reader, writer = conn.reader, conn.writer = await conn.open()

    conn.close()

    assert writer.close.called
    assert conn.connected is False
    assert not hasattr(conn, 'reader')
    assert not hasattr(conn, 'writer')


@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_connection')
async def test_send():
    async with Connection() as conn:
        data = b'Test data'
        await conn.send(data)

        conn.writer.write.assert_called_with(data)


@pytest.mark.asyncio
async def test_receive(mock_connection):
    async with Connection() as conn:
        test_data = b'Test data'
        mock_connection.side_effect = [test_data]

        data = await conn.receive()

        assert conn.reader.read.called
        assert data == test_data


@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_connection')
async def test_context_manager_aenter():
    async with Connection() as conn:
        assert conn.connected is True
        assert hasattr(conn, 'reader')
        assert hasattr(conn, 'writer')


@pytest.mark.asyncio
@pytest.mark.usefixtures('mock_connection')
async def test_context_manager_aexit():
    conn = Connection()
    async with conn:
        pass

    assert conn.connected is False
    assert not hasattr(conn, 'reader')
    assert not hasattr(conn, 'writer')
