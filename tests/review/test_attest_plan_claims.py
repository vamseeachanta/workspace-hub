"""Tests for scripts/review/attest-plan-claims.sh (#2405).

Tests stub `gh` via a per-test directory prepended to PATH so the script
stays pure (no test-mode env vars in production code). File existence
checks use tmp_path-staged plan directories.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import textwrap
import time
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "review" / "attest-plan-claims.sh"
FIXTURE = REPO_ROOT / "tests" / "review" / "fixtures" / "sample_plan_with_citations.md"

ALLOWLIST_REGEX = r"^docs/plans/[^/]+\.md$"


def _stage_plan_dir(tmp_path: Path, fixture_text: str | None = None, filename: str = "sample.md") -> tuple[Path, str, Path]:
    """Create <tmp>/docs/plans/<filename> with fixture content and a git repo.

    The git repo is needed because the attestation script records
    `git rev-parse HEAD` in its output header.

    Returns (cwd, plan_rel_path, plan_abs_path).
    """
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    plan_file = plans_dir / filename
    plan_file.write_text(fixture_text if fixture_text is not None else FIXTURE.read_text())
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=T",
         "commit", "--allow-empty", "-qm", "init"],
        cwd=tmp_path, check=True,
    )
    return tmp_path, f"docs/plans/{filename}", plan_file


def _make_fake_gh(bin_dir: Path, responses: dict[str, tuple[str, int]] | None = None) -> Path:
    """Create a fake `gh` on `bin_dir`. Writes every invocation's argv to gh_invocations.log."""
    defaults: dict[str, tuple[str, int]] = {
        "2208": ("- #2208 CLOSED retrieval contract extended", 0),
        "2206": ("- #2206 OPEN conformance plan", 0),
        "2405": ("- #2405 OPEN cross-review sandbox attestation", 0),
        "2403": ("- #2403 OPEN embeddings model-selection spike", 0),
    }
    resp = {**defaults, **(responses or {})}
    for out, _code in resp.values():
        assert "'" not in out, "fake-gh test responses must not contain single quotes"
    log = bin_dir / "gh_invocations.log"
    case_lines = [f'    {n}) echo \'{out}\'; exit {code} ;;' for n, (out, code) in resp.items()]
    cases = "\n".join(case_lines)
    body = textwrap.dedent(f"""\
        #!/usr/bin/env bash
        printf '%s\\n' "$*" >> '{log}'
        prev=""
        issue=""
        for a in "$@"; do
          if [[ "$prev" == "view" ]]; then issue="$a"; break; fi
          prev="$a"
        done
        case "$issue" in
        {cases}
            *) exit 1 ;;
        esac
        """)
    gh_path = bin_dir / "gh"
    gh_path.write_text(body)
    gh_path.chmod(0o755)
    return gh_path


def _run(plan_rel: str, *, cwd: Path, fake_gh_bin: Path | None = None,
         extra_env: dict | None = None, timeout: int = 30) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if fake_gh_bin is not None:
        env["PATH"] = str(fake_gh_bin) + os.pathsep + env["PATH"]
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(SCRIPT), plan_rel],
        cwd=cwd, capture_output=True, text=True, env=env, timeout=timeout,
    )


def _read_gh_log(bin_dir: Path) -> list[str]:
    log = bin_dir / "gh_invocations.log"
    if not log.exists():
        return []
    return [ln for ln in log.read_text().splitlines() if ln.strip()]


# --------------------------------------------------------------------------- #
# Cluster 1: CLI validation                                                   #
# --------------------------------------------------------------------------- #

def test_rejects_plan_path_outside_allowlist(tmp_path):
    bad = tmp_path / "notes" / "plan.md"
    bad.parent.mkdir(parents=True)
    bad.write_text("not a real plan")
    r = _run(str(bad), cwd=tmp_path)
    assert r.returncode != 0, f"expected non-zero exit, got stdout={r.stdout!r}"
    assert "allowlist" in r.stderr.lower()


