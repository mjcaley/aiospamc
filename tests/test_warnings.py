import pytest

from aiospamc.connections import TcpConnectionManager
from aiospamc.header_values import CompressValue
from aiospamc.requests import Request
from aiospamc.user_warnings import warn_spamd_bug_7183, warn_spamd_bug_7938


@pytest.fixture
def ssl_connection_mock(mocker):
    connection_mock = mocker.Mock(spec=TcpConnectionManager)
    connection_mock.ssl_context = mocker.Mock()

    return connection_mock


def test_spamd_bug_7183_warns(mocker, ssl_connection_mock):
    compressed_request = Request(
        "CHECK", headers={"Compress": CompressValue()}, body=b"Test body\n"
    )

    with pytest.warns(UserWarning):
        warn_spamd_bug_7183(compressed_request, ssl_connection_mock)


def test_spamd_bug_7938_doesnt_warn(mocker, request_with_body, ssl_connection_mock):
    warn_spamd_bug_7938(request_with_body, ssl_connection_mock)


def test_spamd_bug_7938_warns(mocker, ssl_connection_mock):
    compressed_request = Request(
        "CHECK", headers={"Compress": CompressValue()}, body=b"Test body"
    )

    with pytest.warns(UserWarning):
        warn_spamd_bug_7938(compressed_request, ssl_connection_mock)


def test_spamd_bug_7183_doesnt_warn(mocker, request_with_body, ssl_connection_mock):
    warn_spamd_bug_7183(request_with_body, ssl_connection_mock)
