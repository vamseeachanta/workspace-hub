"""Tests for scripts/enforcement/check-wiki-sibling-frontmatter.py (#2778).

19 test cases derived from docs/plans/2026-05-22-issue-2778-wiki-sibling-routing-contract.md
TDD: tests written before implementation; expected to FAIL initially (red phase).

Fixture strategy: each test builds a hermetic git repo under tmp_path with a
wiki-shaped name (e.g., llm-wiki-acma), vendors a registry copy, stages content,
and invokes the script via subprocess. Hermeticity ensures no cross-test
contamination and no dependence on the host workspace-hub state.

Rule coverage:
    Rule A — visibility allowed-set
    Rule B — private-client-llm-wiki requires client:
    Rule C — client slug must match repo identity AND exist in registry
    Rule D — project: only valid when visibility=private-client-llm-wiki
    Rule E — project: must be enumerated in registry.projects when populated

r2 review findings absorbed:
    F1 — repo-identity via git rev-parse, NOT path-prefix
    F3 — pages/ included in scope
    F4 — README.md excluded from project validation
    F5 — CI shallow-clone safety (fetch fallback)
    F6 — WIKI_FRONTMATTER_ALLOW bypass
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PY = REPO_ROOT / "scripts" / "enforcement" / "check-wiki-sibling-frontmatter.py"
SCRIPT_SH = REPO_ROOT / "scripts" / "enforcement" / "check-wiki-sibling-frontmatter.sh"


# ── Fixtures ──────────────────────────────────────────────────────────────


def _make_wiki_repo(parent: Path, name: str) -> Path:
    """Initialize a hermetic wiki-named git repo at parent/name."""
    repo = parent / name
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Test"], check=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "commit.gpgsign", "false"], check=True
    )
    (repo / "README.md").write_text("# init\n")
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-q", "-m", "init", "--no-verify"],
        check=True,
    )
    return repo


def _vendor_registry(repo: Path, content: str | None = None) -> None:
    """Vendor a client-wikis.yml registry into the wiki repo's .workspace-hub/."""
    vendor_dir = repo / ".workspace-hub"
    vendor_dir.mkdir(exist_ok=True)
    default = """\
registry_version: 0.1
wikis:
  - short_name: acma
    repo: vamseeachanta/llm-wiki-acma
    visibility: PRIVATE
    posture: client-private
    status: bootstrapped
    projects:
      - sirocco
  - short_name: doris
    repo: vamseeachanta/llm-wiki-doris
    visibility: PRIVATE
    posture: client-private
    status: planned
  - short_name: client-projects
    repo: vamseeachanta/llm-wiki-client-projects
    visibility: PRIVATE
    posture: client-private
    status: planned
  - short_name: frontierdeepwater
    repo: vamseeachanta/llm-wiki-frontierdeepwater
    visibility: PRIVATE
    posture: client-private
    status: planned
"""
    (vendor_dir / "client-wikis.yml").write_text(content or default)


def _stage(repo: Path, path: str, content: str) -> None:
    """Write content to repo/path and `git add` it."""
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    subprocess.run(["git", "-C", str(repo), "add", "--", path], check=True)


def _commit_for_ci(repo: Path, msg: str = "ci change") -> None:
    """Commit staged content to enable CI-mode diffs (base..HEAD)."""
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-q", "-m", msg, "--no-verify"],
        check=True,
    )


def _run_check(repo: Path, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    """Invoke the enforcement script with cwd=repo."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["python3", str(SCRIPT_PY)],
        cwd=repo,
        capture_output=True,
        text=True,
        env=env,
    )


def _fm(visibility: str, client: str | None = None, project: str | None = None) -> str:
    """Build a minimal YAML frontmatter block."""
    lines = ["---", f"visibility: {visibility}"]
    if client is not None:
        lines.append(f"client: {client}")
    if project is not None:
        lines.append(f"project: {project}")
    lines.append("---")
    lines.append("# page body\n")
    return "\n".join(lines)


# ── Rule A: visibility allowed-set ─────────────────────────────────────────


def test_enforcement_passes_on_valid_generic_frontmatter(tmp_path: Path) -> None:
    """A wiki page with visibility=private-llm-wiki and no client: passes (Rule A baseline)."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki")
    _vendor_registry(repo)
    _stage(repo, "wikis/marine-engineering/wiki/concepts/foo.md", _fm("private-llm-wiki"))
    r = _run_check(repo)
    assert r.returncode == 0, f"unexpected fail: stdout={r.stdout} stderr={r.stderr}"