def test_rejects_plan_path_in_docs_plans_subdir(tmp_path):
    """Allowlist explicitly disallows nested paths like docs/plans/sub/foo.md (v3 scope)."""
    cwd, _, _ = _stage_plan_dir(tmp_path)
    nested = cwd / "docs" / "plans" / "sub"
    nested.mkdir()
    (nested / "foo.md").write_text("nested")
    r = _run("docs/plans/sub/foo.md", cwd=cwd)
    assert r.returncode != 0
    assert "allowlist" in r.stderr.lower()


def test_rejects_nonexistent_plan_file(tmp_path):
    cwd, _, _ = _stage_plan_dir(tmp_path)
    r = _run("docs/plans/does-not-exist.md", cwd=cwd)
    assert r.returncode != 0
    assert "not found" in r.stderr.lower()


def test_accepts_valid_plan_path_under_docs_plans(tmp_path):
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, f"stderr={r.stderr!r}\nstdout={r.stdout!r}"


def test_allowlist_regex_literal_appears_in_script():
    """AC: allowlist regex must be defined once and match the Deliverable wording.
    We enforce this by requiring the exact literal to appear in the script text."""
    assert SCRIPT.read_text().count(ALLOWLIST_REGEX) >= 1, (
        f"script must contain allowlist regex {ALLOWLIST_REGEX!r} as a single source of truth"
    )


# --------------------------------------------------------------------------- #
# Cluster 2: Citation extraction + gh invocation                              #
# --------------------------------------------------------------------------- #

def test_extracts_and_emits_issue_numbers_from_fixture(tmp_path):
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    # Plan regex is 3-5 digits so #9999999 is excluded by design; 4 issues are extracted
    for n in ("2208", "2206", "2405", "2403"):
        assert f"#{n}" in r.stdout, f"expected #{n} in attestation output:\n{r.stdout}"


def test_emits_attested_evidence_header(tmp_path):
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    assert "## Attested Evidence" in r.stdout
    assert "**Issue states**" in r.stdout
    assert "**File existence**" in r.stdout


def test_extracts_backticked_paths_with_known_extensions(tmp_path):
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    # Fixture has these backticked paths with allowed extensions:
    for p in (
        "scripts/review/cross-review.sh",
        "scripts/review/attest-plan-claims.sh",
        "tests/review/test_attest_plan_claims.py",
        "pyproject.toml",
        "docs/plans/_template-issue-plan.md",
        ".claude/skills/coordination/issue-planning-mode/SKILL.md",
    ):
        assert p in r.stdout, f"expected backticked path {p!r} in output:\n{r.stdout}"


def test_skips_plain_non_backticked_paths(tmp_path):
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    # The fixture mentions "docs/plans/foo.md" plainly in the Non-backticked section;
    # it must NOT appear in the file-existence block (documented v2+ limitation).
    # We check the File existence block specifically.
    file_section = r.stdout.split("**File existence**", 1)[1] if "**File existence**" in r.stdout else ""
    assert "docs/plans/foo.md" not in file_section, (
        f"plain-path 'docs/plans/foo.md' should NOT be extracted; File existence block was:\n{file_section}"
    )


def test_gh_issue_view_invoked_per_extracted_issue(tmp_path):
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    log = _read_gh_log(bin_dir)
    invoked_issues = set()
    for line in log:
        # fake gh logs argv joined with spaces; find "view <N>"
        m = re.search(r"\bview\s+(\d+)\b", line)
        if m:
            invoked_issues.add(m.group(1))
    assert invoked_issues == {"2208", "2206", "2405", "2403"}, (
        f"expected gh invoked per extracted issue; got {invoked_issues}"
    )


