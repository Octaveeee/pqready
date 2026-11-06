from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class HybridSupport(StrEnum):
    """Whether the endpoint accepts a hybrid PQC key exchange (see ADR-001)."""

    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class Status(StrEnum):
    """Outcome of scanning one target."""

    OK = "ok"
    ERROR = "error"


@dataclass(frozen=True)
class Target:
    """A TLS endpoint to scan, read from the input CSV."""

    host: str
    port: int
    label: str
    sensitivity: int
    confidentiality_years: int

    def __post_init__(self) -> None:
        if self.sensitivity not in (1, 2, 3):
            raise ValueError(f"sensitivity must be 1, 2 or 3, got {self.sensitivity}")
        if not 1 <= self.port <= 65535:
            raise ValueError(f"port must be between 1 and 65535, got {self.port}")
        if self.confidentiality_years < 0:
            raise ValueError(
                f"confidentiality_years must be >= 0, got {self.confidentiality_years}"
            )


@dataclass(frozen=True)
class TlsInfo:
    """What the TLS handshakes revealed about an endpoint."""

    pq_hybrid_supported: HybridSupport
    rsa_key_exchange: bool
    # None when no group is used (RSA key exchange, see the "faible" lab server).
    negotiated_group: str | None = None
    versions: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CertInfo:
    """Leaf certificate summary."""

    key_type: str
    key_size: int
    signature_algorithm: str
    not_after: datetime
    issuer: str

    def __post_init__(self) -> None:
        if self.not_after.tzinfo is None:
            raise ValueError("not_after must be timezone-aware (UTC)")


@dataclass(frozen=True)
class ScanResult:
    """Raw scan result for one target, before classification."""

    target: Target
    scanned_at: datetime
    status: Status
    error: str | None = None
    tls: TlsInfo | None = None
    cert: CertInfo | None = None

    def __post_init__(self) -> None:
        if self.scanned_at.tzinfo is None:
            raise ValueError("scanned_at must be timezone-aware (UTC)")
        if self.status is Status.ERROR and self.error is None:
            raise ValueError("an ERROR result must carry an error message")
