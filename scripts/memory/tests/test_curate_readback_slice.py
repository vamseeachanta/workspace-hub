"""TDD — curate_readback_slice.py (#2841 Phase A, gap 1/2).

The shared cross-provider read-back selector. Sources ONLY git-tracked
.claude/memory/ (machine-invariant — F1), filters Claude-only entries by SLUG
(structured, default-include — F4), caps at entry boundaries with drop-and-warn
on oversize (F5), deterministic output with a managed header.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

MOD_PATH = Path(__file__).resolve().parents[1] / "curate_readback_slice.py"
spec = importlib.util.spec_from_file_location("curate_readback_slice", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["curate_readback_slice"] = mod
spec.loader.exec_module(mod)

NO_PRIORITIES = ()


@pytest.fixture
def memdir(tmp_path):
    """A fixture .claude/memory/ with index lines + KNOWLEDGE."""
    d = tmp_path / "memory"
    d.mkdir()
    (d / "claude-auto-memory.md").write_text(
        "# Claude Code Auto-Memory Snapshot\n\n# Workspace Hub Memory\n\n## Feedback\n"
        "- [Shared rule about browsers](feedback_webfetch_first_for_linkedin.md) — use WebFetch "
        "before opening a browser tab; applies to all providers (2026-05-01)\n"
        "- [Claude Chrome session-scoped](feedback_claude_in_chrome_session_scoped.md) — "
        "mcp chrome binds main session only (2026-05-02)\n"
        "- [Gmail filter-first](feedback_gmail_filter_first_over_per_thread.md) — ingestion filters "
        "handle 80% of mail (2026-05-03)\n"
        "- [Multi-agent commit serialization](feedback_multi_agent_commit_serialization.md) — "
        "pathspec commits avoid sweep contamination (2026-05-04)\n"
    )
    (d / "KNOWLEDGE.md").write_text(
        "# Institutional Knowledge\n\n## Environment Conventions\n"
        "- Windows MINGW64 paths use /d/workspace-hub/ in bash\n"
        "- Shell scripts: #!/usr/bin/env bash, LF line endings\n"
    )
    return d


def test_curate_excludes_claude_only(memdir):
    """Entries whose SLUG is claude-runtime-specific (chrome, gmail) are dropped."""
    out = mod.curate(memdir, target="codex", cap=7000, priority_slugs=NO_PRIORITIES)
    assert "claude_in_chrome_session_scoped" not in out
    assert "Gmail filter-first" not in out


def test_curate_keeps_shared_entries(memdir):
    """F4 negative test: a SHARED entry whose text mentions 'browser' is NOT dropped
    (slug-based match, not title-substring — 'browser' in the description must survive)."""
    out = mod.curate(memdir, target="codex", cap=7000, priority_slugs=NO_PRIORITIES)
    assert "Shared rule about browsers" in out
    assert "Multi-agent commit serialization" in out


def test_curate_titles_not_bodies(memdir):
    """Only index/title+desc lines + KNOWLEDGE bullets — never full topic bodies."""
    out = mod.curate(memdir, target="codex", cap=7000, priority_slugs=NO_PRIORITIES)
    # the index desc is present...
    assert "pathspec commits avoid sweep contamination" in out
    # ...and KNOWLEDGE bullets, but nothing sourced from topics/ bodies (none read)
    assert "Environment Conventions" in out or "MINGW64" in out


def test_curate_codex_cap(memdir):
    out = mod.curate(memdir, target="codex", cap=400)
    assert len(out.encode("utf-8")) <= 400


def test_curate_hermes_cap(memdir):
    out = mod.curate(memdir, target="hermes", cap=200)
    assert len(out.encode("utf-8")) <= 200


def test_curate_single_oversize_entry(memdir):
    """F5: an entry alone exceeding the cap is DROPPED with an omitted-marker, never mid-cut."""
    big = "- [Huge](feedback_huge.md) — " + ("x" * 5000) + "\n"
    (memdir / "claude-auto-memory.md").write_text(
        "## Feedback\n" + big + "- [Small](feedback_small.md) — tiny shared note\n"
    )
    out = mod.curate(memdir, target="hermes", cap=300)
    assert len(out.encode("utf-8")) <= 300
    assert "xxxxx" not in out                       # the oversize entry is not mid-cut into the slice
    assert "omitted" in out.lower()                 # a marker explains the omission


def test_curate_machine_invariant(memdir, monkeypatch):
    """F1: output depends ONLY on source_dir, never on $HOME auto-memory."""
    monkeypatch.setenv("HOME", "/nonexistent-home-A")
    a = mod.curate(memdir, target="codex", cap=7000, priority_slugs=NO_PRIORITIES)
    monkeypatch.setenv("HOME", "/nonexistent-home-B")
    b = mod.curate(memdir, target="codex", cap=7000, priority_slugs=NO_PRIORITIES)
    assert a == b                                   # HOME change must not affect output


def test_curate_idempotent(memdir):
    assert mod.curate(memdir, target="codex", cap=7000, priority_slugs=NO_PRIORITIES) == mod.curate(
        memdir, target="codex", cap=7000, priority_slugs=NO_PRIORITIES
    )


def test_curate_no_timestamps_in_body(memdir):
    """Determinism: no generation timestamp embedded (would break byte-identical across runs)."""
    out = mod.curate(memdir, target="codex", cap=7000, priority_slugs=NO_PRIORITIES)
    # the managed header may name the tool but must not stamp a today-date that changes per run
    assert not re.search(r"generated:\s*\d{4}-\d{2}-\d{2}", out, re.I)


def test_curate_managed_header(memdir):
    out = mod.curate(memdir, target="codex", cap=7000, priority_slugs=NO_PRIORITIES)
    assert "MANAGED" in out and "do not hand-edit" in out.lower()


def test_curate_regex_handles_markdown_links_in_desc(tmp_path):
    """F6: a desc containing a markdown link `[#NNNN](https://...)` must parse correctly
    (slug anchors on the FIRST `.md)`), and the entry is kept."""
    d = tmp_path / "memory"
    d.mkdir()
    (d / "claude-auto-memory.md").write_text(
        "## Feedback\n"
        "- [Cleanup gate](feedback_pre_completion_cleanup_audit_gate.md) — run audit; tracked at "
        "[#2750](https://github.com/vamseeachanta/workspace-hub/issues/2750) before done\n"
    )
    out = mod.curate(d, target="codex", cap=7000, priority_slugs=NO_PRIORITIES)
    assert "Cleanup gate" in out
    assert "#2750" in out                     # the markdown link in desc survives
    assert "feedback_pre_completion_cleanup_audit_gate" not in out.split("]")[0]  # slug parsed, not leaked as claude-only


def test_curate_empty_source(tmp_path):
    """Missing/empty source dir → header-only, no crash."""
    d = tmp_path / "memory"
    d.mkdir()
    out = mod.curate(d, target="codex", cap=7000, priority_slugs=NO_PRIORITIES)
    assert "MANAGED" in out
    assert out.count("\n- ") == 0             # no entries


def test_curate_tiny_cap_clamped(memdir):
    """F3: a degenerate cap below fixed overhead still yields len(out) <= cap."""
    for cap in (50, 100, 169):
        assert len(mod.curate(memdir, target="hermes", cap=cap).encode("utf-8")) <= cap


def test_curate_gemini_in_default_caps():
    """#3189: gemini is a first-class target reusing the codex path."""
    assert "gemini" in mod.DEFAULT_CAPS