def test_gh_view_limits_to_state_title_only(tmp_path):
    """Privacy: gh must be called with --json number,state,title only — no body, no labels."""
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    log = _read_gh_log(bin_dir)
    for line in log:
        if "view" not in line:
            continue
        assert "body" not in line, f"gh must not request body fields: {line!r}"
        assert "labels" not in line, f"gh must not request labels fields: {line!r}"
        assert "--json" in line, f"gh must use --json: {line!r}"
        # Must be exactly number,state,title (order-insensitive)
        m = re.search(r"--json\s+(\S+)", line)
        assert m, f"--json field list missing: {line!r}"
        fields = set(m.group(1).split(","))
        assert fields == {"number", "state", "title"}, (
            f"gh --json fields must be exactly number,state,title; got {fields} in {line!r}"
        )


def test_extracts_issue_numbers_rejects_longer_digit_strings(tmp_path):
    """Plan-deviation regression: `#[0-9]{3,5}` without \\b mis-extracts #9999999 as #99999.
    Implementation adds \\b word boundary; this test locks the behavior in."""
    plan_text = (
        "# Test plan\n\n"
        "References: #2405 and #2208 (real).\n"
        "Large-number placeholder: #9999999 (7 digits — must NOT be extracted).\n"
        "Small: #12 (2 digits — below minimum — must NOT be extracted).\n"
    )
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path, fixture_text=plan_text)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    log = _read_gh_log(bin_dir)
    invoked = set()
    for line in log:
        m = re.search(r"\bview\s+(\d+)\b", line)
        if m: invoked.add(m.group(1))
    assert invoked == {"2405", "2208"}, (
        f"only 3-5 digit whole-number issues must be extracted; got {invoked}"
    )


def test_gh_issue_view_partial_failure_falls_back(tmp_path):
    """One bad issue should emit a fallback line, not abort the whole attestation."""
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    # Override: #2208 returns exit 1 (simulates gh-lookup-failed or private)
    _make_fake_gh(bin_dir, responses={"2208": ("", 1)})
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, f"partial failure must not crash script: {r.stderr}"
    # The plan pseudocode fallback: "- $n (gh-lookup-failed or private)"
    assert "gh-lookup-failed or private" in r.stdout, (
        f"expected fallback line for failing gh view; stdout:\n{r.stdout}"
    )
    # Other issues should still be present (whole-script did not abort)
    assert "#2405" in r.stdout
    assert "#2206" in r.stdout


# --------------------------------------------------------------------------- #
# Cluster 3: File existence + symlink handling                                #
# --------------------------------------------------------------------------- #

def _parse_attestation(stdout: str) -> dict:
    """Split attestation stdout into payload text + declared sha. Returns
    {'payload': <text-without-sha-footer>, 'declared_sha': <hex>|None}."""
    lines = stdout.split("\n")
    sha_idx = None
    for i, line in enumerate(lines):
        if line.startswith("_Attestation payload sha256: ") and line.endswith("_"):
            sha_idx = i
            break
    if sha_idx is None:
        return {"payload": stdout, "declared_sha": None}
    m = re.match(r"_Attestation payload sha256: ([0-9a-f]{64})_", lines[sha_idx])
    declared = m.group(1) if m else None
    # Payload text = everything before the blank line preceding the sha footer.
    # echo "$PAYLOAD" adds trailing \n, and the blank line comes from `echo ""`.
    assert sha_idx >= 2 and lines[sha_idx - 1] == "", (
        f"expected blank line before sha footer; got lines[{sha_idx-1}]={lines[sha_idx-1]!r}"
    )
    payload = "\n".join(lines[:sha_idx - 1])
    return {"payload": payload, "declared_sha": declared}


def test_reports_missing_paths_as_missing(tmp_path):
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    # None of the fixture's cited paths exist inside tmp_path → all must be MISSING
    assert "MISSING: scripts/review/cross-review.sh" in r.stdout
    assert "MISSING: pyproject.toml" in r.stdout


def test_reports_extant_paths_with_ls_line(tmp_path):
    cwd, plan_rel, plan_abs = _stage_plan_dir(tmp_path)
    # Stage a real file that the fixture references, inside tmp_path
    (cwd / "pyproject.toml").write_text("# stub\n")
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    assert re.search(r"^- EXISTS: pyproject\.toml\s+\(.*pyproject\.toml.*\)$", r.stdout, re.M), (
        f"expected EXISTS line with inline ls output for pyproject.toml; stdout:\n{r.stdout}"
    )


