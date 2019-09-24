#!/usr/bin/env python3

from contextlib import contextmanager
from pathlib import Path
from shutil import which
from subprocess import PIPE, STDOUT, TimeoutExpired, Popen
import sys

import pytest


if sys.platform == 'win32':
    collect_ignore = ["test_unix.py"]


@pytest.fixture(scope='session')
def spamd():
    spamd_path = str(Path(which('spamd')).parent)
    spamd_start = 'info: spamd: server started on'

    @contextmanager
    def inner(*args):
        with Popen(['spamd', *args], cwd=spamd_path, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as process:
            running = False
            for line in process.stdout:
                if spamd_start in line:
                    running = True
                    break

            if running:
                yield process
            else:
                raise Exception

            process.terminate()
            try:
                process.wait(timeout=5)
            except TimeoutExpired:
                process.kill()

    return inner


@pytest.fixture
def spamd_tcp(spamd):
    port = 1783

    with spamd('--local', '--allow-tell', '--listen=localhost:' + str(port)):
        yield 'localhost', port


@pytest.fixture
def spamd_unix(spamd, tmp_path):
    socket_path = str(tmp_path / 'spamd.sock')

    with spamd('--local', '--allow-tell', '--socketpath=' + socket_path):
        yield socket_path


@pytest.fixture
def spamd_ssl(spamd):
    port = 1783

    with spamd('--local', '--allow-tell', '--ssl', '--listen=localhost:' + 'str(port)', '--server-key', '', '--server-cert', ''):
        yield 'localhost', port