def test_curate_gemini_parity_with_codex(memdir):
    """#3189: gemini shares the codex code path -> byte-identical at equal cap."""
    assert mod.curate(memdir, target="gemini", cap=7000, priority_slugs=NO_PRIORITIES) == mod.curate(
        memdir, target="codex", cap=7000, priority_slugs=NO_PRIORITIES
    )


def test_curate_gemini_excludes_claude_only(memdir):
    """#3189: F4 filter honored for gemini (Claude-only slugs dropped; shared kept)."""
    out = mod.curate(memdir, target="gemini", cap=7000, priority_slugs=NO_PRIORITIES)
    assert "claude_in_chrome_session_scoped" not in out
    assert "Shared rule about browsers" in out


def _write_pressure_memory(tmp_path: Path) -> Path:
    source = tmp_path / "memory"
    source.mkdir()
    rows = [
        f"- [Project {i}](project_{i}.md) — " + ("context " * 18)
        for i in range(24)
    ]
    rows.extend(
        [
            "- [Strict merge](feedback_strict.md) — keep CLEAN merge authorization",
            "- [Generated state](feedback_origin.md) — verify against origin/main",
            "- [Operational extra](feedback_extra.md) — preserve feedback capacity",
            "- [Reference](reference_architecture.md) — shared reference context",
            "- [Unknown](new_kind.md) — default include as context",
        ]
    )
    (source / "claude-auto-memory.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (source / "KNOWLEDGE.md").write_text(
        "# Institutional Knowledge\n"
        "- Current institution — shared convention\n"
        "  - nested detail must not detach\n"
        "- Old institution *stale: 2026-01-01*\n"
        "- A current sentence may discuss stale data without a terminal marker\n",
        encoding="utf-8",
    )
    return source


def test_class_reservations_survive_project_pressure(tmp_path):
    source = _write_pressure_memory(tmp_path)
    out = mod.curate(
        source,
        target="hermes",
        cap=2000,
        priority_slugs=("feedback_strict", "feedback_origin"),
    )
    assert "Current institution" in out
    assert "Strict merge" in out and "Generated state" in out
    assert "Project 0" in out
    assert len(out.encode("utf-8")) <= 2000


def test_institutional_entries_are_top_level_and_current(tmp_path):
    source = _write_pressure_memory(tmp_path)
    entries = mod._collect_entries(source)
    texts = [entry.text for entry in entries]
    assert any("Current institution" in text for text in texts)
    assert any("discuss stale data" in text for text in texts)
    assert not any("nested detail" in text for text in texts)
    assert not any("Old institution" in text for text in texts)


