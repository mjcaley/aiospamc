#!/bin/env python3

from pathlib import Path

import trustme
import typer
from cryptography.hazmat.primitives.serialization import (
    BestAvailableEncryption,
    Encoding,
    PrivateFormat,
    load_pem_private_key,
)


def main(dest: Path, private_key_password: str = "password"):
    """Generates certificates and private keys for local development testing."""

    if not dest.exists():
        dest.mkdir(parents=True)

    if dest.exists() and not dest.is_dir():
        typer.echo("Destination is not a directory")
        raise typer.Exit(1)

    # Define paths
    ca_cert_file = dest / "ca.cert"
    server_cert_and_key_file = dest / "server_cert_and_key.pem"
    server_key_file = dest / "server.key"
    server_cert_file = dest / "server.cert"
    client_cert_and_key_file = dest / "client_cert_and_key.pem"
    client_key_file = dest / "client.key"
    client_cert_file = dest / "client.cert"
    client_encrypted_key_file = dest / "client_encrypted.key"

    # Certificate authority
    ca = trustme.CA()
    ca.cert_pem.write_to_path(ca_cert_file)
    typer.echo(f"CA certificate to: [{ca_cert_file}]")

    # Server certificate
    server = ca.issue_cert("localhost", "::1", "127.0.0.1")
    server.private_key_and_cert_chain_pem.write_to_path(server_cert_and_key_file)
    typer.echo(f"Server certificate and private key: [{server_cert_and_key_file}]")
    server.cert_chain_pems[0].write_to_path(server_cert_file)
    typer.echo(f"Server certificate: [{server_key_file}]")
    server.private_key_pem.write_to_path(server_key_file)
    typer.echo(f"Server private key: [{server_key_file}]")

    # Client certificate
    client = ca.issue_cert("localhost", "::1", "127.0.0.1")
    client.private_key_and_cert_chain_pem.write_to_path(client_cert_and_key_file)
    typer.echo(f"Client certificate and private key: [{client_cert_and_key_file}]")
    client.cert_chain_pems[0].write_to_path(client_cert_file)
    typer.echo(f"Client certificate: [{client_cert_file}]")
    client.private_key_pem.write_to_path(client_key_file)
    typer.echo(f"Client private key: [{client_key_file}]")
    client_private_key = load_pem_private_key(
        client.private_key_pem.bytes(),
        None,
    )
    client_enc_key_bytes = client_private_key.private_bytes(
        Encoding.PEM,
        PrivateFormat.PKCS8,
        BestAvailableEncryption(private_key_password.encode()),
    )
    client_encrypted_key_file.write_bytes(client_enc_key_bytes)
    typer.echo(f"Client private key (encrypted): [{client_encrypted_key_file}]")


if __name__ == "__main__":
    typer.run(main)
