import pytest

from src.deckhand.hook import classify_command, inspect, scan_python_source


def config():
    return {
        "policy": {
            "destructive_ops": [
                "repo_delete",
                "branch_delete",
                "tag_delete",
                "release_delete",
                "force_push",
                "reset_hard",
                "git_clean",
            ],
            "action_policy_defaults": {"diff_risk_gate": {"enabled": True, "mass_deletion_file_threshold": 3}},
            "kill_switches": {
                "disable_all_writes": False,
                "disabled_scopes": [],
                "disabled_operators": [],
                "disabled_platforms": [],
            },
            "elevation": {"approvers": ["internal-admin"]},
        },
        "scopes": {
            "scopes": {
                "acma": {
                    "sensitivity": "private",
                    "repositories": ["owner/acma"],
                    "operators": ["tg-100"],
                    "channel_repo_bindings": [],
                }
            },
            "origin_bound_default": {"enabled": False},
        },
    }


def context(**overrides):
    base = {
        "operator_id": "tg-100",
        "platform": "telegram",
        "scope_name": "acma",
        "repo": "owner/acma",
        "origin": {"is_dm": True, "channel_id": "dm-100"},
    }
    base.update(overrides)
    return base


def action_classes(command):
    return [action.action_class for action in classify_command(command)]


def assert_denied(command):
    outcome = inspect(command, cwd="/work", request_context=context(), config=config())

    assert outcome["allow"] is False
    assert outcome["actions"]
    return outcome


def test_classifies_destructive_git_and_gh_commands():
    cases = {
        "git push --force": "force_push",
        "git push --force-with-lease": "force_push",
        "git push -f": "force_push",
        "git push origin --delete stale": "branch_delete",
        "git branch -D stale": "branch_delete",
        "git branch -d stale": "branch_delete",
        "git tag -d v1.0.0": "tag_delete",
        "git push origin --delete v1.0.0": "tag_delete",
        "git push origin --delete refs/tags/v1.0.0": "tag_delete",
        "git reset --hard HEAD~1": "reset_hard",
        "git clean -fdx": "git_clean",
        "gh repo delete owner/acma": "repo_delete",
        "gh release delete v1.0.0": "release_delete",
    }

    for command, expected in cases.items():
        assert action_classes(command) == [expected]


def test_classifies_git_branch_list_as_read_and_branch_create_as_write():
    assert action_classes("git branch") == ["read"]
    assert action_classes("git branch --list feature/*") == ["read"]
    assert action_classes("git branch feature/new") == ["write"]


def test_inspect_blocks_destructive_commands_via_engine():
    for command in [
        "git push --force",
        "git branch -D stale",
        "git reset --hard HEAD~1",
        "git clean -fdx",
        "gh repo delete owner/acma",
    ]:
        outcome = inspect(command, cwd="/work", request_context=context(), config=config())

        assert outcome["allow"] is False
        assert outcome["actions"][0]["action_class"] in {
            "force_push",
            "branch_delete",
            "reset_hard",
            "git_clean",
            "repo_delete",
        }
        assert outcome["decisions"][0]["reason"] == "destructive action denied"


def test_inspect_allows_normal_write_commands_to_allowlisted_repo():
    for command in ["git commit -m ok", "git push origin main"]:
        outcome = inspect(command, cwd="/work", request_context=context(), config=config())

        assert outcome["allow"] is True
        assert outcome["reason"] == "allowed"
        assert outcome["decisions"][0]["allow"] is True


def test_inspect_blocks_repo_outside_allowlist():
    outcome = inspect(
        "git push origin main",
        cwd="/work",
        request_context=context(repo="owner/outside"),
        config=config(),
    )

    assert outcome["allow"] is False
    assert outcome["decisions"][0]["reason"] == "repo outside scope allowlist"