def test_enforcement_passes_on_valid_private_client_frontmatter(tmp_path: Path) -> None:
    """A wiki page with visibility=private-client-llm-wiki + client + project passes."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki-acma")
    _vendor_registry(repo)
    _stage(repo, "projects/sirocco/methodology/foo.md", _fm("private-client-llm-wiki", client="acma", project="sirocco"))
    r = _run_check(repo)
    assert r.returncode == 0, f"unexpected fail: stdout={r.stdout} stderr={r.stderr}"


def test_enforcement_fails_when_visibility_invalid(tmp_path: Path) -> None:
    """Rule A — unknown visibility tier fails."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki")
    _vendor_registry(repo)
    _stage(repo, "wikis/foo.md", _fm("public-wiki"))  # not in allowed set
    r = _run_check(repo)
    assert r.returncode == 1
    assert "visibility" in r.stderr
    assert "public-wiki" in r.stderr


# ── Rule B: private-client-llm-wiki requires client: ───────────────────────


def test_enforcement_fails_when_private_client_missing_client(tmp_path: Path) -> None:
    """Rule B — private-client-llm-wiki without client: fails."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki-acma")
    _vendor_registry(repo)
    _stage(repo, "pages/foo.md", _fm("private-client-llm-wiki"))  # no client:
    r = _run_check(repo)
    assert r.returncode == 1
    assert "client" in r.stderr


# ── Rule C: client slug must match repo identity AND exist in registry ─────


def test_enforcement_fails_when_client_not_in_registry(tmp_path: Path) -> None:
    """Rule C — client slug not registered fails."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki-unknown")
    _vendor_registry(repo)
    _stage(repo, "pages/foo.md", _fm("private-client-llm-wiki", client="unknown"))
    r = _run_check(repo)
    assert r.returncode == 1
    assert "unknown" in r.stderr


def test_enforcement_fails_when_client_slug_mismatches_repo_identity(tmp_path: Path) -> None:
    """Rule C (r2-F1) — client value must match the wiki repo's identity (suffix after llm-wiki-)."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki-doris")
    _vendor_registry(repo)
    _stage(repo, "pages/foo.md", _fm("private-client-llm-wiki", client="acma"))  # acma != doris
    r = _run_check(repo)
    assert r.returncode == 1
    assert "doris" in r.stderr or "acma" in r.stderr


# ── Rule D: project: only valid when visibility=private-client-llm-wiki ────


def test_enforcement_fails_when_project_without_private_client_visibility(tmp_path: Path) -> None:
    """Rule D — project: set without private-client-llm-wiki visibility fails."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki")
    _vendor_registry(repo)
    _stage(repo, "wikis/foo.md", _fm("private-llm-wiki", project="sirocco"))  # project on generic
    r = _run_check(repo)
    assert r.returncode == 1
    assert "project" in r.stderr


# ── Rule E: project must exist in registry.projects when populated ─────────


def test_enforcement_fails_when_project_not_in_registry_projects_list(tmp_path: Path) -> None:
    """Rule E (r1-F5) — project value must be enumerated in registry.projects when populated."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki-acma")
    _vendor_registry(repo)  # default registry has acma.projects=[sirocco]
    _stage(repo, "projects/unknown/foo.md", _fm("private-client-llm-wiki", client="acma", project="unknown"))
    r = _run_check(repo)
    assert r.returncode == 1
    assert "unknown" in r.stderr or "projects" in r.stderr


def test_enforcement_warns_when_registry_projects_list_absent(tmp_path: Path) -> None:
    """Rule E forward-compat — when client.projects is absent/empty, warn-only (exit 0)."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki-doris")
    _vendor_registry(repo)  # doris has no projects: key
    _stage(repo, "projects/new-project/foo.md", _fm("private-client-llm-wiki", client="doris", project="new-project"))
    r = _run_check(repo)
    assert r.returncode == 0, f"expected warn-only pass: stdout={r.stdout} stderr={r.stderr}"


# ── Path-filter / scope tests ──────────────────────────────────────────────


def test_enforcement_passes_on_pages_dir_frontmatter(tmp_path: Path) -> None:
    """r2-F3 — pages/ (not just wikis/) is also validated."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki-acma")
    _vendor_registry(repo)
    _stage(repo, "pages/handbook/foo.md", _fm("private-client-llm-wiki", client="acma", project="sirocco"))
    r = _run_check(repo)
    assert r.returncode == 0, f"unexpected fail: stdout={r.stdout} stderr={r.stderr}"


def test_enforcement_skips_non_wiki_paths(tmp_path: Path) -> None:
    """Staged file outside wiki path globs is ignored."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki")
    _vendor_registry(repo)
    _stage(repo, "docs/reports/foo.md", _fm("invalid-visibility"))  # bad fm, but wrong path
    r = _run_check(repo)
    assert r.returncode == 0, f"unexpected fail on out-of-scope path: stderr={r.stderr}"


