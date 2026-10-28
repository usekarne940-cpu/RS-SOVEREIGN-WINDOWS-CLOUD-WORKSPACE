"""Live network integration tests against the real pixeldrain endpoint.

Marked `network`: excluded from default local runs (`-m "not network"`).
These tests hit the REAL endpoint and assert REAL observed behavior
(evidence captured 2026-10-28T18:55Z): file available, 2,555,783,617 bytes,
genuine 7z signature, range requests honored. If the upstream file changes
or is removed, these tests fail honestly — that is their purpose.

The connectivity check runs in a killed-on-timeout subprocess (a bare
socket call can block unbounded in DNS resolution — observed in this
sandbox), so collection can never hang.
"""
import subprocess
import sys

import pytest

import xlite_inspector as xi

ENDPOINT = "https://pixeldrain.com/api/file/ZdPxkVmH"


def network_available() -> bool:
    """Bounded connectivity check: a socket connect in a subprocess that is
    hard-killed after 8 s regardless of where it blocks."""
    code = ("import socket; "
            "socket.create_connection(('pixeldrain.com', 443), timeout=4).close()")
    try:
        proc = subprocess.run([sys.executable, "-c", code],
                              capture_output=True, timeout=8)
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        return False


pytestmark = [
    pytest.mark.network,
    pytest.mark.integration,
]


def _require_network():
    if not network_available():
        pytest.skip("no network access to pixeldrain (bounded check)")


def test_live_metadata():
    _require_network()
    meta = xi.get_metadata(ENDPOINT, timeout=60)
    assert meta["availability"] == "available"
    assert meta["name"] == "[Windows X-Lite] Optimum 11 26H1 Pro v2.7z"
    assert isinstance(meta["size"], int)
    assert meta["size"] > 1_000_000_000  # a multi-GB Windows image archive
    assert meta["size"] == 2_555_783_617  # live-verified constant


def test_live_probe_magic_bytes():
    _require_network()
    result = xi.probe(ENDPOINT, nbytes=4096, timeout=60)
    assert result["http_status"] in (200, 206)
    assert result["bytes_received"] == 4096
    assert result["is_7z_archive"] is True
    assert result["first_bytes_hex"].startswith("377abcaf271c")
    assert result["total_size_bytes"] == 2_555_783_617
