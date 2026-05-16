"""Tests that each AI-provider bootstrap surface receives the required workflow
constraints (gate keywords + canonical-contract pointer + no broken paths).

Closes #2446 (Hermes onboarding gate gap) criterion 3 ("test added") and
criterion 4 (other-adapter spot-check).

Surfaces under test:
- Repo-root adapter files: CLAUDE.md, GEMINI.md, AGENTS.md, .codex/CODEX.md
- Built runtime artifacts: config/agents/<provider>/SOUL.runtime.md and
  config/agents/codex/AGENTS.runtime.md

The test does NOT validate Hermes runtime symlinks (those are install-time,
not committed) — only the canonical sources and built runtime artifacts.

Refs: workspace-hub#2719 Phase 7, workspace-hub#2446.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ─── Required-content matchers ──────────────────────────────────────────────


# Gate keywords matched as regex stems so APPROVES / approved / approval all count.
# #2446 acceptance is "gate references present", not exact-word match.
GATE_KEYWORD_PATTERNS = {
    "plan": re.compile(r"\bplan", re.IGNORECASE),
    "approval": re.compile(r"\bapprov", re.IGNORECASE),
    "TDD": re.compile(r"\bTDD\b", re.IGNORECASE),
}

CANONICAL_POINTER_PATTERNS = [
    # Adapter files must point at AGENTS.md as the canonical workflow contract.
    re.compile(r"\bAGENTS\.md\b", re.IGNORECASE),
]

BROKEN_CODEX_PATH = re.compile(r"Read `\.Codex/memory/`")


# ─── Cases under test ───────────────────────────────────────────────────────


REPO_ROOT_ADAPTERS = {
    "claude": REPO_ROOT / "CLAUDE.md",
    "gemini": REPO_ROOT / "GEMINI.md",
    "codex": REPO_ROOT / ".codex" / "CODEX.md",
}

CANONICAL_CONTRACT = REPO_ROOT / "AGENTS.md"

PROVIDER_RUNTIME_ARTIFACTS = {
    "hermes": REPO_ROOT / "config" / "agents" / "hermes" / "SOUL.runtime.md",
    "claude": REPO_ROOT / "config" / "agents" / "claude" / "SOUL.runtime.md",
    "codex_soul": REPO_ROOT / "config" / "agents" / "codex" / "SOUL.runtime.md",
    "codex_agents": REPO_ROOT / "config" / "agents" / "codex" / "AGENTS.runtime.md",
    "gemini": REPO_ROOT / "config" / "agents" / "gemini" / "SOUL.runtime.md",
}

SHARED_SOUL = REPO_ROOT / "config" / "agents" / "SHARED_SOUL.md"


# ─── Tests: canonical contract ──────────────────────────────────────────────


def test_canonical_agents_md_exists():
    """AGENTS.md (repo root) must exist as the canonical workflow contract."""
    assert CANONICAL_CONTRACT.exists(), f"{CANONICAL_CONTRACT} missing"


def test_canonical_agents_md_contains_gate_keywords():
    """AGENTS.md must list the planning gate order with all required keywords."""
    body = CANONICAL_CONTRACT.read_text(encoding="utf-8")
    for kw, pattern in GATE_KEYWORD_PATTERNS.items():
        assert pattern.search(body), (
            f"AGENTS.md missing gate keyword: {kw!r}"
        )


def test_canonical_agents_md_references_shared_soul():
    """AGENTS.md must reference SHARED_SOUL.md as the cross-provider identity baseline (#2719)."""
    body = CANONICAL_CONTRACT.read_text(encoding="utf-8")
    assert "SHARED_SOUL.md" in body, (
        "AGENTS.md must point at config/agents/SHARED_SOUL.md per #2719 Phase 6"
    )


# ─── Tests: repo-root adapter files ─────────────────────────────────────────


@pytest.mark.parametrize("provider", sorted(REPO_ROOT_ADAPTERS.keys()))
def test_repo_root_adapter_exists(provider: str):
    """Each provider's repo-root adapter file must exist."""
    path = REPO_ROOT_ADAPTERS[provider]
    assert path.exists(), f"{path} missing"


@pytest.mark.parametrize("provider", sorted(REPO_ROOT_ADAPTERS.keys()))
def test_repo_root_adapter_points_at_canonical_contract(provider: str):
    """Each repo-root adapter must reference AGENTS.md as canonical."""
    body = REPO_ROOT_ADAPTERS[provider].read_text(encoding="utf-8")
    for pattern in CANONICAL_POINTER_PATTERNS:
        assert pattern.search(body), (
            f"{provider} adapter file must reference AGENTS.md"
        )


@pytest.mark.parametrize("provider", sorted(REPO_ROOT_ADAPTERS.keys()))
def test_repo_root_adapter_points_at_soul_runtime(provider: str):
    """Each repo-root adapter must reference its SOUL.runtime.md (or AGENTS.runtime.md for Codex)."""
    body = REPO_ROOT_ADAPTERS[provider].read_text(encoding="utf-8")
    if provider == "codex":
        target = "AGENTS.runtime.md"
    else:
        target = "SOUL.runtime.md"
    assert target in body, (
        f"{provider} adapter file must reference {target} per #2719 Phase 6"
    )


# ─── Tests: SHARED_SOUL.md ──────────────────────────────────────────────────


def test_shared_soul_exists():
    """SHARED_SOUL.md must exist as the cross-provider identity canonical."""
    assert SHARED_SOUL.exists(), f"{SHARED_SOUL} missing"


def test_shared_soul_contains_gate_keywords():
    """SHARED_SOUL.md must carry all gate keywords."""
    body = SHARED_SOUL.read_text(encoding="utf-8")
    for kw, pattern in GATE_KEYWORD_PATTERNS.items():
        assert pattern.search(body), (
            f"SHARED_SOUL.md missing gate keyword: {kw!r}"
        )


def test_shared_soul_contains_never_self_approve_rule():
    """SHARED_SOUL.md must carry the never-self-approve must-fire rule."""
    body = SHARED_SOUL.read_text(encoding="utf-8")
    assert re.search(r"self-(label|approve)", body, re.IGNORECASE), (
        "SHARED_SOUL.md must enforce never-self-approve rule (feedback_never_offer_to_self_label_plan_approved)"
    )


# ─── Tests: built runtime artifacts ─────────────────────────────────────────


@pytest.mark.parametrize("artifact", sorted(PROVIDER_RUNTIME_ARTIFACTS.keys()))
def test_runtime_artifact_exists(artifact: str):
    """Each built runtime artifact must exist (committed by build-soul-runtime.sh)."""
    path = PROVIDER_RUNTIME_ARTIFACTS[artifact]
    assert path.exists(), f"{path} missing — run scripts/agents/build-soul-runtime.sh"


@pytest.mark.parametrize("artifact", sorted(PROVIDER_RUNTIME_ARTIFACTS.keys()))
def test_runtime_artifact_contains_gate_keywords(artifact: str):
    """Each runtime artifact must contain all gate keywords (inherited from SHARED_SOUL)."""
    body = PROVIDER_RUNTIME_ARTIFACTS[artifact].read_text(encoding="utf-8")
    for kw, pattern in GATE_KEYWORD_PATTERNS.items():
        assert pattern.search(body), (
            f"{artifact} runtime missing gate keyword: {kw!r}"
        )


@pytest.mark.parametrize("artifact", sorted(PROVIDER_RUNTIME_ARTIFACTS.keys()))
def test_runtime_artifact_references_canonical_contract(artifact: str):
    """Each runtime artifact must reference AGENTS.md as canonical."""
    body = PROVIDER_RUNTIME_ARTIFACTS[artifact].read_text(encoding="utf-8")
    assert "AGENTS.md" in body, (
        f"{artifact} runtime must reference AGENTS.md as canonical contract"
    )


@pytest.mark.parametrize("artifact", sorted(PROVIDER_RUNTIME_ARTIFACTS.keys()))
def test_runtime_artifact_carries_build_marker(artifact: str):
    """Each runtime artifact must carry the BUILT marker so editors don't hand-edit."""
    body = PROVIDER_RUNTIME_ARTIFACTS[artifact].read_text(encoding="utf-8")
    assert "BUILT by scripts/agents/build-soul-runtime.sh" in body, (
        f"{artifact} runtime missing BUILT marker — was it committed without running build-soul-runtime.sh?"
    )


# ─── Tests: no broken paths anywhere ────────────────────────────────────────


@pytest.mark.parametrize("artifact", sorted(PROVIDER_RUNTIME_ARTIFACTS.keys()))
def test_runtime_artifact_no_broken_codex_path_as_instruction(artifact: str):
    """No runtime artifact may instruct the agent to read .Codex/memory/ (the broken Phase 1 bug).

    The forensic description in codex/SOUL.delta.md is allowed (it documents the
    historical bug); only the operational instruction `Read \\`.Codex/memory/\\``
    is forbidden.
    """
    body = PROVIDER_RUNTIME_ARTIFACTS[artifact].read_text(encoding="utf-8")
    assert not BROKEN_CODEX_PATH.search(body), (
        f"{artifact} runtime contains the broken `Read .Codex/memory/` instruction — "
        f"this regressed the Phase 1 bug fix from #2719"
    )
