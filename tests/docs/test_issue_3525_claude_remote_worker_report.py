from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT = REPO_ROOT / "docs/reports/2026-07-14-issue-3525-claude-remote-worker-discovery.html"
OFFICIAL_HOSTS = {
    "anthropic.com",
    "claude.ai",
    "claude.com",
    "code.claude.com",
    "docs.anthropic.com",
    "platform.claude.com",
    "support.claude.com",
    "www.anthropic.com",
    "www.claude.com",
}
REQUIRED_SECTIONS = {
    "current-state",
    "evidence",
    "gaps-risks",
    "ranked-options",
    "decision",
    "implementation-burden",
    "local-observations",
}
REJECTED_PRACTICES = {
    "password-sharing",
    "session-cookie-sharing",
    "raw-oauth-sharing",
    "personal-api-key-sharing",
}
FALLBACK_CONTROLS = {
    "dedicated-os-account",
    "isolated-auth-config",
    "least-privilege",
    "authenticated-pull-queue",
    "repo-action-allowlist",
    "audit-log",
    "concurrency-lock",
    "spend-rate-limit",
    "failure-quarantine",
    "wake-handling",
}
OFFICIAL_CLAIM_SOURCES = {
    "remote-control": "https://code.claude.com/docs/en/remote-control",
    "desktop-scheduled-tasks": "https://code.claude.com/docs/en/desktop-scheduled-tasks",
    "cowork-dispatch": "https://support.claude.com/en/articles/13947068-assign-tasks-from-anywhere-in-claude-cowork",
    "channels": "https://code.claude.com/docs/en/channels",
    "routines": "https://code.claude.com/docs/en/routines",
    "authentication": "https://code.claude.com/docs/en/authentication",
    "trusted-devices": "https://code.claude.com/docs/en/remote-control#trusted-devices",
    "workload-identity-federation": "https://platform.claude.com/docs/en/manage-claude/workload-identity-federation",
    "usage-cost-api": "https://platform.claude.com/docs/en/manage-claude/usage-cost-api",
    "consumer-terms": "https://www.anthropic.com/legal/consumer-terms",
    "commercial-terms": "https://www.anthropic.com/legal/commercial-terms",
}


def _soup() -> BeautifulSoup:
    return BeautifulSoup(REPORT.read_text(encoding="utf-8"), "html.parser")


def test_report_exists_and_has_required_decision_sections() -> None:
    assert REPORT.is_file()
    soup = _soup()
    assert REQUIRED_SECTIONS <= {node.get("id") for node in soup.find_all(id=True)}
    decision = soup.select_one("#decision [data-decision]")
    assert decision is not None
    assert decision["data-decision"] in {
        "use-existing-feature",
        "build-small-runner",
        "defer",
    }


def test_report_separates_evidence_classes_and_official_links() -> None:
    soup = _soup()
    rows = soup.select("#evidence [data-evidence-class]")
    assert {row["data-evidence-class"] for row in rows} == {
        "verified_official",
        "local_observation",
        "assumption",
        "unresolved",
    }
    for row in soup.select('[data-evidence-class="verified_official"]'):
        link = row.select_one('a[data-source-role="official"][href]')
        accessed = row.select_one("time[datetime]")
        assert link is not None and urlparse(link["href"]).scheme == "https"
        assert urlparse(link["href"]).hostname in OFFICIAL_HOSTS
        assert accessed is not None and accessed["datetime"] >= "2026-07-14"


def test_verified_claims_are_bound_to_reviewed_official_sources() -> None:
    rows = _soup().select('[data-evidence-class="verified_official"]')
    observed = {
        row["data-claim-id"]: row.select_one('a[data-source-role="official"]')["href"]
        for row in rows
    }
    assert observed == OFFICIAL_CLAIM_SOURCES


def test_product_and_account_matrices_cover_requested_boundaries() -> None:
    soup = _soup()
    products = {row["data-product"] for row in soup.select("[data-product]")}
    accounts = {row["data-account-context"] for row in soup.select("[data-account-context]")}
    assert {"desktop", "code", "web", "team", "enterprise", "api"} <= products
    assert {"same-account", "separate-individual", "team", "enterprise", "api"} <= accounts


def test_report_rejects_sharing_and_pins_fallback_controls() -> None:
    soup = _soup()
    rejected = {node["data-rejected-practice"] for node in soup.select("[data-rejected-practice]")}
    controls = {node["data-control"] for node in soup.select("[data-control]")}
    assert rejected == REJECTED_PRACTICES
    assert controls == FALLBACK_CONTROLS


def test_ranked_options_include_size_burden_and_confidence() -> None:
    rows = _soup().select("#ranked-options [data-rank]")
    assert len(rows) >= 3
    assert [int(row["data-rank"]) for row in rows] == list(range(1, len(rows) + 1))
    for row in rows:
        assert row.get("data-size")
        assert row.get("data-ops-burden")
        assert row.get("data-confidence") in {"high", "medium", "low"}


def test_tables_have_accessible_captions_and_scoped_headers() -> None:
    tables = _soup().select("table")
    assert tables
    for table in tables:
        caption = table.select_one("caption")
        assert caption is not None and caption.get_text(strip=True)
        headers = table.select("thead th")
        assert headers and all(header.get("scope") == "col" for header in headers)


def test_local_observations_are_host_bound_and_scrubbed() -> None:
    section = _soup().select_one("#local-observations")
    assert section is not None
    assert section.get("data-lane-status") in {"completed", "blocked"}
    hostname_row = section.select_one('[data-command="hostname"]')
    assert hostname_row is not None
    assert "identifier is intentionally omitted" in hostname_row.parent.get_text(" ", strip=True)
    if section["data-lane-status"] == "completed":
        assert section.get("data-host-match") == "registry-canonical-or-alias"
        commands = {node["data-command"] for node in section.select("[data-command]")}
        assert commands == {"hostname", "claude-version", "claude-help", "desktop-inventory"}
