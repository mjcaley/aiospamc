#!/usr/bin/env python3

import pytest

from email.message import EmailMessage

from aiospamc import Client


@pytest.mark.asyncio
async def test_spam(stub_connection_manager, response_spam_header, spam):
    c = Client()
    c.connection = stub_connection_manager(return_value=response_spam_header)
    result = await c.check(spam)

    assert result


@pytest.mark.asyncio
async def test_gtk_encoding(stub_connection_manager, response_ok):
    message = EmailMessage()
    message.add_header('From', 'wevsty <example@example.com>')
    message.add_header('Subject', '=?UTF-8?B?5Lit5paH5rWL6K+V?=')
    message.add_header('Message-ID', '<example@example.com>')
    message.add_header('Date', '')
    message.add_header('X-Mozilla-Draft-Info', '')
    message.add_header('User-Agent', '')
    message.set_param('charset', 'gbk')
    message.set_content('这是Unicode文字.'
                        'This is Unicode characters.')

    c = Client()
    c.connection = stub_connection_manager(return_value=response_ok)
    result = await c.check(message)

    assert result