def test_enforcement_skips_unstaged_files(tmp_path: Path) -> None:
    """Pre-commit mode — only staged files trigger check; working-tree-only changes don't."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki")
    _vendor_registry(repo)
    target = repo / "wikis" / "foo.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_fm("invalid-visibility"))  # NOT staged
    r = _run_check(repo)
    assert r.returncode == 0, f"unstaged file should not trigger check: stderr={r.stderr}"


def test_enforcement_skips_when_not_in_wiki_repo(tmp_path: Path) -> None:
    """r2-F1 — repo identity check bails early outside wiki repos."""
    repo = _make_wiki_repo(tmp_path, "workspace-hub")  # not a wiki name
    _stage(repo, "wikis/foo.md", _fm("invalid-visibility"))
    r = _run_check(repo)
    assert r.returncode == 0, f"should bail early in non-wiki repo: stderr={r.stderr}"


def test_enforcement_excludes_readme_md_from_project_validation(tmp_path: Path) -> None:
    """r2-F4 — README.md basenames excluded from projects/**/*.md validation."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki-acma")
    _vendor_registry(repo)
    # README without frontmatter under projects/ — should NOT trip
    _stage(repo, "projects/sirocco/README.md", "# Project Sirocco\n\nNavigation aid, no frontmatter.\n")
    r = _run_check(repo)
    assert r.returncode == 0, f"README should be excluded: stdout={r.stdout} stderr={r.stderr}"


def test_enforcement_handles_bucket_name_edge_cases(tmp_path: Path) -> None:
    """#2731 D5/D6 edge cases (client_projects underscore raw-root, frontierdeepwater no-hyphen)
    resolve correctly via repo identity."""
    repo_cp = _make_wiki_repo(tmp_path, "llm-wiki-client-projects")
    _vendor_registry(repo_cp)
    _stage(repo_cp, "projects/foo/methodology/x.md", _fm("private-client-llm-wiki", client="client-projects", project="foo"))
    r1 = _run_check(repo_cp)
    assert r1.returncode == 0, f"client-projects edge case failed: stderr={r1.stderr}"

    repo_fd = _make_wiki_repo(tmp_path, "llm-wiki-frontierdeepwater")
    _vendor_registry(repo_fd)
    _stage(repo_fd, "pages/foo.md", _fm("private-client-llm-wiki", client="frontierdeepwater"))
    r2 = _run_check(repo_fd)
    assert r2.returncode == 0, f"frontierdeepwater edge case failed: stderr={r2.stderr}"


# ── Mode tests ─────────────────────────────────────────────────────────────


def test_enforcement_pre_commit_mode_uses_cached_diff(tmp_path: Path) -> None:
    """Pre-commit mode (no CI env) uses git diff --cached."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki")
    _vendor_registry(repo)
    _stage(repo, "wikis/foo.md", _fm("invalid-visibility"))
    r = _run_check(repo)  # no CI env
    assert r.returncode == 1, "staged invalid frontmatter should fail in pre-commit mode"


def test_enforcement_ci_mode_uses_base_ref_diff(tmp_path: Path) -> None:
    """r2-F2 — CI mode (CI=true) uses ${BASE_REF}..HEAD instead of --cached."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki")
    _vendor_registry(repo)
    # Create a base commit, then commit a bad-frontmatter change on top.
    base_sha = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    _stage(repo, "wikis/bad.md", _fm("invalid-visibility"))
    _commit_for_ci(repo, "add bad frontmatter")
    # In CI mode, with base_ref = the initial commit, the diff includes wikis/bad.md.
    r = _run_check(repo, env_extra={"CI": "true", "WIKI_FRONTMATTER_BASE_REF": base_sha})
    assert r.returncode == 1, f"CI mode should detect committed bad frontmatter: stderr={r.stderr}"


# ── Bypass tests ───────────────────────────────────────────────────────────


def test_enforcement_bypass_via_wiki_frontmatter_allow_env(tmp_path: Path) -> None:
    """r2-F6 — WIKI_FRONTMATTER_ALLOW=1 bypasses the check with stderr log."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki")
    _vendor_registry(repo)
    _stage(repo, "wikis/bad.md", _fm("invalid-visibility"))
    r = _run_check(repo, env_extra={"WIKI_FRONTMATTER_ALLOW": "1"})
    assert r.returncode == 0, "bypass should pass even with bad frontmatter"
    assert "bypass" in r.stderr.lower() or "WIKI_FRONTMATTER_ALLOW" in r.stderr


# ── Wrapper test ──────────────────────────────────────────────────────────


def test_sh_wrapper_invokes_python_script(tmp_path: Path) -> None:
    """The .sh wrapper at scripts/enforcement/check-wiki-sibling-frontmatter.sh execs the .py."""
    repo = _make_wiki_repo(tmp_path, "llm-wiki")
    _vendor_registry(repo)
    _stage(repo, "wikis/foo.md", _fm("private-llm-wiki"))
    r = subprocess.run(
        ["bash", str(SCRIPT_SH)],
        cwd=repo,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    assert r.returncode == 0, f"wrapper should pass on valid input: stdout={r.stdout} stderr={r.stderr}"
