from __future__ import annotations

import importlib.util
import json
from itertools import permutations, product
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts" / "repositories" / "work_surface_inventory.py"
FIXTURES = Path(__file__).parent / "fixtures" / "work_surface_inventory"


def _load_module():
    spec = importlib.util.spec_from_file_location("work_surface_inventory", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _surface(tmp_path: Path) -> Path:
    alpha = tmp_path / "alpha"
    for path in (alpha / ".git", alpha / ".claude", alpha / ".codex", alpha / ".gemini"):
        path.mkdir(parents=True)
    for path in (alpha / "AGENTS.md", alpha / ".claude" / "CLAUDE.md", alpha / ".mcp.json"):
        path.write_text("ok", encoding="utf-8")
    (tmp_path / "private-client-name" / ".git").mkdir(parents=True)
    return tmp_path


def test_fixture_golden_summary(tmp_path):
    inventory = _load_module().build_inventory(
        FIXTURES / "mission-map.yaml", FIXTURES / "workstations.yaml",
        _surface(tmp_path), "macbook-portable")
    expected = json.loads((FIXTURES / "expected.json").read_text())
    assert inventory == expected


def test_rejects_duplicate_names_and_bad_enums(tmp_path):
    module = _load_module()
    bad = tmp_path / "bad.yaml"
    bad.write_text("repos:\n- {repo: a, profile: code, sensitivity: public, mcp_required: false}\n- {repo: a, profile: other, sensitivity: secret, mcp_required: false}\n")
    with pytest.raises(ValueError):
        module.load_declared_repositories(bad)


def test_unclassified_is_incomplete(tmp_path):
    module = _load_module()
    declared = {"a": {"repo": "a", "profile": "code", "sensitivity": "unclassified", "mcp_required": False}}
    result = module.join_inventory(declared, set(), {}, 0)
    assert result["repositories"][0]["contract"]["complete"] is False


def test_unknown_repositories_are_aggregate_only(tmp_path):
    inventory = _load_module().build_inventory(
        FIXTURES / "mission-map.yaml", FIXTURES / "workstations.yaml",
        _surface(tmp_path), "macbook-portable")
    rendered = json.dumps(inventory)
    assert inventory["summary"]["unexpected_count"] == 1
    assert "private-client-name" not in rendered
    assert "token" not in rendered


def test_external_symlink_is_not_followed(tmp_path):
    outside = tmp_path.parent / "outside-secret"
    (outside / ".git").mkdir(parents=True)
    (tmp_path / "linked").symlink_to(outside, target_is_directory=True)
    observed, unexpected = _load_module().observe_work_surface(tmp_path, {"linked"})
    assert observed["linked"]["observed_local"] is False
    assert unexpected == 0


def test_gitfile_worktrees_count_as_repositories(tmp_path):
    declared_worktree = tmp_path / "declared"
    declared_worktree.mkdir()
    (declared_worktree / ".git").write_text("gitdir: ../real.git/worktrees/declared\n")
    unknown_worktree = tmp_path / "unknown"
    unknown_worktree.mkdir()
    (unknown_worktree / ".git").write_text("gitdir: ../real.git/worktrees/unknown\n")
    observed, unexpected = _load_module().observe_work_surface(tmp_path, {"declared"})
    assert observed["declared"]["observed_local"] is True
    assert unexpected == 1


def test_same_adapter_contract_for_knowledge_profile(tmp_path):
    module = _load_module()
    repo = tmp_path / "notes"
    (repo / ".git").mkdir(parents=True)
    (repo / "AGENTS.md").write_text("ok")
    observed, _ = module.observe_work_surface(tmp_path, {"notes"})
    declared = {"notes": {"repo": "notes", "profile": "knowledge", "sensitivity": "public", "mcp_required": False}}
    item = module.join_inventory(declared, set(), observed, 0)["repositories"][0]
    assert item["contract"]["complete"] is False
    assert item["contract"]["codex_dir"] is False


def test_distinguishes_configured_missing_declared_missing_and_non_git(tmp_path):
    module = _load_module()
    (tmp_path / "plain").mkdir()
    declared = {
        name: {"repo": name, "profile": "knowledge", "sensitivity": "public", "mcp_required": False}
        for name in ("configured", "absent", "plain")
    }
    observed, unexpected = module.observe_work_surface(tmp_path, set(declared))
    inventory = module.join_inventory(declared, {"configured"}, observed, unexpected)
    states = {item["name"]: item["state"] for item in inventory["repositories"]}
    assert states == {"absent": "declared-missing", "configured": "configured-missing", "plain": "non-git"}
    assert inventory["summary"]["missing"] == 2
    assert inventory["summary"]["non_git"] == 1


def test_summary_reports_configured_and_present_counts(tmp_path):
    inventory = _load_module().build_inventory(
        FIXTURES / "mission-map.yaml", FIXTURES / "workstations.yaml",
        _surface(tmp_path), "macbook-portable")
    assert inventory["summary"]["configured"] == 1
    assert inventory["summary"]["present"] == 1
    assert inventory["summary"]["unknown"] == 1
    assert inventory["summary"]["adapter_coverage"] == {"complete": 1, "incomplete": 1}


def test_markdown_exposes_distinct_states(tmp_path):
    module = _load_module()
    (tmp_path / "plain").mkdir()
    declared = {
        name: {"repo": name, "profile": "knowledge", "sensitivity": "public", "mcp_required": False}
        for name in ("configured", "absent", "plain")
    }
    observed, unexpected = module.observe_work_surface(tmp_path, set(declared))
    markdown = module.render_markdown(module.join_inventory(declared, {"configured"}, observed, unexpected))
    assert "| State |" in markdown
    assert "configured-missing" in markdown
    assert "declared-missing" in markdown
    assert "non-git" in markdown


def test_check_mode_never_writes(tmp_path):
    module = _load_module()
    output = tmp_path / "missing.json"
    assert module.write_or_check(output, "{}\n", check=True) is False
    assert not output.exists()


# Hand-written truth table: bits are AGENTS, Claude directory, Claude entry,
# Codex directory, Gemini directory, and optional root Claude entry, in order.
# Fixture basis: each profile has 16 declarations, 12 local Git repositories,
# 12 configured entries, 2 missing entries, 2 non-Git entries, and 4 complete
# contracts. Thus three profiles yield 48 declarations, 36 local repositories,
# 36 configured declarations, 6 missing, 6 non-Git, and 12 complete contracts.
# The configured unknown adds one configured entry; two unknown Git directories
# contribute only to aggregate counts. No expected total comes from production.
_PROFILE_CASES = ("code", "knowledge", "control-product")
_ADAPTER_PATHS = {
    "agents_md": "AGENTS.md", "claude_dir": ".claude",
    "claude_in_dir": ".claude/CLAUDE.md", "codex_dir": ".codex",
    "gemini_dir": ".gemini", "root_claude_md": "CLAUDE.md",
}
# name, state, configured, required MCP, omitted adapter, MCP file, root entry,
# sensitivity, expected adapter bits, expected MCP status, expected completeness.
_STATE_CASES = (
    ("required", "configured-present", True, True, None, True, False,
     "public", "111110", "present", True),
    ("optional-absent", "configured-present", True, False, None, False, False,
     "public", "111110", "not-required", True),
    ("optional-present", "configured-present", True, False, None, True, True,
     "public", "111111", "present", True),
    ("missing-mcp", "configured-present", True, True, None, False, True,
     "public", "111111", "missing-required", False),
    ("missing-agents", "configured-present", True, False, "agents_md", False, True,
     "public", "011111", "not-required", False),
    ("missing-claude-dir", "configured-present", True, False, "claude_dir", False, True,
     "public", "100111", "not-required", False),
    ("missing-claude-entry", "configured-present", True, False, "claude_in_dir", False, True,
     "public", "110111", "not-required", False),
    ("missing-codex", "configured-present", True, False, "codex_dir", False, True,
     "public", "111011", "not-required", False),
    ("missing-gemini", "configured-present", True, False, "gemini_dir", False, True,
     "public", "111101", "not-required", False),
    ("unclassified", "configured-present", True, False, None, False, True,
     "unclassified", "111111", "not-required", False),
    ("unregistered-complete", "observed-unregistered", False, False, None, False, False,
     "public", "111110", "not-required", True),
    ("unregistered-incomplete", "observed-unregistered", False, True, "gemini_dir", True, True,
     "public", "111101", "present", False),
    ("configured-absent", "configured-missing", True, True, None, False, False,
     "public", "000000", "missing-required", False),
    ("declared-absent", "declared-missing", False, False, None, False, False,
     "public", "000000", "not-required", False),
    ("plain-configured", "non-git", True, False, None, False, False,
     "public", "000000", "not-required", False),
    ("plain-unconfigured", "non-git", False, True, None, False, False,
     "public", "000000", "missing-required", False),
)


def _make_case_directory(path, state, omitted, mcp_file, root_entry):
    if state in {"configured-missing", "declared-missing"}:
        return
    path.mkdir()
    if state == "non-git":
        return
    (path / ".git").mkdir()
    for key, relative in _ADAPTER_PATHS.items():
        if key == omitted or (omitted == "claude_dir" and key == "claude_in_dir"):
            continue
        if key == "root_claude_md" and not root_entry:
            continue
        target = path / relative
        if key.endswith("_dir") and key != "claude_in_dir":
            target.mkdir()
        else:
            target.write_text("synthetic adapter\n", encoding="utf-8")
    if mcp_file:
        (path / ".mcp.json").write_text("{}\n", encoding="utf-8")


@pytest.fixture
def inventory_truth_table(tmp_path):
    declared, configured, expected = {}, set(), []
    for profile, case in product(_PROFILE_CASES, _STATE_CASES):
        (suffix, state, enabled, required, omitted, mcp_file, root_entry,
         sensitivity, bits, mcp_status, complete) = case
        name = f"{profile}-{suffix}"
        declared[name] = {
            "repo": name, "profile": profile, "sensitivity": sensitivity,
            "mcp_required": required,
        }
        if enabled:
            configured.add(name)
        _make_case_directory(tmp_path / name, state, omitted, mcp_file, root_entry)
        contract = {key: bit == "1" for key, bit in zip(_ADAPTER_PATHS, bits)}
        contract.update(mcp=mcp_status, complete=complete)
        expected.append({
            "configured_for_machine": enabled, "contract": contract,
            "mcp_required": required, "name": name,
            "observed_local": state in {"configured-present", "observed-unregistered"},
            "profile": profile, "sensitivity": sensitivity, "state": state,
        })
    configured.add("unknown-configured")
    for name in ("unknown-configured", "unknown-observed"):
        (tmp_path / name / ".git").mkdir(parents=True)
    module = _load_module()
    observed, unexpected = module.observe_work_surface(tmp_path, set(declared))
    return module, declared, configured, observed, unexpected, sorted(
        expected, key=lambda item: item["name"])


@pytest.mark.parametrize("profile", _PROFILE_CASES)
def test_inventory_state_profile_truth_table(inventory_truth_table, profile):
    module, declared, configured, observed, unexpected, expected = inventory_truth_table
    inventory = module.join_inventory(declared, configured, observed, unexpected)
    actual = [item for item in inventory["repositories"] if item["profile"] == profile]
    assert actual == [item for item in expected if item["profile"] == profile]


def test_inventory_permutation_stability(inventory_truth_table):
    module, declared, configured, observed, unexpected, expected = inventory_truth_table
    baseline = module.join_inventory(declared, configured, observed, unexpected)
    assert baseline["repositories"] == expected
    baseline_json = json.dumps(baseline).encode("utf-8")
    baseline_markdown = module.render_markdown(baseline).encode("utf-8")
    # The 216 loop iterations cover six declared-map and six observed-map
    # profile-block orders, repeated while configured names are rebuilt as sets.
    # Distinct configured set iteration orders are not guaranteed.
    orders = tuple(permutations(_PROFILE_CASES))

    def ordered_names(names, order):
        return sorted(names, key=lambda name: (
            next((index for index, profile in enumerate(order)
                  if name.startswith(profile + "-")), len(order)), name))

    for declared_order, configured_order, observed_order in product(orders, repeat=3):
        result = module.join_inventory(
            {name: declared[name] for name in ordered_names(declared, declared_order)},
            set(ordered_names(configured, configured_order)),
            {name: observed[name] for name in ordered_names(observed, observed_order)},
            unexpected,
        )
        assert result == baseline
        assert json.dumps(result).encode("utf-8") == baseline_json
        assert module.render_markdown(result).encode("utf-8") == baseline_markdown


# Hand totals follow the table arithmetic above. Empty has no entries; unknown
# only has one configured name and two observed Git directories, no declarations.
_SUMMARY_CASES = (
    ("empty", (0, 0, 0, 0, 0, 0, 0, 0)),
    ("unknown-only", (0, 1, 0, 0, 0, 0, 0, 2)),
    ("mixed", (48, 37, 36, 6, 6, 12, 36, 2)),
)


@pytest.mark.parametrize("surface, totals", _SUMMARY_CASES)
def test_inventory_rendered_totals_match_fixture(inventory_truth_table, surface, totals):
    module, declared, configured, observed, unexpected, expected = inventory_truth_table
    if surface == "empty":
        declared, configured, observed, unexpected, expected = {}, set(), {}, 0, []
    elif surface == "unknown-only":
        declared, configured, observed, expected = {}, {"unknown-configured"}, {}, []
    inventory = module.join_inventory(declared, configured, observed, unexpected)
    count, enabled, present, missing, non_git, complete, incomplete, unknown = totals
    assert inventory == {
        "schema_version": 1, "repositories": expected,
        "summary": {
            "declared": count, "configured": enabled, "present": present,
            "missing": missing, "non_git": non_git, "observed_declared": present,
            "contract_complete": complete,
            "adapter_coverage": {"complete": complete, "incomplete": incomplete},
            "unexpected_count": unknown, "unknown": unknown,
        },
    }
    markdown = module.render_markdown(inventory)
    summary_lines = markdown.split("## Summary\n\n")[1].split("\n\n")[0].splitlines()
    assert summary_lines == [
        f"- Declared repositories: {count}",
        f"- Configured for this machine: {enabled}",
        f"- Present Git repositories: {present}",
        f"- Missing declared repositories: {missing}",
        f"- Declared non-Git directories: {non_git}",
        f"- Declared repositories observed locally: {present}",
        f"- Complete provider contracts: {complete}",
        f"- Incomplete provider contracts: {incomplete}",
        f"- Undeclared local repositories: {unknown} (names suppressed)",
    ]
    assert sum(line.startswith("| ") for line in markdown.splitlines()) == count + 1
    for name in ("unknown-configured", "unknown-observed"):
        assert name not in json.dumps(inventory)
        assert name not in markdown
