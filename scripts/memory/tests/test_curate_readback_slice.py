"""TDD — curate_readback_slice.py (#2841 Phase A, gap 1/2).

The shared cross-provider read-back selector. Sources ONLY git-tracked
.claude/memory/ (machine-invariant — F1), filters Claude-only entries by SLUG
(structured, default-include — F4), caps at entry boundaries with drop-and-warn
on oversize (F5), deterministic output with a managed header.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MOD_PATH = Path(__file__).resolve().parents[1] / "curate_readback_slice.py"
spec = importlib.util.spec_from_file_location("curate_readback_slice", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["curate_readback_slice"] = mod
spec.loader.exec_module(mod)


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
    out = mod.curate(memdir, target="codex", cap=7000)
    assert "claude_in_chrome_session_scoped" not in out
    assert "Gmail filter-first" not in out


def test_curate_keeps_shared_entries(memdir):
    """F4 negative test: a SHARED entry whose text mentions 'browser' is NOT dropped
    (slug-based match, not title-substring — 'browser' in the description must survive)."""
    out = mod.curate(memdir, target="codex", cap=7000)
    assert "Shared rule about browsers" in out
    assert "Multi-agent commit serialization" in out


def test_curate_titles_not_bodies(memdir):
    """Only index/title+desc lines + KNOWLEDGE bullets — never full topic bodies."""
    out = mod.curate(memdir, target="codex", cap=7000)
    # the index desc is present...
    assert "pathspec commits avoid sweep contamination" in out
    # ...and KNOWLEDGE bullets, but nothing sourced from topics/ bodies (none read)
    assert "Environment Conventions" in out or "MINGW64" in out


def test_curate_codex_cap(memdir):
    out = mod.curate(memdir, target="codex", cap=400)
    assert len(out) <= 400


def test_curate_hermes_cap(memdir):
    out = mod.curate(memdir, target="hermes", cap=200)
    assert len(out) <= 200


def test_curate_single_oversize_entry(memdir):
    """F5: an entry alone exceeding the cap is DROPPED with an omitted-marker, never mid-cut."""
    big = "- [Huge](feedback_huge.md) — " + ("x" * 5000) + "\n"
    (memdir / "claude-auto-memory.md").write_text(
        "## Feedback\n" + big + "- [Small](feedback_small.md) — tiny shared note\n"
    )
    out = mod.curate(memdir, target="hermes", cap=300)
    assert len(out) <= 300
    assert "xxxxx" not in out                       # the oversize entry is not mid-cut into the slice
    assert "omitted" in out.lower()                 # a marker explains the omission


def test_curate_machine_invariant(memdir, monkeypatch):
    """F1: output depends ONLY on source_dir, never on $HOME auto-memory."""
    monkeypatch.setenv("HOME", "/nonexistent-home-A")
    a = mod.curate(memdir, target="codex", cap=7000)
    monkeypatch.setenv("HOME", "/nonexistent-home-B")
    b = mod.curate(memdir, target="codex", cap=7000)
    assert a == b                                   # HOME change must not affect output


def test_curate_idempotent(memdir):
    assert mod.curate(memdir, target="codex", cap=7000) == mod.curate(memdir, target="codex", cap=7000)


def test_curate_no_timestamps_in_body(memdir):
    """Determinism: no generation timestamp embedded (would break byte-identical across runs)."""
    out = mod.curate(memdir, target="codex", cap=7000)
    import re
    # the managed header may name the tool but must not stamp a today-date that changes per run
    assert not re.search(r"generated:\s*\d{4}-\d{2}-\d{2}", out, re.I)


def test_curate_managed_header(memdir):
    out = mod.curate(memdir, target="codex", cap=7000)
    assert "MANAGED" in out and "do not hand-edit" in out.lower()


def test_curate_regex_handles_markdown_links_in_desc(tmp_path):
    """F6: a desc containing a markdown link `[#NNNN](https://...)` must parse correctly
    (slug anchors on the FIRST `.md)`), and the entry is kept."""
    d = tmp_path / "memory"; d.mkdir()
    (d / "claude-auto-memory.md").write_text(
        "## Feedback\n"
        "- [Cleanup gate](feedback_pre_completion_cleanup_audit_gate.md) — run audit; tracked at "
        "[#2750](https://github.com/vamseeachanta/workspace-hub/issues/2750) before done\n"
    )
    out = mod.curate(d, target="codex", cap=7000)
    assert "Cleanup gate" in out
    assert "#2750" in out                     # the markdown link in desc survives
    assert "feedback_pre_completion_cleanup_audit_gate" not in out.split("]")[0]  # slug parsed, not leaked as claude-only


def test_curate_empty_source(tmp_path):
    """Missing/empty source dir → header-only, no crash."""
    d = tmp_path / "memory"; d.mkdir()
    out = mod.curate(d, target="codex", cap=7000)
    assert "MANAGED" in out
    assert out.count("\n- ") == 0             # no entries


def test_curate_tiny_cap_clamped(memdir):
    """F3: a degenerate cap below fixed overhead still yields len(out) <= cap."""
    for cap in (50, 100, 169):
        assert len(mod.curate(memdir, target="hermes", cap=cap)) <= cap


def test_curate_gemini_in_default_caps():
    """#3189: gemini is a first-class target reusing the codex path."""
    assert "gemini" in mod.DEFAULT_CAPS


def test_curate_gemini_parity_with_codex(memdir):
    """#3189: gemini shares the codex code path -> byte-identical at equal cap."""
    assert mod.curate(memdir, target="gemini", cap=7000) == mod.curate(memdir, target="codex", cap=7000)


def test_curate_gemini_excludes_claude_only(memdir):
    """#3189: F4 filter honored for gemini (Claude-only slugs dropped; shared kept)."""
    out = mod.curate(memdir, target="gemini", cap=7000)
    assert "claude_in_chrome_session_scoped" not in out
    assert "Shared rule about browsers" in out
