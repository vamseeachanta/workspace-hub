"""Tests for workspace-hub-only model-release readiness contract (#2408).

Scope: workspace-hub control-plane only. Tier-1 ecosystem inventory and
provider-entrypoint-shape normalization are explicitly out of scope for #2408.

Verifies:
- Contract/playbook/package cover all required dimensions.
- Canonical discoverability anchors are wired from AGENTS.md and
  docs/standards/CONTROL_PLANE_CONTRACT.md.
- New docs do not contradict the control-plane adapter topology.
- Audited thin adapters remain within the line limit sourced from
  .claude/rules/coding-style.md (not hardcoded).
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PACKAGE = REPO_ROOT / "docs" / "reports" / "2026-04-20-issue-2408-workspace-hub-readiness-package.md"
CONTRACT = REPO_ROOT / "docs" / "standards" / "MODEL_RELEASE_READINESS_CONTRACT.md"
PLAYBOOK = REPO_ROOT / "docs" / "standards" / "MODEL_RELEASE_UPGRADE_PLAYBOOK.md"
PLAN = REPO_ROOT / "docs" / "plans" / "2026-04-20-issue-2408-workspace-hub-model-release-readiness-contract-and-upgrade-playbook.md"
AGENTS = REPO_ROOT / "AGENTS.md"
CONTROL_PLANE = REPO_ROOT / "docs" / "standards" / "CONTROL_PLANE_CONTRACT.md"
CODING_STYLE = REPO_ROOT / ".claude" / "rules" / "coding-style.md"
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
GEMINI_MD = REPO_ROOT / "GEMINI.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# Package ----------------------------------------------------------------------

def test_package_contains_workspace_hub_gap_summary_section():
    text = _read(PACKAGE)
    assert re.search(
        r"^#{1,6}\s+Workspace-Hub Gap Summary\b",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    ), "readiness package must contain a named 'Workspace-Hub Gap Summary' section"


def test_package_states_tier1_and_normalization_out_of_scope():
    text = _read(PACKAGE).lower()
    assert "out of scope" in text, "package must name an explicit out-of-scope section"
    assert "tier-1" in text or "tier 1" in text, (
        "package must explicitly defer tier-1 ecosystem inventory"
    )
    assert "provider-entrypoint" in text or "provider entrypoint" in text, (
        "package must explicitly defer provider-entrypoint-shape normalization"
    )


def test_package_validation_evidence_avoids_stale_fixed_test_counts():
    text = _read(PACKAGE)
    assert not re.search(r"\b\d+\s+tests?,\s+all passing\b", text), (
        "durable package validation evidence must not embed a fixed test count; "
        "the closeout comment carries current run evidence"
    )


def test_plan_artifact_matches_approved_strict_canonical_scope():
    text = _read(PLAN)
    assert "> **Status:** plan-approved" in text, (
        "approved implementation plan must not retain stale draft status"
    )
    assert "PENDING" not in text, (
        "approved implementation plan must summarize review outcome rather than "
        "retain stale pending review placeholders"
    )
    assert "live root provider entry surfaces (`CLAUDE.md`, `GEMINI.md`) are updated" not in text, (
        "plan must not require provider-entrypoint normalization in #2408; "
        "those surfaces are audit-only for the strict canonical-doc strategy"
    )


# Contract ---------------------------------------------------------------------

def test_contract_declares_read_budget_for_standards_docs():
    for path in (CONTRACT, PLAYBOOK):
        head = "\n".join(_read(path).splitlines()[:8])
        assert re.search(r"read budget", head, flags=re.IGNORECASE), (
            f"{path.name} must declare a read-budget note in its opening block"
        )


def test_contract_covers_context_budget_and_truncation_safety():
    text = _read(CONTRACT)
    assert re.search(r"Context[- ]Budget", text, flags=re.IGNORECASE), (
        "contract must explicitly name 'Context-Budget'"
    )
    assert re.search(r"Truncation[- ]Safe", text, flags=re.IGNORECASE), (
        "contract must explicitly name 'Truncation-Safe' artifact design"
    )


def test_contract_covers_machine_readable_vs_prose_guidance():
    text = _read(CONTRACT)
    assert re.search(r"Machine[- ]Readable", text, flags=re.IGNORECASE), (
        "contract must explicitly name 'Machine-Readable' guidance"
    )
    assert re.search(r"\bProse\b", text), (
        "contract must explicitly contrast prose-only guidance vs machine-readable"
    )


def test_contract_covers_prompt_pack_portability():
    combined = _read(CONTRACT) + "\n" + _read(PLAYBOOK)
    assert re.search(r"Prompt[- ]Pack Portability", combined, flags=re.IGNORECASE), (
        "contract or playbook must name 'Prompt-Pack Portability' dimension"
    )


def test_contract_scope_is_workspace_hub_only():
    text = _read(CONTRACT).lower()
    assert "workspace-hub" in text, "contract must self-identify as workspace-hub scope"
    assert "out of scope" in text, "contract must state an explicit out-of-scope boundary"


# Playbook ---------------------------------------------------------------------

def test_upgrade_playbook_separates_provider_vs_repo_drift():
    text = _read(PLAYBOOK).lower()
    assert "provider-owned" in text, "playbook must name 'provider-owned' drift branch"
    assert "repo-owned" in text, "playbook must name 'repo-owned' drift branch"


def test_upgrade_playbook_references_required_operational_paths():
    text = _read(PLAYBOOK)
    assert "scripts/_core/sync-agent-configs.sh" in text, (
        "playbook must reference the config-sync entrypoint"
    )
    assert "config/agents/" in text, (
        "playbook must reference the config/agents/ surface"
    )


def test_upgrade_playbook_steps_are_actionable():
    text = _read(PLAYBOOK)
    assert re.search(r"^\s*1\.\s+\S", text, flags=re.MULTILINE), (
        "playbook must present an enumerated, actionable step sequence"
    )


# Canonical anchor strategy ---------------------------------------------------

def test_canonical_anchor_strategy_matches_control_plane_contract():
    agents_text = _read(AGENTS)
    control_plane_text = _read(CONTROL_PLANE)
    assert "docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md" in agents_text, (
        "AGENTS.md must point to the readiness contract as a canonical anchor"
    )
    assert "MODEL_RELEASE_READINESS_CONTRACT.md" in control_plane_text, (
        "CONTROL_PLANE_CONTRACT.md must cross-reference the readiness contract"
    )
    assert "MODEL_RELEASE_UPGRADE_PLAYBOOK.md" in control_plane_text, (
        "CONTROL_PLANE_CONTRACT.md must cross-reference the upgrade playbook"
    )


def test_non_contradiction_with_control_plane_contract_uses_concrete_assertions():
    contract_text = _read(CONTRACT)
    playbook_text = _read(PLAYBOOK)
    for canonical_path in ("AGENTS.md", ".claude/", ".codex/", ".gemini/"):
        assert (canonical_path in contract_text) or (canonical_path in playbook_text), (
            f"readiness docs must reference canonical adapter path '{canonical_path}' "
            "as defined in CONTROL_PLANE_CONTRACT.md"
        )
    forbidden_inventions = (".anthropic/", ".openai/", ".google/", ".llm/")
    for bad in forbidden_inventions:
        assert bad not in contract_text, (
            f"contract invents adapter path '{bad}' — contradicts control-plane contract"
        )
        assert bad not in playbook_text, (
            f"playbook invents adapter path '{bad}' — contradicts control-plane contract"
        )


# Audited thin-adapter line-limit compliance ---------------------------------

def _line_limit_from_policy() -> int:
    """Source the limit from .claude/rules/coding-style.md so the test tracks policy."""
    text = _read(CODING_STYLE)
    m = re.search(
        r"CLAUDE\.md,\s*MEMORY\.md,\s*AGENTS\.md,\s*GEMINI\.md must not exceed\s+(\d+)\s+lines",
        text,
    )
    assert m, "coding-style.md must define the agent-harness line limit"
    return int(m.group(1))


def test_audited_thin_adapters_remain_within_line_limits():
    limit = _line_limit_from_policy()
    for path in (CLAUDE_MD, GEMINI_MD, AGENTS):
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) <= limit, (
            f"{path.name} has {len(lines)} lines (limit {limit} from "
            ".claude/rules/coding-style.md). Migrate excess to a skill or doc."
        )


def test_playbook_does_not_overclaim_codex_tree_line_limit():
    text = _read(PLAYBOOK)
    assert "not to the entire `.codex/**` tree" in text, (
        "playbook must explicitly avoid claiming the 20-line policy applies to the full .codex tree"
    )


def test_contract_does_not_overclaim_codex_tree_line_limit():
    text = _read(CONTRACT)
    assert "`.codex/` tree" in text and "20-line harness-file cap" in text, (
        "contract must explicitly distinguish .codex tree topology from the harness-file line cap"
    )
