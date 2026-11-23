from __future__ import annotations

import socket
from pathlib import Path

import pytest


def test_dev_secondary_ground_truth_captured_before_registry_mutation():
    hostname = socket.gethostname().split(".")[0]
    if hostname != "ace-linux-2":
        pytest.skip("dev-secondary ground-truth probe only runs on ace-linux-2")
    expected = Path("/mnt/local-analysis/workspace-hub")
    assert (expected / ".git").exists(), f"expected workspace-hub checkout at {expected}"
