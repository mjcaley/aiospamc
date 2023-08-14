import pytest

from aiospamc.client import Client
from aiospamc.connections import ConnectionManager
from aiospamc.exceptions import BadResponse
from aiospamc.frontend import (
    check,
    headers,
    ping,
    process,
    report,
    report_if_spam,
    symbols,
    tell,
)
from aiospamc.header_values import ActionOption, MessageClassOption
from aiospamc.responses import (
    CantCreateException,
    ConfigException,
    DataErrorException,
    InternalSoftwareException,
    IOErrorException,
    NoHostException,
    NoInputException,
    NoPermissionException,
    NoUserException,
    OSErrorException,
    OSFileException,
    ProtocolException,
    Response,
    ResponseException,
    ServerTimeoutException,
    TemporaryFailureException,
    UnavailableException,
    UsageException,
)


@pytest.mark.parametrize(
    "func,expected_verb",
    [
        (check, "CHECK"),
        (headers, "HEADERS"),
        (process, "PROCESS"),
        (report, "REPORT"),
        (report_if_spam, "REPORT_IFSPAM"),
        (symbols, "SYMBOLS"),
    ],
)
async def test_functions_with_default_parameters(
    func, expected_verb, fake_tcp_server, spam, mocker
):
    _, host, port = fake_tcp_server
    req_spy = mocker.spy(Client, "request")
    await func(spam, host=host, port=port)
    req = req_spy.await_args[0][1]

    assert expected_verb == req.verb
    assert "User" not in req.headers
    assert "Compress" not in req.headers
    assert spam == req.body


@pytest.mark.parametrize(
    "func,expected_verb",
    [
        (check, "CHECK"),
        (headers, "HEADERS"),
        (process, "PROCESS"),
        (report, "REPORT"),
        (report_if_spam, "REPORT_IFSPAM"),
        (symbols, "SYMBOLS"),
    ],
)
async def test_functions_with_optional_parameters(
    func, expected_verb, fake_tcp_server, spam, mocker
):
    _, host, port = fake_tcp_server
    req_spy = mocker.spy(Client, "request")
    await func(spam, user="testuser", compress=True, host=host, port=port)
    req = req_spy.await_args[0][1]

    assert expected_verb == req.verb
    assert "testuser" == req.headers["User"].name
    assert "zlib" == req.headers["Compress"].algorithm
    assert spam == req.body


@pytest.mark.parametrize(
    "func",
    [
        check,
        headers,
        process,
        report,
        report_if_spam,
        symbols,
    ],
)
async def test_functions_returns_response(func, fake_tcp_server, spam):
    _, host, port = fake_tcp_server
    result = await func(spam, host=host, port=port)

    assert isinstance(result, Response)


async def test_ping_request_with_parameters(fake_tcp_server, mocker):
    _, host, port = fake_tcp_server
    req_spy = mocker.spy(Client, "request")
    await ping(host=host, port=port)
    req = req_spy.await_args[0][1]

    assert "PING" == req.verb
    assert "User" not in req.headers


async def test_ping_returns_response(fake_tcp_server, mocker):
    _, host, port = fake_tcp_server
    req_spy = mocker.spy(Client, "request")
    result = await ping(host=host, port=port)

    assert req_spy.spy_return is result


async def test_tell_request_with_default_parameters(fake_tcp_server, spam, mocker):
    _, host, port = fake_tcp_server
    req_spy = mocker.spy(Client, "request")
    await tell(spam, MessageClassOption.spam, host=host, port=port)
    req = req_spy.await_args[0][1]

    assert "TELL" == req.verb
    assert "User" not in req.headers
    assert "Compress" not in req.headers
    assert MessageClassOption.spam == req.headers["Message-class"].value
    assert spam == req.body


async def test_tell_request_with_optional_parameters(fake_tcp_server, spam, mocker):
    _, host, port = fake_tcp_server
    req_spy = mocker.spy(Client, "request")
    await tell(
        spam,
        MessageClassOption.spam,
        set_action=ActionOption(local=True, remote=True),
        remove_action=ActionOption(local=True, remote=True),
        user="testuser",
        compress=True,
        host=host, port=port
    )
    req = req_spy.await_args[0][1]

    assert "TELL" == req.verb
    assert "testuser" == req.headers["User"].name
    assert "zlib" == req.headers["Compress"].algorithm
    assert MessageClassOption.spam == req.headers["Message-class"].value
    assert ActionOption(local=True, remote=True) == req.headers["Set"].action
    assert ActionOption(local=True, remote=True) == req.headers["Remove"].action
    assert spam == req.body


