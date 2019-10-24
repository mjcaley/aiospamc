#!/usr/bin/env python3

import datetime
from functools import partial
from pathlib import Path
from shutil import which
from subprocess import DEVNULL, TimeoutExpired, Popen
import sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509

import pytest


if sys.platform == 'win32':
    collect_ignore = ["test_unix.py"]


@pytest.fixture(scope='session')
def certificate(tmp_path_factory):
    certs_path = tmp_path_factory.mktemp('localhost_certs')
    key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
    subject = issuer = x509.Name([
        x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "CA"),
        x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "Ontario"),
        x509.NameAttribute(x509.NameOID.LOCALITY_NAME, "Toronto"),
        x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "mjcaley"),
        x509.NameAttribute(x509.NameOID.COMMON_NAME, "aiospamc")
    ])
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=7)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False
    ).sign(key, hashes.SHA256(), default_backend())

    key_path = certs_path / 'localhost.key'
    with open(str(key_path), 'wb') as key_file:
        key_file.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    cert_path = certs_path / 'localhost.cert'
    with open(str(cert_path), 'wb') as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))

    yield key_path, cert_path


@pytest.fixture(scope='session')
def spamd_tcp_options():
    port = 1783

    return {'host': 'localhost', 'port': port}


@pytest.fixture(scope='session')
def spamd_ssl_options(certificate):
    port = 11783

    return {
        'host': 'localhost',
        'port': port,
        'key': str(certificate[0]),
        'cert': str(certificate[1])
    }


@pytest.fixture(scope='session')
def spamd_unix_options(tmp_path_factory):
    path = tmp_path_factory.mktemp('sockets') / 'spamd.sock'

    if sys.platform == 'win32':
        return None
    else:
        return {'socket': str(path)}


@pytest.fixture(scope='session')
def spamd(spamd_tcp_options, spamd_ssl_options, spamd_unix_options, tmp_path_factory, request):
    spamd_path = str(Path(which('spamd')).parent)
    spamd_start = 'info: spamd: server started on'
    log_file = tmp_path_factory.mktemp('spamd') / 'spamd.log'

    options = [
        '--syslog={}'.format(str(log_file)),
        '--local',
        '--allow-tell',
        '--listen={host}:{port}'.format(**spamd_tcp_options),
        '--listen=ssl:{host}:{port}'.format(**spamd_ssl_options),
        '--server-key',
        '{key}'.format(**spamd_ssl_options),
        '--server-cert',
        '{cert}'.format(**spamd_ssl_options)
    ]
    if spamd_unix_options:
        options += ['--socketpath={socket}'.format(**spamd_unix_options)]

    process = Popen(
        ['spamd', *options],
        cwd=spamd_path,
        stdout=DEVNULL, stderr=DEVNULL,
        universal_newlines=True
    )

    def terminate(process):
        process.terminate()
        try:
            process.wait(timeout=5)
        except TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    request.addfinalizer(partial(terminate, process))

    timeout = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=request.config.getoption('--spamd-process-timeout')
    )
    while not log_file.exists():
        if datetime.datetime.utcnow() > timeout:
            raise TimeoutError

    running = False
    with open(str(log_file), 'r') as log:
        while not running:
            if datetime.datetime.utcnow() > timeout:
                raise TimeoutError

            log.seek(0)
            for line in log:
                if spamd_start in line:
                    running = True
                    break

    if running:
        yield {
            'tcp': spamd_tcp_options,
            'ssl': spamd_ssl_options,
            'unix': spamd_unix_options
        }
    else:
        raise ChildProcessError