def test_compound_command_detects_later_force_push_and_blocks():
    outcome = inspect("git status && git push --force", cwd="/work", request_context=context(), config=config())

    assert [action["action_class"] for action in outcome["actions"]] == ["read", "force_push"]
    assert outcome["allow"] is False
    assert outcome["decisions"][1]["reason"] == "destructive action denied"


def test_prefixes_and_absolute_git_path_are_detected_and_blocked():
    for command in ["GIT_SSH=x git push -f", "sudo -u root git push -f"]:
        outcome = inspect(command, cwd="/work", request_context=context(), config=config())

        assert outcome["allow"] is False
        assert outcome["actions"][0]["action_class"] == "force_push"

    outcome = inspect("/usr/bin/git push -f", cwd="/work", request_context=context(), config=config())
    assert outcome["allow"] is False
    assert outcome["actions"][0]["action_class"] == "unparseable_suspicious"


def test_unparseable_or_suspicious_git_shell_forms_fail_closed():
    for command in ['eval "$(echo git push --force)"', 'echo "$(git status)"', "alias g=git; g push -f"]:
        outcome = inspect(command, cwd="/work", request_context=context(), config=config())

        assert outcome["allow"] is False
        assert outcome["actions"][0]["action_class"] == "unparseable_suspicious"
        assert "fail-closed" in outcome["reason"]


def test_non_git_command_allows_pass_through_without_engine_decision():
    outcome = inspect("ls -la", cwd="/work", request_context=context(), config=config())

    assert outcome == {"allow": True, "reason": "no git/gh action detected", "actions": [], "decisions": []}


def test_scan_python_source_detects_git_subprocess_patterns():
    assert scan_python_source('import subprocess\nsubprocess.run(["git", "push"])') is True
    assert scan_python_source("print(1)") is False


@pytest.mark.parametrize(
    "src",
    [
        "from hermes_tools import terminal\nr=terminal('command -v git', workdir='/tmp')",
        "import hermes_tools; hermes_tools.terminal('git status')",
        "__import__('hermes_tools')",
        "getattr(__import__('hermes_tools'), 'terminal')('git status')",
    ],
)
def test_scan_python_source_detects_hermes_tool_reentry(src):
    assert scan_python_source(src) is True


@pytest.mark.parametrize(
    "src",
    [
        "print(1)",
        "x = (2 + 3) * 5\nprint(x)",
    ],
)
def test_scan_python_source_allows_benign_scripts(src):
    assert scan_python_source(src) is False