async def test_tell_returns_response(fake_tcp_server, spam, mocker):
    _, host, port = fake_tcp_server
    req_spy = mocker.spy(Client, "request")
    result = await tell(spam, MessageClassOption.spam, host=host, port=port)

    assert req_spy.spy_return is result


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_bad_response(func, fake_tcp_server, response_invalid):
    resp, host, port = fake_tcp_server
    resp.response = response_invalid

    with pytest.raises(BadResponse):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_usage(func, fake_tcp_server, ex_usage):
    resp, host, port = fake_tcp_server
    resp.response = ex_usage

    with pytest.raises(UsageException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_data_err(func, fake_tcp_server, ex_data_err):
    resp, host, port = fake_tcp_server
    resp.response = ex_data_err

    with pytest.raises(DataErrorException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_no_input(func, fake_tcp_server, ex_no_input):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_input

    with pytest.raises(NoInputException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_no_user(func, fake_tcp_server, ex_no_user):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_user

    with pytest.raises(NoUserException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_no_host(func, fake_tcp_server, ex_no_host):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_host

    with pytest.raises(NoHostException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_unavailable(func, fake_tcp_server, mocker, ex_unavailable):
    resp, host, port = fake_tcp_server
    resp.response = ex_unavailable

    with pytest.raises(UnavailableException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_software(func, fake_tcp_server, mocker, ex_software):
    resp, host, port = fake_tcp_server
    resp.response = ex_software

    with pytest.raises(InternalSoftwareException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_os_error(func, fake_tcp_server, mocker, ex_os_err):
    resp, host, port = fake_tcp_server
    resp.response = ex_os_err

    with pytest.raises(OSErrorException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_os_file(func, fake_tcp_server, mocker, ex_os_file):
    resp, host, port = fake_tcp_server
    resp.response = ex_os_file

    with pytest.raises(OSFileException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_cant_create(func, fake_tcp_server, mocker, ex_cant_create):
    resp, host, port = fake_tcp_server
    resp.response = ex_cant_create

    with pytest.raises(CantCreateException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_io_error(func, fake_tcp_server, mocker, ex_io_err):
    resp, host, port = fake_tcp_server
    resp.response = ex_io_err

    with pytest.raises(IOErrorException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_temporary_failure(
    func, fake_tcp_server, mocker, ex_temp_fail
):
    resp, host, port = fake_tcp_server
    resp.response = ex_temp_fail

    with pytest.raises(TemporaryFailureException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_protocol(func, fake_tcp_server, mocker, ex_protocol):
    resp, host, port = fake_tcp_server
    resp.response = ex_protocol

    with pytest.raises(ProtocolException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_no_permission(func, fake_tcp_server, mocker, ex_no_perm):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_perm

    with pytest.raises(NoPermissionException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_config(func, fake_tcp_server, mocker, ex_config):
    resp, host, port = fake_tcp_server
    resp.response = ex_config

    with pytest.raises(ConfigException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_timeout(func, fake_tcp_server, mocker, ex_timeout):
    resp, host, port = fake_tcp_server
    resp.response = ex_timeout

    with pytest.raises(ServerTimeoutException):
        await func(b"test", host=host, port=port)


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_undefined(func, fake_tcp_server, mocker, ex_undefined):
    resp, host, port = fake_tcp_server
    resp.response = ex_undefined

    with pytest.raises(ResponseException):
        await func(b"test", host=host, port=port)


async def test_ping_raises_usage(fake_tcp_server, ex_usage):
    resp, host, port = fake_tcp_server
    resp.response = ex_usage

    with pytest.raises(UsageException):
        await ping(host=host, port=port)


async def test_ping_raises_data_err(fake_tcp_server, ex_data_err):
    resp, host, port = fake_tcp_server
    resp.response = ex_data_err

    with pytest.raises(DataErrorException):
        await ping(host=host, port=port)


async def test_ping_raises_no_input(fake_tcp_server, ex_no_input):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_input

    with pytest.raises(NoInputException):
        await ping(host=host, port=port)


async def test_ping_raises_no_user(fake_tcp_server, ex_no_user):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_user

    with pytest.raises(NoUserException):
        await ping(host=host, port=port)


async def test_ping_raises_no_host(fake_tcp_server, ex_no_host):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_host

    with pytest.raises(NoHostException):
        await ping(host=host, port=port)


async def test_ping_raises_unavailable(fake_tcp_server, ex_unavailable):
    resp, host, port = fake_tcp_server
    resp.response = ex_unavailable

    with pytest.raises(UnavailableException):
        await ping(host=host, port=port)


async def test_ping_raises_software(fake_tcp_server, ex_software):
    resp, host, port = fake_tcp_server
    resp.response = ex_software

    with pytest.raises(InternalSoftwareException):
        await ping(host=host, port=port)


async def test_ping_raises_os_error(fake_tcp_server, ex_os_err):
    resp, host, port = fake_tcp_server
    resp.response = ex_os_err

    with pytest.raises(OSErrorException):
        await ping(host=host, port=port)


async def test_ping_raises_os_file(fake_tcp_server, ex_os_file):
    resp, host, port = fake_tcp_server
    resp.response = ex_os_file

    with pytest.raises(OSFileException):
        await ping(host=host, port=port)


async def test_ping_raises_cant_create(fake_tcp_server, ex_cant_create):
    resp, host, port = fake_tcp_server
    resp.response = ex_cant_create

    with pytest.raises(CantCreateException):
        await ping(host=host, port=port)


async def test_ping_raises_io_error(fake_tcp_server, ex_io_err):
    resp, host, port = fake_tcp_server
    resp.response = ex_io_err

    with pytest.raises(IOErrorException):
        await ping(host=host, port=port)


async def test_ping_raises_temporary_failure(fake_tcp_server, ex_temp_fail):
    resp, host, port = fake_tcp_server
    resp.response = ex_temp_fail

    with pytest.raises(TemporaryFailureException):
        await ping(host=host, port=port)


async def test_ping_raises_protocol(fake_tcp_server, ex_protocol):
    resp, host, port = fake_tcp_server
    resp.response = ex_protocol

    with pytest.raises(ProtocolException):
        await ping(host=host, port=port)


async def test_ping_raises_no_permission(fake_tcp_server, ex_no_perm):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_perm

    with pytest.raises(NoPermissionException):
        await ping(host=host, port=port)


async def test_ping_raises_config(fake_tcp_server, ex_config):
    resp, host, port = fake_tcp_server
    resp.response = ex_config

    with pytest.raises(ConfigException):
        await ping(host=host, port=port)


async def test_ping_raises_timeout(fake_tcp_server, ex_timeout):
    resp, host, port = fake_tcp_server
    resp.response = ex_timeout

    with pytest.raises(ServerTimeoutException):
        await ping(host=host, port=port)


async def test_ping_raises_undefined(fake_tcp_server, ex_undefined):
    resp, host, port = fake_tcp_server
    resp.response = ex_undefined

    with pytest.raises(ResponseException):
        await ping(host=host, port=port)


async def test_tell_raises_usage(fake_tcp_server, mocker, ex_usage):
    resp, host, port = fake_tcp_server
    resp.response = ex_usage

    with pytest.raises(UsageException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_data_err(fake_tcp_server, mocker, ex_data_err):
    resp, host, port = fake_tcp_server
    resp.response = ex_data_err

    with pytest.raises(DataErrorException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_no_input(fake_tcp_server, mocker, ex_no_input):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_input

    with pytest.raises(NoInputException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_no_user(fake_tcp_server, mocker, ex_no_user):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_user

    with pytest.raises(NoUserException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_no_host(fake_tcp_server, mocker, ex_no_host):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_host

    with pytest.raises(NoHostException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_unavailable(fake_tcp_server, mocker, ex_unavailable):
    resp, host, port = fake_tcp_server
    resp.response = ex_unavailable

    with pytest.raises(UnavailableException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_software(fake_tcp_server, mocker, ex_software):
    resp, host, port = fake_tcp_server
    resp.response = ex_software

    with pytest.raises(InternalSoftwareException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_os_error(fake_tcp_server, mocker, ex_os_err):
    resp, host, port = fake_tcp_server
    resp.response = ex_os_err

    with pytest.raises(OSErrorException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_os_file(fake_tcp_server, mocker, ex_os_file):
    resp, host, port = fake_tcp_server
    resp.response = ex_os_file

    with pytest.raises(OSFileException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_cant_create(fake_tcp_server, mocker, ex_cant_create):
    resp, host, port = fake_tcp_server
    resp.response = ex_cant_create

    with pytest.raises(CantCreateException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_io_error(fake_tcp_server, mocker, ex_io_err):
    resp, host, port = fake_tcp_server
    resp.response = ex_io_err

    with pytest.raises(IOErrorException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_temporary_failure(
    fake_tcp_server, mocker, ex_temp_fail
):
    resp, host, port = fake_tcp_server
    resp.response = ex_temp_fail

    with pytest.raises(TemporaryFailureException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_protocol(fake_tcp_server, mocker, ex_protocol):
    resp, host, port = fake_tcp_server
    resp.response = ex_protocol

    with pytest.raises(ProtocolException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_no_permission(fake_tcp_server, mocker, ex_no_perm):
    resp, host, port = fake_tcp_server
    resp.response = ex_no_perm

    with pytest.raises(NoPermissionException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_config(fake_tcp_server, mocker, ex_config):
    resp, host, port = fake_tcp_server
    resp.response = ex_config

    with pytest.raises(ConfigException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_timeout(fake_tcp_server, mocker, ex_timeout):
    resp, host, port = fake_tcp_server
    resp.response = ex_timeout

    with pytest.raises(ServerTimeoutException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )


async def test_tell_raises_undefined(fake_tcp_server, mocker, ex_undefined):
    resp, host, port = fake_tcp_server
    resp.response = ex_undefined

    with pytest.raises(ResponseException):
        await tell(b"test", host=host, port=port, message_class=MessageClassOption.spam,
        )
