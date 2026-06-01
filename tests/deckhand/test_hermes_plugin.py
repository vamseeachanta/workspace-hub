import importlib.util
import json
import subprocess
import sys
import types
from pathlib import Path

import yaml


PLUGIN_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "deckhand"
    / "hermes-plugin"
    / "deckhand-scope"
    / "__init__.py"
)


def write_config(config_dir: Path) -> Path:
    config_dir.mkdir(parents=True)
    (config_dir / "policy.yml").write_text(
        yaml.safe_dump(
            {
                "destructive_ops": [
                    "repo_delete",
                    "branch_delete",
                    "tag_delete",
                    "release_delete",
                    "force_push",
                    "reset_hard",
                    "git_clean",
                ],
                "action_policy_defaults": {
                    "diff_risk_gate": {"enabled": True, "mass_deletion_file_threshold": 3}
                },
                "audit": {
                    "raw_store": {
                        "kind": "append_only_file",
                        "path": str(config_dir / "audit.ndjson"),
                    }
                },
                "kill_switches": {
                    "disable_all_writes": False,
                    "disabled_scopes": [],
                    "disabled_operators": [],
                    "disabled_platforms": [],
                },
                "elevation": {"approvers": ["internal-admin"]},
            }
        ),
        encoding="utf-8",
    )
    (config_dir / "scopes.yml").write_text(
        yaml.safe_dump(
            {
                "scopes": {
                    "acma": {
                        "sensitivity": "private",
                        "repositories": ["owner/acma"],
                        "operators": ["tg-100"],
                        "channel_repo_bindings": [],
                    },
                    "other": {
                        "sensitivity": "private",
                        "repositories": ["owner/other"],
                        "operators": ["tg-200"],
                        "channel_repo_bindings": [],
                    },
                },
                "origin_bound_default": {"enabled": False},
            }
        ),
        encoding="utf-8",
    )
    return config_dir


def install_session_shim(monkeypatch, env):
    gateway = types.ModuleType("gateway")
    session_context = types.ModuleType("gateway.session_context")

    def get_session_env(name, default=""):
        return env.get(name, default)

    session_context.get_session_env = get_session_env
    monkeypatch.setitem(sys.modules, "gateway", gateway)
    monkeypatch.setitem(sys.modules, "gateway.session_context", session_context)


def load_plugin(monkeypatch, tmp_path, env=None):
    install_session_shim(
        monkeypatch,
        env
        or {
            "HERMES_SESSION_USER_ID": "tg-100",
            "HERMES_SESSION_PLATFORM": "telegram",
            "HERMES_SESSION_CHAT_ID": "dm-100",
            "HERMES_SESSION_THREAD_ID": "thread-1",
        },
    )
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    module_name = f"deckhand_scope_plugin_{id(tmp_path)}"
    spec = importlib.util.spec_from_file_location(module_name, PLUGIN_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    module.CONFIG_DIR = write_config(tmp_path / "config")
    return module


def make_repo(tmp_path: Path, remote: str) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(
        ["git", "remote", "add", "origin", f"https://github.com/{remote}.git"],
        cwd=repo,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return repo


def test_scope_sets_state_for_authorized_operator_and_refuses_unauthorized(monkeypatch, tmp_path):
    plugin = load_plugin(monkeypatch, tmp_path)

    assert plugin.handle_scope("acma") == "active scope = acma (write, destructive denied)"
    state = json.loads(plugin._state_path(plugin._identity()).read_text(encoding="utf-8"))
    assert state["scope_name"] == "acma"
    assert state["operator_id"] == "tg-100"

    denied = plugin.handle_scope("other")
    assert "denied" in denied
    state_after = json.loads(plugin._state_path(plugin._identity()).read_text(encoding="utf-8"))
    assert state_after["scope_name"] == "acma"


def test_pre_tool_call_blocks_and_allows_by_scope(monkeypatch, tmp_path):
    plugin = load_plugin(monkeypatch, tmp_path)
    repo = make_repo(tmp_path, "owner/acma")

    assert plugin.on_pre_tool_call("terminal", {"command": "git push origin main", "workdir": str(repo)})[
        "action"
    ] == "block"

    plugin.handle_scope("acma")

    forced = plugin.on_pre_tool_call("terminal", {"command": "git push --force", "workdir": str(repo)})
    assert forced["action"] == "block"
    assert "destructive" in forced["message"] or "force" in forced["message"]

    outside_repo = make_repo(tmp_path / "outside", "owner/other")
    outside = plugin.on_pre_tool_call(
        "terminal",
        {"command": "git push origin main", "workdir": str(outside_repo)},
    )
    assert outside["action"] == "block"
    assert "outside scope" in outside["message"]

    allowed = plugin.on_pre_tool_call("terminal", {"command": "git commit -m ok", "workdir": str(repo)})
    assert allowed is None


def test_write_blocked_when_repo_unresolvable(monkeypatch, tmp_path):
    plugin = load_plugin(monkeypatch, tmp_path)
    plugin.handle_scope("acma")
    nonrepo = tmp_path / "plain"
    nonrepo.mkdir()
    out = plugin.on_pre_tool_call("terminal", {"command": "git commit -m x", "workdir": str(nonrepo)})
    assert out["action"] == "block"
    assert "resolve target repository" in out["message"]


def test_dm_binding_resolves_scope_without_scope_command(monkeypatch, tmp_path):
    plugin = load_plugin(monkeypatch, tmp_path)
    scopes_path = plugin.CONFIG_DIR / "scopes.yml"
    data = yaml.safe_load(scopes_path.read_text(encoding="utf-8"))
    data["scopes"]["acma"]["channel_repo_bindings"] = [
        {"platform": "telegram", "channel_id": "dm-100", "repo": "owner/acma"}
    ]
    scopes_path.write_text(yaml.safe_dump(data), encoding="utf-8")
    repo = make_repo(tmp_path, "owner/acma")

    # No /scope state set; the DM binding must resolve scope=acma and allow a write.
    assert plugin.on_pre_tool_call("terminal", {"command": "git commit -m ok", "workdir": str(repo)}) is None
    # Destructive still blocked even with the binding.
    forced = plugin.on_pre_tool_call("terminal", {"command": "git push --force", "workdir": str(repo)})
    assert forced["action"] == "block"


def test_report_mode_never_blocks(monkeypatch, tmp_path):
    plugin = load_plugin(monkeypatch, tmp_path)
    repo = make_repo(tmp_path, "owner/acma")
    monkeypatch.setenv("DECKHAND_ENFORCE", "report")

    assert plugin.on_pre_tool_call("terminal", {"command": "git push --force", "workdir": str(repo)}) is None


def test_execute_code_git_subprocess_is_blocked(monkeypatch, tmp_path):
    plugin = load_plugin(monkeypatch, tmp_path)

    blocked = plugin.on_pre_tool_call(
        "execute_code",
        {"code": 'import subprocess\nsubprocess.run(["git", "push"])'},
    )

    assert blocked["action"] == "block"
    assert "approved Deckhand path" in blocked["message"]
