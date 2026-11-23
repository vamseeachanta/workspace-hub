"""Exercise strict capacity and budget inequalities without requiring bc.

Limit source: scripts/coordination/routing/lib/provider_filter.sh at the base
revision, capacity checks and simplified budget check. Fixture values are
synthetic: below/at/above each limit differ by one tenth. Independently,
limit - (limit - 0.1) = 0.1 > 0, limit - limit = 0, and
limit - (limit + 0.1) = -0.1 < 0. Only the first case permits inclusion.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


PROVIDER_FILTER = (
    Path(__file__).resolve().parents[2]
    / "scripts/coordination/routing/lib/provider_filter.sh"
)
PROVIDERS = ("codex", "gemini", "claude")

# Source: the six capacity comparisons in provider_filter.sh, in provider order.
CAPACITY_LIMITS = (
    ("codex", "requests_percent", 85),
    ("codex", "tokens_percent", 90),
    ("gemini", "requests_percent", 80),
    ("gemini", "tokens_percent", 85),
    ("claude", "requests_percent", 80),
    ("claude", "tokens_percent", 80),
)
# Independent hand calculation above: strict inequality excludes equality.
BOUNDARIES = ((-0.1, True), (0, False), (0.1, False))


@pytest.fixture
def filter_fixture(tmp_path):
    tools = tmp_path / "bin"
    tools.mkdir()
    # cat is also required by the existing JSON-reading code. There is no
    # resolver interpreter or provider executable in this isolated PATH.
    for command in ("bash", "awk", "jq", "cat"):
        executable = shutil.which(command)
        assert executable is not None, f"required fixture tool: {command}"
        (tools / command).symlink_to(executable)
    assert shutil.which("bc", path=str(tools)) is None

    config = tmp_path / "config"
    config.mkdir()
    # Synthetic available baseline: zero capacity usage is below every cited
    # limit, and budget 2.5 - cost 0.5 = 2.0 > 0 for each provider.
    usage = {
        provider: {
            "requests_percent": 0,
            "tokens_percent": 0,
            "cost_today": 0.5,
            "daily_budget": 2.5,
        }
        for provider in PROVIDERS
    }

    def run(raw_usage=None):
        for provider, values in usage.items():
            (config / f"{provider}_usage.json").write_text(
                (raw_usage or {}).get(provider, json.dumps(values)),
                encoding="utf-8", newline="\n"
            )
        result = subprocess.run(
            [
                str(tools / "bash"), "--noprofile", "--norc", "-c",
                '_resolver() { echo "unexpected resolver call" >&2; return 1; }\n'
                'source "$1"\nfilter_available_providers',
                "filter-test", str(PROVIDER_FILTER),
            ],
            env={"PATH": str(tools), "CONFIG_DIR": str(config)},
            capture_output=True,
            text=True,
            encoding="utf-8",
            # Synthetic execution bound; no provider command may be run.
            timeout=10,
        )
        assert result.returncode == 0, result.stderr
        assert result.stderr == ""
        return json.loads(result.stdout)

    return usage, run


@pytest.mark.parametrize("provider,field,limit", CAPACITY_LIMITS)
@pytest.mark.parametrize("offset,included", BOUNDARIES)
def test_capacity_strict_boundary_without_bc(
    filter_fixture, provider, field, limit, offset, included
):
    usage, run = filter_fixture
    usage[provider][field] = limit + offset
    expected = [name for name in PROVIDERS if name != provider or included]
    assert run() == expected


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("offset,included", BOUNDARIES)
def test_budget_strict_boundary_without_bc(
    filter_fixture, provider, offset, included
):
    usage, run = filter_fixture
    # Independent inequalities for the synthetic budget: 2.4 < 2.5,
    # 2.5 == 2.5, and 2.6 > 2.5. Capacity remains available throughout.
    usage[provider]["cost_today"] = usage[provider]["daily_budget"] + offset
    expected = [name for name in PROVIDERS if name != provider or included]
    assert run() == expected


def test_empty_availability_without_bc(filter_fixture):
    usage, run = filter_fixture
    for provider, field, limit in CAPACITY_LIMITS:
        usage[provider][field] = limit
    # Equality leaves no remaining capacity for any provider.
    assert run() == []


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize(
    "field", ("requests_percent", "tokens_percent", "cost_today", "daily_budget")
)
@pytest.mark.parametrize(
    "invalid", ("missing", None, "", "invalid", "0.5", True, [], {}, -1,
                float("inf"), float("nan")),
)
def test_invalid_quota_excludes_only_affected_provider(
    filter_fixture, provider, field, invalid
):
    usage, run = filter_fixture
    if invalid == "missing":
        del usage[provider][field]
    else:
        usage[provider][field] = invalid
    assert run() == [name for name in PROVIDERS if name != provider]


@pytest.mark.parametrize("provider", PROVIDERS)
def test_multiple_quota_documents_fail_closed(filter_fixture, provider):
    usage, run = filter_fixture
    invalid = dict(usage[provider])
    del invalid["daily_budget"]
    records = json.dumps(invalid) + "\n" + json.dumps(usage[provider])
    assert run({provider: records}) == [name for name in PROVIDERS if name != provider]
