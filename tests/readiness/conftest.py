"""Fixtures for the readiness suite."""

import socket
from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="module")
def primary_dispatch_hostname():
    root = Path(__file__).resolve().parents[2]
    registry = root / "config" / "workstations" / "registry.yaml"
    machines = yaml.safe_load(registry.read_text(encoding="utf-8"))["machines"]
    hostname, = (m["hostname"] for m in machines.values() if m["role"] == "primary-dev")
    return hostname


@pytest.fixture
def local_dispatch_identity(monkeypatch, primary_dispatch_hostname):
    monkeypatch.setattr(socket, "gethostname", lambda: primary_dispatch_hostname)
    monkeypatch.setattr(socket, "getfqdn", lambda: primary_dispatch_hostname)
