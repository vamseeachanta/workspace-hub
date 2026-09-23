"""Tests for the pre-push installer extension point — workspace-hub#3781.

TDD: written before implementation.

Background: `install-hooks.sh` wired enforcement blocks with `cat >> pre-push`,
but the hook ends in an unconditional `exit`, so every appended block was
unreachable. Its idempotence check greps for a *string* rather than checking
*reachability*, so the installer reported "already wired" forever and could
never repair the damage it caused.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SCRIPT = REPO_ROOT / "scripts" / "hooks" / "pre-push.sh"
INSTALLER = REPO_ROOT / "scripts" / "enforcement" / "install-hooks.sh"
SENTINEL = "<<INSTALL_HOOKS_EXTENSION_POINT>>"

# Directories whose scripts are enforcement gates. Matching on these rather than
# on a `require-*` filename prefix is deliberate: the two gates that were dead
# for months -- check-state-file-size-prepush.sh and sync-cadence-helper.sh --
# carry neither that prefix nor that directory, so a prefix-based guard would
# have missed the exact defect it exists to catch.
GATE_DIRS = ("scripts/enforcement/", "scripts/sync/", ".claude/hooks/")


def _body_after_final_exit(text: str) -> str:
    """Return everything after the last top-level unconditional `exit`.

    "Top-level" means column zero: an `exit` indented inside an if/case/function
    is conditional and is not the script terminator.
    """
    matches = list(re.finditer(r"(?m)^exit\b.*$", text))
    if not matches:
        return ""
    return text[matches[-1].end():]


class TestReachability:
    """No enforcement may live below the hook's terminal exit."""

    def test_no_enforcement_block_below_final_exit(self):
        text = HOOK_SCRIPT.read_text()
        tail = _body_after_final_exit(text)

        offenders = []
        for line in tail.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue
            if any(d in line for d in GATE_DIRS) or "enforcement-env" in line:
                offenders.append(stripped)

        assert not offenders, (
            "enforcement below the terminal exit never runs (#3781):\n  "
            + "\n  ".join(offenders)
        )

    def test_hook_declares_an_extension_point(self):
        assert SENTINEL in HOOK_SCRIPT.read_text(), (
            "the hook must carry an explicit insertion marker so the installer "
            "never has to append blindly"
        )

    def test_extension_point_precedes_the_final_exit(self):
        text = HOOK_SCRIPT.read_text()
        assert SENTINEL not in _body_after_final_exit(text), (
            "the extension point itself sits below the exit — anything inserted "
            "at it would be unreachable"
        )


class TestOrdering:
    """enforcement-env must precede the gates whose behaviour it sets."""

    def test_enforcement_env_precedes_review_gate(self):
        text = HOOK_SCRIPT.read_text()
        env_at = text.find("enforcement-env")
        review_at = text.find("require-review-on-push.sh")
        assert env_at != -1, "enforcement-env is not wired into the hook"
        assert review_at != -1, "review gate is not wired into the hook"
        assert env_at < review_at, (
            "enforcement-env exports REVIEW_GATE_STRICT=1; the review wrapper "
            "defaults it to 0. Sourcing it after the wrapper leaves the review "
            "gate advisory — the #3781 defect."
        )


class TestStdinReplay:
    """Gates that read git's pre-push stdin must actually receive it."""

    def test_state_size_guard_receives_the_pushed_refs(self):
        """The hook consumes stdin into PUSH_LINES before any gate runs.

        `check-state-file-size-prepush.sh` reads ref lines from its own stdin and
        silently falls back to an inferred ref when none arrive — so a gate that
        merely *executes* can still be scanning the wrong commit range. The
        buffered lines must be replayed into it.
        """
        text = HOOK_SCRIPT.read_text()
        idx = text.find("check-state-file-size-prepush.sh")
        assert idx != -1, "state-size guard is not wired into the hook"

        block = text[max(0, idx - 400): idx + 400]
        assert "PUSH_LINES" in block, (
            "state-size guard invoked without replaying ${PUSH_LINES[@]} into "
            "its stdin — it will scan an inferred ref, not the pushed range"
        )


def _make_repo(tmp_path: Path, sentinel: bool, stale_block: bool = False) -> Path:
    """Build a throwaway repo with a pre-push hook in a chosen state."""
    repo = tmp_path / "repo"
    hooks = repo / ".git" / "hooks"
    scripts = repo / "scripts" / "enforcement"
    hooks.mkdir(parents=True)
    scripts.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

    for name in (
        "enforcement-env.sh",
        "require-stage-prompt-drift.sh",
        "require-review-on-push.sh",
    ):
        src = REPO_ROOT / "scripts" / "enforcement" / name
        if src.exists():
            shutil.copy2(src, scripts / name)

    body = "#!/usr/bin/env bash\nset -euo pipefail\nOVERALL_EXIT=0\n"
    if sentinel:
        body += f"# {SENTINEL}\n\nexit 0\n"
    else:
        body += "exit 0\n"
    if stale_block:
        # Reproduce the real #3781 state: the hook DOES carry an extension point
        # (post-#3782), and a block sits below the terminal exit anyway. An
        # earlier version of this fixture omitted the sentinel, which tested the
        # refusal path instead of the repair path.
        body += (
            "\n# ── Enforcement environment ──\n"
            'ENFORCEMENT_ENV="${REPO_ROOT}/.git/hooks/enforcement-env"\n'
            'if [[ -f "${ENFORCEMENT_ENV}" ]]; then source "${ENFORCEMENT_ENV}"; fi\n'
        )

    (hooks / "pre-push").write_text(body)
    (hooks / "pre-commit").write_text("#!/usr/bin/env bash\nexit 0\n")
    (hooks / "post-commit").write_text("#!/usr/bin/env bash\nexit 0\n")
    return repo


def _run_installer(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(INSTALLER)], cwd=repo, capture_output=True, text=True
    )


class TestInstaller:
    """The installer must insert at the marker, never append past the end."""

    def test_refuses_without_sentinel(self, tmp_path):
        repo = _make_repo(tmp_path, sentinel=False)
        hook = repo / ".git" / "hooks" / "pre-push"
        before = hook.read_text()

        result = _run_installer(repo)

        assert result.returncode != 0, (
            "installing into a hook with no extension point must fail loudly — "
            "appending blindly is what created #3781"
        )
        assert hook.read_text() == before, "hook must be left untouched on refusal"

    def test_idempotent_when_already_reachable(self, tmp_path):
        repo = _make_repo(tmp_path, sentinel=True)
        hook = repo / ".git" / "hooks" / "pre-push"

        assert _run_installer(repo).returncode == 0
        once = hook.read_text()
        assert _run_installer(repo).returncode == 0
        twice = hook.read_text()

        assert once == twice, "second install must be a no-op"
        assert once.count("ENFORCEMENT_ENV=") <= 1, "block inserted twice"

    def test_rewires_an_unreachable_block(self, tmp_path):
        """Given the #3781 state, the installer must repair it — not report OK.

        A string-presence idempotence check reports 'already wired' here, which
        is why the broken state was permanent.
        """
        repo = _make_repo(tmp_path, sentinel=True, stale_block=True)
        hook = repo / ".git" / "hooks" / "pre-push"

        result = _run_installer(repo)
        assert result.returncode == 0, result.stderr

        text = hook.read_text()
        tail = _body_after_final_exit(text)
        assert "enforcement-env" not in tail, (
            "the unreachable block was left below the exit — the installer "
            "detected a string, not a reachable block"
        )
