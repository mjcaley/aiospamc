#!/usr/bin/env python3

import pytest

from email.message import EmailMessage

import aiospamc


@pytest.mark.integration
@pytest.mark.asyncio
async def test_spam(spam):
    result = await aiospamc.check(spam)

    assert result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_gtk_encoding():
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

    result = await aiospamc.check(message)

    assert result