def test_symlink_recorded_with_target_not_followed(tmp_path):
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    # Create a real target and a symlink to it, with a path that the fixture cites
    target = cwd / "real-pyproject.toml"
    target.write_text("# real\n")
    link = cwd / "pyproject.toml"
    link.symlink_to(target)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    # Must show SYMLINK prefix and the target; must NOT emit EXISTS for this path
    assert re.search(r"^- SYMLINK: pyproject\.toml -> .*real-pyproject\.toml", r.stdout, re.M), (
        f"expected SYMLINK line; stdout:\n{r.stdout}"
    )
    assert "- EXISTS: pyproject.toml " not in r.stdout, (
        f"symlink must not be reported as EXISTS:\n{r.stdout}"
    )


# --------------------------------------------------------------------------- #
# Cluster 4: SHA footer + determinism                                         #
# --------------------------------------------------------------------------- #

def test_attestation_payload_has_sha256_footer(tmp_path):
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    parsed = _parse_attestation(r.stdout)
    assert parsed["declared_sha"] is not None, f"missing sha256 footer:\n{r.stdout}"
    assert re.fullmatch(r"[0-9a-f]{64}", parsed["declared_sha"])


def test_attestation_sha_hashes_payload_not_plan_file(tmp_path):
    """SHA must be of the rendered payload, not the plan file bytes."""
    cwd, plan_rel, plan_abs = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    parsed = _parse_attestation(r.stdout)
    plan_sha = hashlib.sha256(plan_abs.read_bytes()).hexdigest()
    payload_sha = hashlib.sha256(parsed["payload"].encode()).hexdigest()
    assert parsed["declared_sha"] == payload_sha, (
        f"declared sha must match sha256(payload); declared={parsed['declared_sha']} "
        f"payload_sha={payload_sha} plan_sha={plan_sha}"
    )
    # Negative: declared sha should not accidentally equal the plan-file sha
    assert parsed["declared_sha"] != plan_sha


def test_attestation_sha_stable_for_identical_inputs(tmp_path):
    """Same plan, same fake-gh, same SOURCE_DATE_EPOCH, same repo HEAD → same sha."""
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    env = {"SOURCE_DATE_EPOCH": "1700000000"}
    r1 = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir, extra_env=env)
    r2 = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir, extra_env=env)
    p1 = _parse_attestation(r1.stdout)
    p2 = _parse_attestation(r2.stdout)
    assert p1["declared_sha"] == p2["declared_sha"], (
        f"sha must be stable for identical inputs; p1={p1['declared_sha']} p2={p2['declared_sha']}"
    )


def test_attestation_sha_changes_when_citations_change(tmp_path):
    """Changing attested content (add an issue citation) must change sha."""
    cwd, plan_rel, plan_abs = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    env = {"SOURCE_DATE_EPOCH": "1700000000"}
    r1 = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir, extra_env=env)
    # Add a new issue citation; this changes the extracted list → changes payload
    plan_abs.write_text(plan_abs.read_text() + "\n\nAlso see #2017.\n")
    # fake gh doesn't know about 2017 → will emit fallback line, still changes sha
    r2 = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir, extra_env=env)
    p1 = _parse_attestation(r1.stdout)
    p2 = _parse_attestation(r2.stdout)
    assert p1["declared_sha"] != p2["declared_sha"], (
        "sha must change when attestation content changes"
    )


# --------------------------------------------------------------------------- #
# Cluster 5: Budget caps (20 issues / 40 paths)                               #
# --------------------------------------------------------------------------- #

