import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

from deckhand import shim_resolve


def write_scopes(path: Path) -> Path:
    path.parent.mkdir(parents=True)
    path.write_text(
        yaml.safe_dump(
            {
                "scopes": {
                    "acma": {
                        "pat_env": "DECKHAND_PAT_ACMA",
                        "operators": ["tg-100"],
                        "channel_repo_bindings": [
                            {"platform": "telegram", "channel_id": "dm-100", "repo": "owner/acma"}
                        ],
                    },
                    "doris": {
                        "pat_env": "DECKHAND_PAT_DORIS",
                        "operators": ["tg-100"],
                        "channel_repo_bindings": [],
                    },
                    "other": {
                        "pat_env": "DECKHAND_PAT_OTHER",
                        "operators": ["tg-200"],
                        "channel_repo_bindings": [
                            {"platform": "telegram", "channel_id": "dm-100", "repo": "owner/other"}
                        ],
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    return path


def identity_env() -> dict[str, str]:
    return {
        "HERMES_SESSION_USER_ID": "tg-100",
        "HERMES_SESSION_PLATFORM": "telegram",
        "HERMES_SESSION_CHAT_ID": "dm-100",
        "HERMES_SESSION_THREAD_ID": "thread-1",
    }


def write_state(home: Path, *, scope_name: str = "acma", operator_id: str = "tg-100") -> None:
    path = (
        home
        / ".hermes"
        / "deckhand"
        / "active-scope"
        / "telegram"
        / "dm-100"
        / f"{operator_id}.json"
    )
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "platform": "telegram",
                "chat_id": "dm-100",
                "thread_id": "thread-1",
                "operator_id": operator_id,
                "scope_name": scope_name,
            }
        ),
        encoding="utf-8",
    )


def test_resolves_state_scope_pat_env(tmp_path):
    config = write_scopes(tmp_path / "config" / "scopes.yml")
    home = tmp_path / "home"
    write_state(home)

    assert shim_resolve.resolve_pat_env(env=identity_env(), config_path=config, home=home) == "DECKHAND_PAT_ACMA"


def test_state_precedes_channel_binding(tmp_path):
    config = write_scopes(tmp_path / "config" / "scopes.yml")
    home = tmp_path / "home"
    write_state(home, scope_name="doris", operator_id="tg-100")

    assert shim_resolve.resolve_pat_env(env=identity_env(), config_path=config, home=home) == "DECKHAND_PAT_DORIS"


def test_unauthorized_state_falls_back_to_authorized_binding(tmp_path):
    config = write_scopes(tmp_path / "config" / "scopes.yml")
    home = tmp_path / "home"
    write_state(home, scope_name="other", operator_id="tg-100")

    assert shim_resolve.resolve_pat_env(env=identity_env(), config_path=config, home=home) == "DECKHAND_PAT_ACMA"


def test_binding_scope_resolves_when_state_missing(tmp_path):
    config = write_scopes(tmp_path / "config" / "scopes.yml")

    assert (
        shim_resolve.resolve_pat_env(env=identity_env(), config_path=config, home=tmp_path / "home")
        == "DECKHAND_PAT_ACMA"
    )


def test_missing_identity_returns_none(tmp_path):
    config = write_scopes(tmp_path / "config" / "scopes.yml")

    assert shim_resolve.resolve_pat_env(env={}, config_path=config, home=tmp_path / "home") is None


def test_cli_prints_name_only_and_exit_3_without_scope(monkeypatch, tmp_path):
    config = write_scopes(tmp_path / "config" / "scopes.yml")
    env = os.environ.copy()
    env.update(identity_env())
    env["DECKHAND_SCOPES_CONFIG"] = str(config)
    env["HOME"] = str(tmp_path / "home")
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[2] / "src")

    ok = subprocess.run(
        [sys.executable, "-m", "deckhand.shim_resolve"],
        check=False,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert ok.returncode == 0
    assert ok.stdout == "DECKHAND_PAT_ACMA\n"
    assert "token" not in ok.stdout.lower()
    assert ok.stderr == ""

    env["HERMES_SESSION_CHAT_ID"] = "unknown"
    missing = subprocess.run(
        [sys.executable, "-m", "deckhand.shim_resolve"],
        check=False,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert missing.returncode == 3
    assert missing.stdout == ""