@pytest.mark.parametrize(
    "command",
    [
        "git push $F origin main",
        "git push ${F} origin main",
        "git p${X}ush --force",
        "$GIT push --force",
        "${GIT} push --force",
        "${G:-git} push --force",
        "g${X}it push --force",
        "git push --\\\nforce",
        "git pu\\\nsh --force",
        "git status\ngit push --force",
        "git status & git push --force",
        "git status \\\n& git push --force",
        "git-push --force origin main",
        "g push --force",
        "git -c alias.nuke='push --force' nuke origin main",
        "git -c alias.wipe='branch -D main' wipe",
        "git.exe push --force",
        "gh-api -X DELETE /repos/o/r",
        "Git push --force",
        "git() { git push --force; }; git origin main",
        "./git push --force",
        "/tmp/git push --force",
    ],
)
def test_confirmed_shell_expansion_wrapper_and_alias_bypasses_fail_closed(command):
    outcome = assert_denied(command)

    assert outcome["actions"][0]["action_class"] == "unparseable_suspicious"
    assert "fail-closed" in outcome["reason"]


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("git push origin :old", "branch_delete"),
        ("git push origin :refs/heads/old", "branch_delete"),
        ("git push origin +main:main", "force_push"),
        ("git push --atomic origin :old +main:main", {"branch_delete", "force_push"}),
        ("git push --mirror origin", "destructive"),
        ("git push --prune origin main", "destructive"),
        ("git update-ref -d refs/heads/main", "destructive"),
        ("git branch -m main old", "destructive"),
        ("git branch --move main old", "destructive"),
        ("git branch --copy main old", "destructive"),
        ("git stash clear", "destructive"),
        ("git stash drop", "destructive"),
        ("git reflog delete HEAD@{0}", {"destructive", "unparseable_suspicious"}),
        ("git filter-branch --force HEAD", "destructive"),
        ("git rebase -i HEAD~3", "destructive"),
        ("git gc --prune=now", "destructive"),
        ("git maintenance run --task=gc", "destructive"),
        ("git worktree remove --force ../wt", "destructive"),
        ("git remote remove origin", "destructive"),
        ("git remote rm origin", "destructive"),
        ("git submodule deinit -f vendor/x", "destructive"),
        ("git checkout -- .", "destructive"),
        ("git restore .", "destructive"),
        ("git switch other", "destructive"),
        ("git rm -r .", "destructive"),
        ("git mv a b", "destructive"),
        ("git notes remove HEAD", "destructive"),
        ("git notes prune", "destructive"),
        ("git replace -d abc", "destructive"),
        ("git merge --abort", "destructive"),
        ("git rebase --abort", "destructive"),
    ],
)
def test_confirmed_git_destructive_bypasses_are_classified_and_denied(command, expected):
    outcome = assert_denied(command)
    classes = {action["action_class"] for action in outcome["actions"]}

    if isinstance(expected, set):
        assert classes & expected
    else:
        assert expected in classes


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("gh api repos/o/r/git/refs/heads/main -X DELETE", "destructive"),
        ("gh api --method DELETE /repos/o/r/releases/assets/1", "destructive"),
        ("gh api -X PATCH /repos/o/r --field archived=true", "destructive"),
        ("hub api repos/o/r -X DELETE", "destructive"),
        ("gh alias set wipe 'api -X DELETE /repos/o/r'", "destructive"),
        ("gh release delete-asset v1.0.0 asset.zip", "release_delete"),
        ("gh repo archive owner/repo", "repo_delete"),
        ("gh repo edit owner/repo --visibility public", "repo_delete"),
        ("gh repo rename newname", "repo_delete"),
        ("gh repo transfer owner/repo someone", "repo_delete"),
        ("gh repo deploy-key delete 1", "destructive"),
        ("gh secret delete TOKEN", "destructive"),
        ("gh ssh-key delete abc", "destructive"),
        ("gh pr close 1", "destructive"),
        ("gh issue close 1", "destructive"),
        ("gh cache delete 1", "destructive"),
        ("gh ruleset delete 1", "destructive"),
        ("gh run delete 1", "destructive"),
        ("gh workflow disable ci.yml", "destructive"),
        ("gh variable delete NAME", "destructive"),
        ("gh label delete bug", "destructive"),
        ("gh auth refresh -h github.com -s delete_repo", "destructive"),
        ("gh auth logout", "destructive"),
        ("hub delete owner/repo", "repo_delete"),
    ],
)
def test_confirmed_gh_and_hub_destructive_bypasses_are_classified_and_denied(command, expected):
    outcome = assert_denied(command)

    assert outcome["actions"][0]["action_class"] == expected


@pytest.mark.parametrize(
    "src",
    [
        "from subprocess import Popen\nPopen(('git','push','--force'))",
        "import os as o\no.system('git push --force')",
        "from os import system\nsystem('git push --force')",
        "from os import popen\npopen('git push --force')",
        "runner = __import__('subprocess').Popen\nrunner(('git','push','--force'))",
        "getattr(__import__('subprocess'), 'run')(['g' + 'it','push','--force'])",
        "cmd = 'git ' + 'push --force'\nsubprocess.run(cmd, shell=True)",
        "cmd = ['g'+'it','push','--force']\nsubprocess.run(cmd)",
        "def broken(:\n    pass",
    ],
)
def test_confirmed_python_source_scan_bypasses_are_gated(src):
    assert scan_python_source(src) is True