def test_unknown_slug_defaults_to_context(tmp_path):
    source = _write_pressure_memory(tmp_path)
    entries = mod._collect_entries(source)
    unknown = next(entry for entry in entries if entry.slug == "new_kind")
    assert unknown.entry_class == "context"


def test_reservations_use_utf8_bytes_and_context_gets_remainder():
    allocations = mod._class_allocations(101)
    assert allocations == {"institutional": 15, "operational": 50, "context": 36}
    assert mod._byte_len("é\n") == 3


@pytest.mark.parametrize("count", [9, 10, 99, 100])
def test_maximum_count_marker_reserve_bounds_exact_marker(count):
    maximum = mod._omitted_marker(count)
    for actual in range(1, count + 1):
        assert mod._byte_len(mod._omitted_marker(actual)) <= mod._byte_len(maximum)


def test_spill_selection_emits_in_original_order(tmp_path):
    source = tmp_path / "memory"
    source.mkdir()
    (source / "claude-auto-memory.md").write_text(
        "- [Earlier large](project_earlier.md) — " + ("x" * 350) + "\n"
        "- [Later small](project_later.md) — small\n"
        "- [Priority](feedback_priority.md) — required\n",
        encoding="utf-8",
    )
    (source / "KNOWLEDGE.md").write_text("- Institutional — compact\n", encoding="utf-8")
    out = mod.curate(source, "hermes", 2000, priority_slugs=("feedback_priority",))
    assert out.index("Earlier large") < out.index("Later small") < out.index("Priority") < out.index("Institutional")
    assert out == mod.curate(source, "hermes", 2000, priority_slugs=("feedback_priority",))


@pytest.mark.parametrize(
    ("manifest", "message"),
    [
        ({"schema_version": 1, "must_retain_operational_slugs": ["feedback_missing"]}, "missing"),
        ({"schema_version": 1, "must_retain_operational_slugs": ["feedback_strict", "feedback_strict"]}, "duplicate"),
        ({"schema_version": 1, "must_retain_operational_slugs": ["feedback_claude_in_chrome"]}, "Claude-only"),
    ],
)
def test_priority_manifest_fails_closed(tmp_path, manifest, message):
    import yaml

    source = _write_pressure_memory(tmp_path)
    path = tmp_path / "priorities.yaml"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        mod.curate(source, "hermes", 2000, priority_path=path)


@pytest.mark.parametrize(
    "duplicate_lines",
    [
        "schema_version: 1\nschema_version: 1\n",
        "must_retain_operational_slugs: []\nmust_retain_operational_slugs: []\n",
    ],
)
def test_priority_manifest_rejects_duplicate_mapping_keys(tmp_path, duplicate_lines):
    source = _write_pressure_memory(tmp_path)
    path = tmp_path / "priorities.yaml"
    path.write_text(duplicate_lines, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate mapping key"):
        mod.curate(source, "hermes", 2000, priority_path=path)


@pytest.mark.parametrize("schema_version", ["true", "1.0"])
def test_priority_manifest_requires_integer_schema_version(tmp_path, schema_version):
    source = _write_pressure_memory(tmp_path)
    path = tmp_path / "priorities.yaml"
    path.write_text(
        f"schema_version: {schema_version}\nmust_retain_operational_slugs: []\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="schema_version must be integer 1"):
        mod.curate(source, "hermes", 2000, priority_path=path)


def test_priority_over_budget_fails_closed(tmp_path):
    source = tmp_path / "memory"
    source.mkdir()
    huge = "- [Huge required](feedback_huge.md) — " + ("x" * 1200) + "\n"
    (source / "claude-auto-memory.md").write_text(huge, encoding="utf-8")
    with pytest.raises(ValueError, match="operational reservation"):
        mod.curate(source, "hermes", 2000, priority_slugs=("feedback_huge",))


def test_small_custom_cap_is_explicitly_degraded(memdir):
    out = mod.curate(memdir, "hermes", 300, priority_slugs=("definitely_missing",))
    assert len(out.encode("utf-8")) <= 300


def test_live_corpus_retains_manifest_priorities():
    repo_root = MOD_PATH.parents[2]
    source = repo_root / ".claude" / "memory"
    for target, cap in mod.DEFAULT_CAPS.items():
        out = mod.curate(source, target, cap)
        assert "feedback_strict_uptodate_ruleset_no_admin_bypass.md" in out
        assert "feedback_verify_generated_state_against_origin_not_working_copy.md" in out
        assert len(out.encode("utf-8")) <= cap


def test_hermes_production_cap_retains_all_classes():
    repo_root = MOD_PATH.parents[2]
    out = mod.curate(repo_root / ".claude" / "memory", "hermes", 2000)
    assert "KNOWLEDGE.md" not in out  # bullets, not source metadata
    assert "feedback_strict_uptodate_ruleset_no_admin_bypass.md" in out
    assert "project_" in out
    assert any(
        line.startswith("- ") and "](" not in line
        for line in out.splitlines()
    )
    assert re.search(r"_\[\d+ entr(?:y|ies) omitted: oversize/over-cap\]_", out)
