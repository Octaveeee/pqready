import re

from pqready.models import HybridSupport, TlsInfo
from pqready.scanner.openssl import run_s_client

HYBRID_GROUP = "X25519MLKEM768"
CLASSICAL_GROUP = "X25519"

# TLS <= 1.2 probes need SECLEVEL=0, otherwise OpenSSL 3.5 refuses to send
# TLS 1.0/1.1 at all and the server would look like it rejects them (ADR-002).
_LEGACY_CIPHERS = "DEFAULT:@SECLEVEL=0"
_VERSION_FLAGS = {
    "TLSv1": "-tls1",
    "TLSv1.1": "-tls1_1",
    "TLSv1.2": "-tls1_2",
    "TLSv1.3": "-tls1_3",
}

_HYBRID_GROUP_RE = re.compile(r"^Negotiated TLS1\.3 group: (\S+)", re.MULTILINE)
_TEMP_KEY_RE = re.compile(r"^Peer Temp Key: (?:ECDH, )?([^,]+),", re.MULTILINE)
_VERSION_RE = re.compile(r"^Protocol version: (\S+)", re.MULTILINE)
_ALERT_RE = re.compile(r"SSL alert number (\d+)")
# <id>:error:<code>:<lib>:<function>:<reason>:<file>:<line>:<detail>, e.g.
# ...:error:10080002:BIO routines:BIO_lookup_ex:system lib:...:767:Name or service not known
_OPENSSL_ERROR_RE = re.compile(
    r":error:[0-9A-F]+:[^:]*:[^:]*:([^:]*):[^:]*:\d+:(.*)$", re.MULTILINE
)


class ClientConfigError(RuntimeError):
    """OpenSSL refused to send the probe: a pqready bug, never a server answer."""


def _established(output: str) -> bool:
    """True if the handshake completed."""
    return "CONNECTION ESTABLISHED" in output


def _client_config_error(output: str) -> bool:
    """True if OpenSSL refused to send anything (see ADR-002)."""
    return "no protocols available" in output


def _negotiated_group(output: str) -> str | None:
    """Return the negotiated key exchange group, or None (e.g. RSA key exchange)."""
    if match := _HYBRID_GROUP_RE.search(output):
        return match.group(1)
    if match := _TEMP_KEY_RE.search(output):
        return match.group(1)
    return None


def _protocol_version(output: str) -> str | None:
    """Return the negotiated protocol version, e.g. 'TLSv1.3'."""
    if match := _VERSION_RE.search(output):
        return match.group(1)
    return None


def _alert(output: str) -> int | None:
    """Return the TLS alert number sent by the server, if any."""
    if match := _ALERT_RE.search(output):
        return int(match.group(1))
    return None


def _error_message(output: str) -> str:
    """Return a short error message from the first OpenSSL error line."""
    if match := _OPENSSL_ERROR_RE.search(output):
        reason, detail = match.group(1), match.group(2).strip()
        return f"{reason}: {detail}" if detail else reason
    lines = output.strip().splitlines()
    return lines[-1] if lines else "no output"


def _probe(host: str, port: int, args: list[str], timeout: float) -> str:
    """Run one s_client probe in brief mode."""
    output = run_s_client(host, port, [*args, "-brief"], timeout)
    if _client_config_error(output):
        raise ClientConfigError(f"OpenSSL refused probe {args}: {_error_message(output)}")
    return output


def _hybrid_support(host: str, port: int, timeout: float) -> HybridSupport:
    """Calls (b) and (c) of ADR-001, evaluated in the order of its decision table."""
    hybrid = _probe(host, port, ["-groups", HYBRID_GROUP], timeout)
    if _negotiated_group(hybrid) == HYBRID_GROUP:
        return HybridSupport.YES
    # Established without the group line: the server ignored our groups (RSA key exchange).
    if _established(hybrid):
        return HybridSupport.NO
    control = _probe(host, port, ["-groups", CLASSICAL_GROUP], timeout)
    if _established(control):
        return HybridSupport.NO
    return HybridSupport.UNKNOWN


def _versions(host: str, port: int, timeout: float) -> list[str]:
    """Return the TLS versions accepted by the server (ADR-002)."""
    accepted = []
    for version, flag in _VERSION_FLAGS.items():
        args = [flag] if version == "TLSv1.3" else [flag, "-cipher", _LEGACY_CIPHERS]
        output = _probe(host, port, args, timeout)
        if _established(output) and _protocol_version(output) == version:
            accepted.append(version)
    return accepted


def _rsa_key_exchange(host: str, port: int, timeout: float) -> bool:
    """True if the server accepts a TLS_RSA_* cipher suite in TLS 1.2 (ADR-002)."""
    output = _probe(host, port, ["-tls1_2", "-cipher", "kRSA:@SECLEVEL=0"], timeout)
    return _established(output)


def scan_tls(host: str, port: int, timeout: float) -> TlsInfo:
    """Run all TLS probes against one endpoint.

    Raises ConnectionError if the default handshake fails without a TLS alert
    (DNS, TCP or non-TLS service), TimeoutError if the host does not answer.
    """
    default = _probe(host, port, [], timeout)
    if not _established(default) and _alert(default) is None:
        raise ConnectionError(f"cannot connect to {host}:{port}: {_error_message(default)}")
    return TlsInfo(
        pq_hybrid_supported=_hybrid_support(host, port, timeout),
        rsa_key_exchange=_rsa_key_exchange(host, port, timeout),
        negotiated_group=_negotiated_group(default),
        versions=_versions(host, port, timeout),
    )