def test_caps_gh_calls_at_20_with_skipped_note(tmp_path):
    # Generate a plan with 25 unique 3-5 digit issue numbers
    issues = [f"#{n}" for n in range(10100, 10125)]
    plan_text = "# Cap test\n\n" + " ".join(issues) + "\n"
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path, fixture_text=plan_text)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    responses = {str(n): (f"- #{n} OPEN fake", 0) for n in range(10100, 10125)}
    _make_fake_gh(bin_dir, responses=responses)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    log = _read_gh_log(bin_dir)
    view_count = sum(1 for line in log if "view" in line)
    assert view_count == 20, f"gh must be capped at 20 invocations; got {view_count}"
    assert "budget exhausted" in r.stdout, (
        f"expected 'budget exhausted' skip-note when >20 issues cited; stdout:\n{r.stdout}"
    )
    assert "25" in r.stdout, "note should surface the full count of citations"


def test_caps_paths_at_40_with_skipped_note(tmp_path):
    # Generate a plan with 45 unique backticked paths with allowed extensions
    paths = [f"`f{i:03d}.md`" for i in range(45)]
    plan_text = "# Path cap test\n\nCites #2405.\n\n" + "\n".join(paths) + "\n"
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path, fixture_text=plan_text)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
    assert r.returncode == 0, r.stderr
    # Count how many "- MISSING: fNNN.md" lines appear (all paths are missing in tmp)
    missing_lines = re.findall(r"^- MISSING: f\d{3}\.md$", r.stdout, re.M)
    assert len(missing_lines) == 40, f"paths must be capped at 40; got {len(missing_lines)}"
    assert "budget exhausted" in r.stdout


# --------------------------------------------------------------------------- #
# Cluster 6: Security properties                                              #
# --------------------------------------------------------------------------- #

def test_no_shell_interpolation_from_plan_content(tmp_path):
    """Plan content with shell-metacharacter-looking paths must not execute."""
    plan_text = (
        "# Injection test\n\n"
        "Cites #2405.\n"
        "Bad try: `foo.md; touch /tmp/attest_pwned_plan`\n"
        "Valid: `legit.md`\n"
    )
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path, fixture_text=plan_text)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    marker = Path("/tmp/attest_pwned_plan")
    marker.unlink(missing_ok=True)
    try:
        r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir)
        assert r.returncode == 0, r.stderr
        assert not marker.exists(), "plan content executed as shell — injection!"
    finally:
        marker.unlink(missing_ok=True)


def test_allowlist_regex_matches_doc_plans_deliverable_wording():
    """The Deliverable text references a single allowlist regex; keep it wired to this test.
    If the plan's wording changes, update both the plan and this assertion."""
    plan_file = REPO_ROOT / "docs" / "plans" / "2026-04-20-issue-2405-cross-review-sandbox-repo-access.md"
    plan_text = plan_file.read_text()
    assert ALLOWLIST_REGEX in plan_text, (
        f"plan file must reference the single allowlist regex literal"
    )


# --------------------------------------------------------------------------- #
# Cluster 7: Runtime benchmark                                                #
# --------------------------------------------------------------------------- #

def test_attestation_runtime_under_5s_for_20_issues_40_paths(tmp_path):
    issues = [f"#{n}" for n in range(10200, 10220)]
    paths = [f"`b{i:03d}.md`" for i in range(40)]
    plan_text = "# Perf test\n\n" + " ".join(issues) + "\n\n" + "\n".join(paths) + "\n"
    cwd, plan_rel, _ = _stage_plan_dir(tmp_path, fixture_text=plan_text)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    responses = {str(n): (f"- #{n} OPEN fake", 0) for n in range(10200, 10220)}
    _make_fake_gh(bin_dir, responses=responses)
    start = time.monotonic()
    r = _run(plan_rel, cwd=cwd, fake_gh_bin=bin_dir, timeout=10)
    elapsed = time.monotonic() - start
    assert r.returncode == 0, r.stderr
    assert elapsed < 5.0, f"attestation took {elapsed:.2f}s — must be <5s for 20 issues + 40 paths"


# --------------------------------------------------------------------------- #
# Cluster 8: Dispatcher integration (submit-to-codex.sh + submit-to-gemini.sh) #
# --------------------------------------------------------------------------- #

