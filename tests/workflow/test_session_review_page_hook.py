"""Tests for the #3316 SessionEnd session-review-page hook.

Behavioural + safety tests (fail-open). The generation path itself is covered by
the #3311 --from-git tests; here we assert the hook never blocks a session and
respects its guards. Registration in .claude/settings.json is a deliberate
user-approved activation step (documented in SESSION-GOVERNANCE.md), so it is
NOT asserted here.
"""
import os
import stat
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "session-review-page.sh"


def _run(args, env_extra):
    env = {**os.environ, **env_extra}
    return subprocess.run(["bash", str(HOOK), *args], env=env,
                          capture_output=True, text=True, timeout=30)


def test_hook_exists_and_is_executable():
    assert HOOK.exists()
    assert HOOK.stat().st_mode & stat.S_IXUSR, "hook must be executable"


def test_disabled_switch_exits_clean():
    r = _run(["emit"], {"SESSION_REVIEW_PAGE": "false"})
    assert r.returncode == 0
    assert "[session-review]" not in r.stderr


def test_emit_fails_open_outside_a_repo(tmp_path):
    r = _run(["emit"], {"WORKSPACE_HUB": str(tmp_path)})  # no .git → nothing to do
    assert r.returncode == 0


def test_start_fails_open_outside_a_repo(tmp_path):
    r = _run(["start"], {"WORKSPACE_HUB": str(tmp_path)})
    assert r.returncode == 0


def test_unknown_mode_exits_clean(tmp_path):
    r = _run(["bogus"], {"WORKSPACE_HUB": str(tmp_path)})
    assert r.returncode == 0


def test_does_not_commit_or_push_by_default():
    # the default path must never invoke a committing/pushing git verb
    import re
    body = HOOK.read_text(encoding="utf-8")
    # assert no actual git push/commit INVOCATION (the words may appear in notify
    # strings/comments, which are fine — only a real git verb is disallowed)
    git_verb = re.compile(r"\bgit\b[^#\n]*\b(push|commit)\b")
    for line in body.splitlines():
        code = line.split("#", 1)[0]
        assert not git_verb.search(code), f"hook must not run git push/commit: {line.strip()}"


def test_activation_is_documented():
    gov = (REPO / "docs" / "governance" / "SESSION-GOVERNANCE.md").read_text(encoding="utf-8")
    assert "session-review-page.sh" in gov
    assert "SessionEnd" in gov
