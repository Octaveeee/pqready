"""End-to-end scans of the Docker lab.

Run inside the tools image, on the lab network (see README); skipped elsewhere.
"""

import json
import socket

import pytest
from typer.testing import CliRunner

from pqready.cli import app
from pqready.models import HybridSupport, Status, Target
from pqready.scanner.scan import scan_target


def _lab_running() -> bool:
    try:
        socket.gethostbyname("hybride")
    except OSError:
        return False
    return True


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not _lab_running(), reason="Docker lab not reachable"),
]

TIMEOUT = 5


@pytest.mark.parametrize(
    ("host", "hybrid", "rsa_kx", "group", "versions", "key"),
    [
        ("hybride", HybridSupport.YES, False, "X25519MLKEM768", ["TLSv1.3"], ("EC", 256)),
        ("classique", HybridSupport.NO, False, "X25519", ["TLSv1.2", "TLSv1.3"], ("EC", 256)),
        ("faible", HybridSupport.NO, True, None, ["TLSv1", "TLSv1.1", "TLSv1.2"], ("RSA", 1024)),
    ],
)
def test_scan_lab_server(host, hybrid, rsa_kx, group, versions, key):
    result = scan_target(Target(host, 443, host, 1, 0), TIMEOUT)

    assert result.status is Status.OK
    assert result.tls.pq_hybrid_supported is hybrid
    assert result.tls.rsa_key_exchange is rsa_kx
    assert result.tls.negotiated_group == group
    assert result.tls.versions == versions
    assert (result.cert.key_type, result.cert.key_size) == key
    assert result.cert.issuer == f"CN={host}"


def test_scan_unknown_host_is_error():
    result = scan_target(Target("nexistepas", 443, "unknown", 1, 0), TIMEOUT)

    assert result.status is Status.ERROR
    assert "Name or service not known" in result.error


def test_scan_closed_port_is_error():
    result = scan_target(Target("hybride", 444, "closed port", 1, 0), TIMEOUT)

    assert result.status is Status.ERROR
    assert "Connection refused" in result.error


def test_cli_scan_writes_json(tmp_path):
    targets = tmp_path / "targets.csv"
    targets.write_text(
        "host,port,label,sensitivity,confidentiality_years\n"
        "hybride,443,lab,3,10\n"
        "nexistepas,443,unknown,1,0\n",
        encoding="utf-8",
    )
    output = tmp_path / "results.json"

    run = CliRunner().invoke(app, ["scan", str(targets), "-o", str(output), "--delay", "0"])

    assert run.exit_code == 0, run.output
    results = json.loads(output.read_text(encoding="utf-8"))
    assert [r["status"] for r in results] == ["ok", "error"]
    assert results[0]["tls"]["pq_hybrid_supported"] == "yes"