SUBMIT_CODEX = REPO_ROOT / "scripts" / "review" / "submit-to-codex.sh"
SUBMIT_GEMINI = REPO_ROOT / "scripts" / "review" / "submit-to-gemini.sh"


def _make_fake_codex(bin_dir: Path, capture_path: Path) -> Path:
    """Fake codex that captures the prompt (argv[2] of 'codex exec PROMPT ...') and emits
    minimal valid structured JSON to --output-last-message so the dispatcher pipeline succeeds."""
    body = textwrap.dedent(f"""\
        #!/usr/bin/env bash
        # argv[1] expected = "exec"; argv[2] = prompt text
        prompt="${{2:-}}"
        printf '%s' "$prompt" > '{capture_path}'
        out=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            --output-last-message) out="${{2:-}}"; shift 2 ;;
            *) shift ;;
          esac
        done
        if [[ -n "$out" ]]; then
          printf '{{"verdict":"APPROVE","summary":"fake","issues_found":[],"suggestions":[],"questions_for_author":[]}}' > "$out"
        fi
        exit 0
        """)
    fake = bin_dir / "codex"
    fake.write_text(body)
    fake.chmod(0o755)
    return fake


def _make_fake_gemini(bin_dir: Path, capture_prompt: Path, capture_stdin: Path) -> Path:
    """Fake gemini that captures the -p PROMPT argv and the stdin INPUT_TEXT."""
    body = textwrap.dedent(f"""\
        #!/usr/bin/env bash
        cat > '{capture_stdin}'
        prompt=""
        while [[ $# -gt 0 ]]; do
          case "$1" in
            -p) prompt="${{2:-}}"; shift 2 ;;
            *) shift ;;
          esac
        done
        printf '%s' "$prompt" > '{capture_prompt}'
        printf '{{"verdict":"APPROVE","summary":"fake","issues_found":[],"suggestions":[],"questions_for_author":[]}}'
        """)
    fake = bin_dir / "gemini"
    fake.write_text(body)
    fake.chmod(0o755)
    return fake


def test_codex_dispatcher_embeds_attestation_for_plan_file(tmp_path):
    """submit-to-codex.sh must inject ## Attested Evidence when CONTENT_FILE is a plan."""
    cwd, plan_rel, plan_abs = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    capture = tmp_path / "codex_prompt.txt"
    fake_codex = _make_fake_codex(bin_dir, capture)
    env = os.environ.copy()
    env["PATH"] = str(bin_dir) + os.pathsep + env["PATH"]
    env["CODEX_BIN"] = str(fake_codex)
    env["REPO_ROOT"] = str(cwd)  # scope attestation relative-path resolution to tmp
    r = subprocess.run(
        ["bash", str(SUBMIT_CODEX), "--file", str(plan_abs), "--prompt", "Review this plan."],
        cwd=cwd, capture_output=True, text=True, env=env, timeout=60,
    )
    assert capture.exists(), (
        f"fake codex never ran — dispatcher exited {r.returncode}\n"
        f"stderr:\n{r.stderr}\nstdout:\n{r.stdout}"
    )
    prompt = capture.read_text()
    assert "## Attested Evidence" in prompt, (
        f"attestation block not injected; captured prompt:\n{prompt[:2000]}"
    )
    assert "Review this plan." in prompt, "original prompt lost"
    # Also: attestation must appear BEFORE the CONTENT TO REVIEW divider
    att_idx = prompt.find("## Attested Evidence")
    content_idx = prompt.find("CONTENT TO REVIEW")
    assert 0 <= att_idx < content_idx, (
        f"attestation must precede CONTENT divider; att={att_idx} content={content_idx}"
    )


