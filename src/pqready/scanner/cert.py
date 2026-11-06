import re

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, ed448, ed25519, rsa
from cryptography.hazmat.primitives.asymmetric.types import CertificatePublicKeyTypes

from pqready.models import CertInfo


def extract_leaf_pem(s_client_output: str) -> bytes:
    """Return the first PEM certificate block from s_client output."""
    if match := re.search(
        r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", s_client_output, re.DOTALL
    ):
        return match.group(0).encode("ascii")
    raise ValueError("No PEM certificate block found in s_client output")


def _key_info(public_key: CertificatePublicKeyTypes) -> tuple[str, int]:
    """Return (key_type, key_size) for a certificate public key."""
    if isinstance(public_key, rsa.RSAPublicKey):
        return "RSA", public_key.key_size
    elif isinstance(public_key, ec.EllipticCurvePublicKey):
        return "EC", public_key.key_size
    elif isinstance(public_key, ed25519.Ed25519PublicKey):
        return "Ed25519", 256
    elif isinstance(public_key, ed448.Ed448PublicKey):
        return "Ed448", 448
    raise ValueError(f"Unsupported public key type: {type(public_key).__name__}")


# Our own stable names (OpenSSL style) rather than the private `oid._name`:
# classification rules match on these strings.
_SIGNATURE_NAMES: dict[x509.ObjectIdentifier, str] = {
    x509.SignatureAlgorithmOID.RSA_WITH_SHA1: "sha1WithRSAEncryption",
    x509.SignatureAlgorithmOID.RSA_WITH_SHA256: "sha256WithRSAEncryption",
    x509.SignatureAlgorithmOID.RSA_WITH_SHA384: "sha384WithRSAEncryption",
    x509.SignatureAlgorithmOID.RSA_WITH_SHA512: "sha512WithRSAEncryption",
    x509.SignatureAlgorithmOID.RSASSA_PSS: "rsassaPss",
    x509.SignatureAlgorithmOID.ECDSA_WITH_SHA1: "ecdsa-with-SHA1",
    x509.SignatureAlgorithmOID.ECDSA_WITH_SHA256: "ecdsa-with-SHA256",
    x509.SignatureAlgorithmOID.ECDSA_WITH_SHA384: "ecdsa-with-SHA384",
    x509.SignatureAlgorithmOID.ECDSA_WITH_SHA512: "ecdsa-with-SHA512",
    x509.SignatureAlgorithmOID.ED25519: "ed25519",
    x509.SignatureAlgorithmOID.ED448: "ed448",
}


def _signature_name(cert: x509.Certificate) -> str:
    """Return a readable signature algorithm name, or the dotted OID if unknown."""
    oid = cert.signature_algorithm_oid
    return _SIGNATURE_NAMES.get(oid, oid.dotted_string)


def parse_certificate(pem: bytes) -> CertInfo:
    """Parse a PEM leaf certificate into a CertInfo."""
    cert = x509.load_pem_x509_certificate(pem)
    key_type, key_size = _key_info(cert.public_key())
    return CertInfo(
        key_type=key_type,
        key_size=key_size,
        signature_algorithm=_signature_name(cert),
        not_after=cert.not_valid_after_utc,
        issuer=cert.issuer.rfc4514_string(),
    )
