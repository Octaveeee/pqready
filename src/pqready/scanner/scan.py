from datetime import UTC, datetime

from pqready.models import CertInfo, ScanResult, Status, Target
from pqready.scanner.cert import extract_leaf_pem, parse_certificate
from pqready.scanner.openssl import run_s_client
from pqready.scanner.tls import ClientConfigError, scan_tls


def _scan_cert(target: Target, timeout: float) -> CertInfo:
    """Fetch and parse the leaf certificate (full s_client output, not -brief)."""
    output = run_s_client(target.host, target.port, [], timeout)
    return parse_certificate(extract_leaf_pem(output))


def scan_target(target: Target, timeout: float) -> ScanResult:
    """Scan one target. Network and parsing failures become an ERROR result."""
    scanned_at = datetime.now(UTC)
    try:
        tls_info = scan_tls(target.host, target.port, timeout)
        cert = _scan_cert(target, timeout)
    except (ConnectionError, TimeoutError, ClientConfigError, ValueError) as exc:
        return ScanResult(
            target=target,
            scanned_at=scanned_at,
            status=Status.ERROR,
            error=f"{type(exc).__name__}: {exc}",
        )
    return ScanResult(
        target=target,
        scanned_at=scanned_at,
        status=Status.OK,
        tls=tls_info,
        cert=cert,
    )