def test_codex_dispatcher_no_attestation_for_non_plan_content(tmp_path):
    """Non-plan content files (e.g. commit diffs, random files) must not trigger attestation."""
    cwd, _, _ = _stage_plan_dir(tmp_path)  # sets up git repo at tmp
    nonplan = cwd / "notes.md"
    nonplan.write_text("# Random doc, not a plan\nMentions #2405 and `foo.md`.\n")
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    capture = tmp_path / "codex_prompt.txt"
    fake_codex = _make_fake_codex(bin_dir, capture)
    env = os.environ.copy()
    env["PATH"] = str(bin_dir) + os.pathsep + env["PATH"]
    env["CODEX_BIN"] = str(fake_codex)
    env["REPO_ROOT"] = str(cwd)
    r = subprocess.run(
        ["bash", str(SUBMIT_CODEX), "--file", str(nonplan), "--prompt", "Review."],
        cwd=cwd, capture_output=True, text=True, env=env, timeout=60,
    )
    assert capture.exists(), f"fake codex never ran; stderr:\n{r.stderr}"
    prompt = capture.read_text()
    assert "## Attested Evidence" not in prompt, (
        f"attestation must NOT be injected for non-plan content; prompt:\n{prompt[:2000]}"
    )


def test_gemini_dispatcher_embeds_attestation_for_plan_file(tmp_path):
    """submit-to-gemini.sh must inject ## Attested Evidence in the prompt argv (-p)."""
    cwd, plan_rel, plan_abs = _stage_plan_dir(tmp_path)
    bin_dir = tmp_path / "bin"; bin_dir.mkdir()
    _make_fake_gh(bin_dir)
    capture_prompt = tmp_path / "gemini_prompt.txt"
    capture_stdin = tmp_path / "gemini_stdin.txt"
    fake_gemini = _make_fake_gemini(bin_dir, capture_prompt, capture_stdin)
    env = os.environ.copy()
    env["PATH"] = str(bin_dir) + os.pathsep + env["PATH"]
    env["GEMINI_CMD"] = str(fake_gemini)
    env["REPO_ROOT"] = str(cwd)
    r = subprocess.run(
        ["bash", str(SUBMIT_GEMINI), "--file", str(plan_abs), "--prompt", "Review this plan."],
        cwd=cwd, capture_output=True, text=True, env=env, timeout=60,
    )
    assert capture_prompt.exists(), (
        f"fake gemini never ran — dispatcher exit {r.returncode}\n"
        f"stderr:\n{r.stderr}\nstdout:\n{r.stdout}"
    )
    prompt = capture_prompt.read_text()
    assert "## Attested Evidence" in prompt, (
        f"attestation not in prompt argv; got:\n{prompt[:2000]}"
    )
    assert "Review this plan." in prompt


# --------------------------------------------------------------------------- #
# Cluster 9: Static contract checks — prompt template + SKILL.md              #
# --------------------------------------------------------------------------- #

PROMPT_TEMPLATE = REPO_ROOT / "scripts" / "review" / "prompts" / "plan-review.md"
ISSUE_PLANNING_SKILL = REPO_ROOT / ".claude" / "skills" / "coordination" / "issue-planning-mode" / "SKILL.md"


def test_prompt_template_documents_attested_evidence_block():
    """Reviewers must be told to prefer the ## Attested Evidence block over plan text."""
    assert PROMPT_TEMPLATE.exists(), f"{PROMPT_TEMPLATE} missing"
    text = PROMPT_TEMPLATE.read_text()
    assert "## Attested Evidence" in text, (
        "plan-review prompt must reference the ## Attested Evidence block so reviewers know to trust it"
    )
    assert re.search(r"prefer.*attested|attested.*authoritat|rely on.*attestation", text, re.I), (
        "plan-review prompt must tell reviewers to prefer attested evidence over plan-asserted claims"
    )


def test_issue_planning_skill_documents_attestation_preference():
    """SKILL.md adversarial-stance contract must tell reviewers attestation > plan prose."""
    text = ISSUE_PLANNING_SKILL.read_text()
    assert "Attested Evidence" in text or "attest-plan-claims" in text, (
        "issue-planning-mode SKILL.md must document the attestation contract in the reviewer-stance section"
    )
