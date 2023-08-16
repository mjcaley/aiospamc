from email.message import EmailMessage

import pytest

import aiospamc


@pytest.mark.integration
async def test_spam(spamd_tcp, spam):
    result = await aiospamc.check(spam, host=spamd_tcp[0], port=spamd_tcp[1])

    assert 0 == result.status_code
    assert True is result.headers["Spam"].value


@pytest.mark.integration
async def test_gtk_encoding(spamd_tcp):
    message = EmailMessage()
    message.add_header("From", "wevsty <example@example.com>")
    message.add_header("Subject", "=?UTF-8?B?5Lit5paH5rWL6K+V?=")
    message.add_header("Message-ID", "<example@example.com>")
    message.add_header("Date", "")
    message.add_header("X-Mozilla-Draft-Info", "")
    message.add_header("User-Agent", "")
    message.set_param("charset", "gbk")
    message.set_content("这是Unicode文字." "This is Unicode characters.")

    result = await aiospamc.check(message, host=spamd_tcp[0], port=spamd_tcp[1])

    assert 0 == result.status_code
