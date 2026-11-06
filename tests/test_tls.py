from pathlib import Path

import pytest

from pqready.models import HybridSupport
from pqready.scanner import tls

# Brief s_client outputs recorded on the Docker lab (no network in these tests).
FIXTURES = Path(__file__).parent / "fixtures" / "tls"

HYBRID = ("-groups", tls.HYBRID_GROUP)
CONTROL = ("-groups", tls.CLASSICAL_GROUP)


def read_fixture(name: str) -> str:
    return (FIXTURES / f"{name}.txt").read_text(encoding="utf-8")


def fake_s_client(monkeypatch, outputs: dict[tuple[str, ...], str]) -> None:
    """Replace run_s_client: probe args (without -brief) -> recorded output."""

    def run(host: str, port: int, args: list[str], timeout: float) -> str:
        return outputs[tuple(arg for arg in args if arg != "-brief")]

    monkeypatch.setattr(tls, "run_s_client", run)


@pytest.mark.parametrize(
    ("name", "established"),
    [
        ("hybride_groups_hybrid", True),
        ("faible_groups_hybrid", True),
        ("classique_groups_hybrid", False),
        ("dns_error", False),
    ],
)
def test_established(name, established):
    assert tls._established(read_fixture(name)) is established


@pytest.mark.parametrize(
    ("name", "group"),
    [
        ("hybride_groups_hybrid", "X25519MLKEM768"),
        ("classique_default", "X25519"),
        ("faible_groups_hybrid", None),
    ],
)
def test_negotiated_group(name, group):
    assert tls._negotiated_group(read_fixture(name)) == group


def test_negotiated_group_nist_curve():
    assert tls._negotiated_group("Peer Temp Key: ECDH, prime256v1, 256 bits\n") == "prime256v1"


@pytest.mark.parametrize(
    ("name", "version"),
    [
        ("hybride_groups_hybrid", "TLSv1.3"),
        ("faible_tls1", "TLSv1"),
        ("classique_tls1", None),
    ],
)
def test_protocol_version(name, version):
    assert tls._protocol_version(read_fixture(name)) == version


@pytest.mark.parametrize(
    ("name", "alert"),
    [
        ("classique_groups_hybrid", 40),
        ("classique_tls1", 70),
        ("hybride_groups_hybrid", None),
    ],
)
def test_alert(name, alert):
    assert tls._alert(read_fixture(name)) == alert


def test_client_config_error():
    assert tls._client_config_error(read_fixture("no_protocols"))
    assert not tls._client_config_error(read_fixture("classique_tls1"))


@pytest.mark.parametrize(
    ("name", "message"),
    [
        ("dns_error", "system lib: Name or service not known"),
        ("no_protocols", "no protocols available"),
        ("", "no output"),
    ],
)
def test_error_message(name, message):
    output = read_fixture(name) if name else ""
    assert tls._error_message(output) == message


def test_hybrid_support_yes(monkeypatch):
    fake_s_client(monkeypatch, {HYBRID: read_fixture("hybride_groups_hybrid")})
    assert tls._hybrid_support("hybride", 443, 5) is HybridSupport.YES


def test_hybrid_support_refused_then_control_ok(monkeypatch):
    fake_s_client(
        monkeypatch,
        {
            HYBRID: read_fixture("classique_groups_hybrid"),
            CONTROL: read_fixture("classique_default"),
        },
    )
    assert tls._hybrid_support("classique", 443, 5) is HybridSupport.NO


def test_hybrid_support_established_without_group_is_no(monkeypatch):
    # ADR-001 central rule: CONNECTION ESTABLISHED alone is not proof of hybrid support.
    fake_s_client(monkeypatch, {HYBRID: read_fixture("faible_groups_hybrid")})
    assert tls._hybrid_support("faible", 443, 5) is HybridSupport.NO


def test_hybrid_support_both_refused_is_unknown(monkeypatch):
    refused = read_fixture("classique_groups_hybrid")
    fake_s_client(monkeypatch, {HYBRID: refused, CONTROL: refused})
    assert tls._hybrid_support("x", 443, 5) is HybridSupport.UNKNOWN


def test_probe_raises_on_client_config_error(monkeypatch):
    fake_s_client(monkeypatch, {("-tls1",): read_fixture("no_protocols")})
    with pytest.raises(tls.ClientConfigError, match="no protocols available"):
        tls._probe("faible", 443, ["-tls1"], 5)


def test_scan_tls_unreachable_raises(monkeypatch):
    fake_s_client(monkeypatch, {(): read_fixture("dns_error")})
    with pytest.raises(ConnectionError, match="Name or service not known"):
        tls.scan_tls("nexistepas", 443, 5)
