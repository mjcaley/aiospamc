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
    func, expected_verb, mock_client, spam, mocker
):
    req_spy = mocker.spy(Client, "request")
    await func(spam, user="testuser", compress=True)
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
async def test_functions_returns_response(func, mock_client, spam):
    result = await func(spam)

    assert isinstance(result, Response)


async def test_ping_request_with_parameters(mock_client, mocker):
    req_spy = mocker.spy(Client, "request")
    await ping()
    req = req_spy.await_args[0][1]

    assert "PING" == req.verb
    assert "User" not in req.headers


async def test_ping_returns_response(mock_client, mocker):
    req_spy = mocker.spy(Client, "request")
    result = await ping()

    assert req_spy.spy_return is result


async def test_tell_request_with_default_parameters(mock_client, spam, mocker):
    req_spy = mocker.spy(Client, "request")
    await tell(spam, MessageClassOption.spam)
    req = req_spy.await_args[0][1]

    assert "TELL" == req.verb
    assert "User" not in req.headers
    assert "Compress" not in req.headers
    assert MessageClassOption.spam == req.headers["Message-class"].value
    assert spam == req.body


async def test_tell_request_with_optional_parameters(mock_client, spam, mocker):
    req_spy = mocker.spy(Client, "request")
    await tell(
        spam,
        MessageClassOption.spam,
        set_action=ActionOption(local=True, remote=True),
        remove_action=ActionOption(local=True, remote=True),
        user="testuser",
        compress=True,
    )
    req = req_spy.await_args[0][1]

    assert "TELL" == req.verb
    assert "testuser" == req.headers["User"].name
    assert "zlib" == req.headers["Compress"].algorithm
    assert MessageClassOption.spam == req.headers["Message-class"].value
    assert ActionOption(local=True, remote=True) == req.headers["Set"].action
    assert ActionOption(local=True, remote=True) == req.headers["Remove"].action
    assert spam == req.body


async def test_tell_returns_response(mock_client, spam, mocker):
    req_spy = mocker.spy(Client, "request")
    result = await tell(spam, MessageClassOption.spam)

    assert req_spy.spy_return is result


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_bad_response(
    func, mock_client_response, response_invalid, mocker
):
    mock_client_response(response_invalid)

    with pytest.raises(BadResponse):
        await func(mocker.MagicMock())


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_usage(func, mock_client_response, mocker, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_data_err(func, mock_client_response, mocker, ex_data_err):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_no_input(func, mock_client_response, mocker, ex_no_input):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_no_user(func, mock_client_response, mocker, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_no_host(func, mock_client_response, mocker, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_unavailable(func, mock_client_response, mocker, ex_unavailable):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_software(func, mock_client_response, mocker, ex_software):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_os_error(func, mock_client_response, mocker, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_os_file(func, mock_client_response, mocker, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_cant_create(func, mock_client_response, mocker, ex_cant_create):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_io_error(func, mock_client_response, mocker, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_temporary_failure(
    func, mock_client_response, mocker, ex_temp_fail
):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_protocol(func, mock_client_response, mocker, ex_protocol):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_no_permission(func, mock_client_response, mocker, ex_no_perm):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_config(func, mock_client_response, mocker, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_timeout(func, mock_client_response, mocker, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(ServerTimeoutException):
        await func(
            mocker.MagicMock(),
        )


@pytest.mark.parametrize(
    "func", [check, headers, process, report, report_if_spam, symbols]
)
async def test_raises_undefined(func, mock_client_response, mocker, ex_undefined):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await func(
            mocker.MagicMock(),
        )


async def test_ping_raises_usage(mock_client_response, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await ping()


async def test_ping_raises_data_err(mock_client_response, ex_data_err):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await ping()


async def test_ping_raises_no_input(mock_client_response, ex_no_input):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await ping()


async def test_ping_raises_no_user(mock_client_response, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await ping()


async def test_ping_raises_no_host(mock_client_response, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await ping()


async def test_ping_raises_unavailable(mock_client_response, ex_unavailable):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await ping()


async def test_ping_raises_software(mock_client_response, ex_software):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await ping()


async def test_ping_raises_os_error(mock_client_response, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await ping()


async def test_ping_raises_os_file(mock_client_response, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await ping()


async def test_ping_raises_cant_create(mock_client_response, ex_cant_create):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await ping()


async def test_ping_raises_io_error(mock_client_response, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await ping()


async def test_ping_raises_temporary_failure(mock_client_response, ex_temp_fail):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await ping()


async def test_ping_raises_protocol(mock_client_response, ex_protocol):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await ping()


async def test_ping_raises_no_permission(mock_client_response, ex_no_perm):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await ping()


async def test_ping_raises_config(mock_client_response, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await ping()


async def test_ping_raises_timeout(mock_client_response, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(ServerTimeoutException):
        await ping()


async def test_ping_raises_undefined(mock_client_response, ex_undefined):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await ping()


async def test_tell_raises_usage(mock_client_response, mocker, ex_usage):
    mock_client = mock_client_response(ex_usage)

    with pytest.raises(UsageException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_data_err(mock_client_response, mocker, ex_data_err):
    mock_client = mock_client_response(ex_data_err)

    with pytest.raises(DataErrorException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_no_input(mock_client_response, mocker, ex_no_input):
    mock_client = mock_client_response(ex_no_input)

    with pytest.raises(NoInputException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_no_user(mock_client_response, mocker, ex_no_user):
    mock_client = mock_client_response(ex_no_user)

    with pytest.raises(NoUserException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_no_host(mock_client_response, mocker, ex_no_host):
    mock_client = mock_client_response(ex_no_host)

    with pytest.raises(NoHostException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_unavailable(mock_client_response, mocker, ex_unavailable):
    mock_client = mock_client_response(ex_unavailable)

    with pytest.raises(UnavailableException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_software(mock_client_response, mocker, ex_software):
    mock_client = mock_client_response(ex_software)

    with pytest.raises(InternalSoftwareException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_os_error(mock_client_response, mocker, ex_os_err):
    mock_client = mock_client_response(ex_os_err)

    with pytest.raises(OSErrorException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_os_file(mock_client_response, mocker, ex_os_file):
    mock_client = mock_client_response(ex_os_file)

    with pytest.raises(OSFileException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_cant_create(mock_client_response, mocker, ex_cant_create):
    mock_client = mock_client_response(ex_cant_create)

    with pytest.raises(CantCreateException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_io_error(mock_client_response, mocker, ex_io_err):
    mock_client = mock_client_response(ex_io_err)

    with pytest.raises(IOErrorException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_temporary_failure(
    mock_client_response, mocker, ex_temp_fail
):
    mock_client = mock_client_response(ex_temp_fail)

    with pytest.raises(TemporaryFailureException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_protocol(mock_client_response, mocker, ex_protocol):
    mock_client = mock_client_response(ex_protocol)

    with pytest.raises(ProtocolException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_no_permission(mock_client_response, mocker, ex_no_perm):
    mock_client = mock_client_response(ex_no_perm)

    with pytest.raises(NoPermissionException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_config(mock_client_response, mocker, ex_config):
    mock_client = mock_client_response(ex_config)

    with pytest.raises(ConfigException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_timeout(mock_client_response, mocker, ex_timeout):
    mock_client = mock_client_response(ex_timeout)

    with pytest.raises(ServerTimeoutException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )


async def test_tell_raises_undefined(mock_client_response, mocker, ex_undefined):
    mock_client = mock_client_response(ex_undefined)

    with pytest.raises(ResponseException):
        await tell(
            mocker.MagicMock(),
            MessageClassOption.spam,
        )
