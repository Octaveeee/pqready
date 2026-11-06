from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
from cryptography.x509.oid import NameOID

from pqready.scanner.cert import extract_leaf_pem, parse_certificate

FIXTURES = Path(__file__).parent / "fixtures"


def make_cert(private_key, hash_algorithm: hashes.HashAlgorithm | None) -> bytes:
    """Build a self-signed PEM certificate for tests."""
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test")])
    now = datetime.now(UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=30))
        .sign(private_key, hash_algorithm)
    )
    return cert.public_bytes(serialization.Encoding.PEM)


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_extract_leaf_pem_from_lab_output():
    pem = extract_leaf_pem(read_fixture("faible_full.txt"))

    assert pem.startswith(b"-----BEGIN CERTIFICATE-----")
    assert pem.endswith(b"-----END CERTIFICATE-----")


def test_extract_leaf_pem_without_cert_raises():
    with pytest.raises(ValueError, match="No PEM"):
        extract_leaf_pem("no certificate here")


def test_parse_rsa_1024():
    info = parse_certificate(make_cert(rsa.generate_private_key(65537, 1024), hashes.SHA256()))

    assert info.key_type == "RSA"
    assert info.key_size == 1024
    assert info.signature_algorithm == "sha256WithRSAEncryption"


def test_parse_ec_p256():
    info = parse_certificate(make_cert(ec.generate_private_key(ec.SECP256R1()), hashes.SHA256()))

    assert info.key_type == "EC"
    assert info.key_size == 256
    assert info.signature_algorithm == "ecdsa-with-SHA256"


def test_parse_ed25519():
    info = parse_certificate(make_cert(ed25519.Ed25519PrivateKey.generate(), None))

    assert info.key_type == "Ed25519"
    assert info.key_size == 256
    assert info.signature_algorithm == "ed25519"


def test_parse_sha1_signature():
    # cryptography refuses to sign with SHA-1, so this certificate was generated with
    # OpenSSL: openssl req -x509 -newkey rsa:2048 -sha1 -nodes -keyout /dev/null ...
    info = parse_certificate((FIXTURES / "rsa2048_sha1.crt").read_bytes())

    assert info.signature_algorithm == "sha1WithRSAEncryption"


def test_parse_not_after_is_utc():
    info = parse_certificate(make_cert(ec.generate_private_key(ec.SECP256R1()), hashes.SHA256()))

    assert info.not_after.tzinfo is not None
    assert info.not_after.utcoffset() == timedelta(0)


def test_parse_lab_output_end_to_end():
    info = parse_certificate(extract_leaf_pem(read_fixture("faible_full.txt")))

    assert info.key_type == "RSA"
    assert info.key_size == 1024
    assert info.issuer == "CN=faible"
