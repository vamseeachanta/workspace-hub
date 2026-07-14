from __future__ import annotations

import base64
import importlib.util
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / "scripts/legal/manage_rule_authority.py"
sys.path.insert(0, str(ROOT / "scripts" / "legal"))
from rule_authority import authority, codec  # noqa: E402


def run(*args, env=None):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        text=True,
        capture_output=True,
        env=env,
    )


def _authority_fixture(tmp_path, pattern=b"forbidden-private"):
    registry = codec.parse_registry(
        (ROOT / "config/legal-rule-registry.json").read_bytes()
    )
    policy = codec.parse_policy(
        (ROOT / "config/legal-rule-authority-policy.json").read_bytes()
    )
    private_map = {
        "authority_revision": registry["authority_revision"],
        "generation": registry["generation"],
        "rules": [
            {
                "pattern_b64": base64.b64encode(pattern).decode(),
                "rule_id": registry["rules"][0]["rule_id"],
            }
        ],
        "schema_id": "legal-rule-map-v1",
    }
    key = bytes(range(32))
    manifest = authority.build_manifest(registry, policy, private_map, key)
    tool = "f" * 40
    anchor = authority.make_anchor(manifest, tool)
    ledger = authority.new_ledger("synthetic", manifest, key)
    directory = tmp_path / "authority"
    directory.mkdir(mode=0o700)
    for name, value in (
        ("map.json", private_map),
        ("manifest.json", manifest),
        ("anchor.json", anchor),
        ("ledger.json", ledger),
    ):
        (directory / name).write_bytes(codec.canonical_bytes(value))
    (directory / "key.b64").write_bytes(base64.b64encode(key) + b"\n")
    return directory, tool


def _git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, text=True, capture_output=True
    ).stdout.strip()


def test_cli_rc0_public_and_rc2_schema(tmp_path):
    valid = run(
        "validate-public",
        "--registry",
        ROOT / "config/legal-rule-registry.json",
        "--policy",
        ROOT / "config/legal-rule-authority-policy.json",
    )
    assert valid.returncode == 0 and "verdict=verified rc=0" in valid.stdout
    bad = tmp_path / "bad.json"
    bad.write_text("{}\n", encoding="utf-8")
    invalid = run(
        "validate-public",
        "--registry",
        bad,
        "--policy",
        ROOT / "config/legal-rule-authority-policy.json",
    )
    assert invalid.returncode == 2 and "verdict=schema rc=2" in invalid.stderr


def test_cli_rc4_filesystem_is_fixed_and_redacted(tmp_path):
    missing = tmp_path / "private-sensitive-name"
    result = run(
        "validate-public",
        "--registry",
        missing,
        "--policy",
        ROOT / "config/legal-rule-authority-policy.json",
    )
    assert (
        result.returncode == 4
        and result.stderr.strip() == "command=authority verdict=filesystem rc=4"
    )
    assert str(missing) not in result.stderr


def test_cli_exposes_frozen_phase_a_commands():
    result = run("--help")
    for command in (
        "validate-public",
        "seal",
        "verify",
        "audit-tree",
        "audit-history",
        "cleanup-incomplete",
        "materialize-envelope",
        "promote",
        "verify-protection",
    ):
        assert command in result.stdout


def test_exact_audit_tree_commands_cover_rc0_and_rc1_without_detail_leak(tmp_path):
    authority_dir, tool = _authority_fixture(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "synthetic@example.invalid")
    _git(repo, "config", "user.name", "Synthetic")
    (repo / "data.bin").write_bytes(b"clean")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "clean")
    out = tmp_path / "reports"
    out.mkdir(mode=0o700)

    def command(transaction):
        oid = _git(repo, "rev-parse", "HEAD")
        return run(
            "audit-tree",
            "--repo",
            repo / ".git",
            "--commit",
            oid,
            "--required-ref",
            "refs/heads/main",
            "--registry",
            ROOT / "config/legal-rule-registry.json",
            "--policy",
            ROOT / "config/legal-rule-authority-policy.json",
            "--authority-dir",
            authority_dir,
            "--out-dir",
            out,
            "--transaction-id",
            transaction,
            "--tool-sha",
            tool,
        )

    clean = command(str(uuid.uuid4()))
    assert clean.returncode == 0 and "verdict=clean rc=0" in clean.stdout
    (repo / "data.bin").write_bytes(b"forbidden-private")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "finding")
    finding = command(str(uuid.uuid4()))
    assert finding.returncode == 1 and "verdict=finding rc=1" in finding.stdout
    assert "forbidden-private" not in finding.stdout + finding.stderr
    (repo / "data.bin").write_bytes(b"legal-rule-map-v1")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "structural")
    structural = command(str(uuid.uuid4()))
    assert structural.returncode == 1 and "verdict=finding rc=1" in structural.stdout


def test_exact_audit_history_command_is_fail_closed_rc3_for_residual(tmp_path):
    authority_dir, _tool = _authority_fixture(tmp_path)
    out = tmp_path / "reports"
    out.mkdir(mode=0o700)
    env = {**os.environ, "REMOTE": "file:///not-authorized", "TOKEN": "synthetic"}
    result = run(
        "audit-history",
        "--remote-url-env",
        "REMOTE",
        "--github-repo",
        "owner/repo",
        "--authority-dir",
        authority_dir,
        "--mirror-dir",
        tmp_path / "mirror.git",
        "--out-dir",
        out,
        "--github-token-env",
        "TOKEN",
        "--transaction-id",
        str(uuid.uuid4()),
        "--registry",
        ROOT / "config/legal-rule-registry.json",
        "--policy",
        ROOT / "config/legal-rule-authority-policy.json",
        env=env,
    )
    assert result.returncode == 3
    assert result.stderr.strip() == "command=authority verdict=integrity rc=3"
    assert "file:///" not in result.stdout + result.stderr


def test_exact_verify_and_seal_commands_succeed_with_synthetic_authority(tmp_path):
    authority_dir, tool = _authority_fixture(tmp_path)
    verified = run(
        "verify",
        "--registry",
        ROOT / "config/legal-rule-registry.json",
        "--policy",
        ROOT / "config/legal-rule-authority-policy.json",
        "--map",
        authority_dir / "map.json",
        "--manifest",
        authority_dir / "manifest.json",
        "--anchor",
        authority_dir / "anchor.json",
        "--ledger",
        authority_dir / "ledger.json",
        "--key-file",
        authority_dir / "key.b64",
        "--tool-sha",
        tool,
    )
    assert verified.returncode == 0 and "verdict=verified rc=0" in verified.stdout

    registry = json.loads((ROOT / "config/legal-rule-registry.json").read_text())
    policy = json.loads((ROOT / "config/legal-rule-authority-policy.json").read_text())
    revision = "87654321-4321-4321-8321-cba987654321"
    for value in (registry, policy):
        value["generation"] = 2
        value["authority_revision"] = revision
    mapped = json.loads((authority_dir / "map.json").read_text())
    mapped["generation"] = 2
    mapped["authority_revision"] = revision
    public = tmp_path / "next"
    public.mkdir()
    for name, value in (
        ("registry.json", registry),
        ("policy.json", policy),
        ("map.json", mapped),
    ):
        (public / name).write_bytes(codec.canonical_bytes(value))
    output = tmp_path / "sealed"
    output.mkdir(mode=0o700)
    sealed = run(
        "seal",
        "--registry",
        public / "registry.json",
        "--policy",
        public / "policy.json",
        "--map",
        public / "map.json",
        "--key-file",
        authority_dir / "key.b64",
        "--current-anchor",
        authority_dir / "anchor.json",
        "--ledger",
        authority_dir / "ledger.json",
        "--out-dir",
        output,
    )
    assert sealed.returncode == 0 and "verdict=sealed rc=0" in sealed.stdout
    assert (output / "authority-manifest.json").is_file()


def test_filesystem_failure_has_rc4_precedence_over_private_finding(
    monkeypatch, capsys
):
    spec = importlib.util.spec_from_file_location("manage_rule_authority_test", CLI)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest = {"generation": 1, "authority_revision": "opaque"}
    monkeypatch.setattr(
        module,
        "_authority_dir",
        lambda _args: ({}, {"limits": {}}, manifest, b"k" * 32, []),
    )
    monkeypatch.setattr(
        module.audit,
        "audit_tree",
        lambda *_args: {
            "coverage": "complete",
            "findings": 1,
            "warnings": 0,
            "objects_examined": 1,
        },
    )
    monkeypatch.setattr(
        module.private_io,
        "write_complete_transaction",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            codec.AuthorityError("filesystem")
        ),
    )
    rc = module.main(
        [
            "audit-tree",
            "--repo",
            "opaque",
            "--commit",
            "a" * 40,
            "--required-ref",
            "refs/heads/main",
            "--registry",
            "opaque",
            "--policy",
            "opaque",
            "--authority-dir",
            "opaque",
            "--out-dir",
            "opaque",
            "--transaction-id",
            str(uuid.uuid4()),
            "--tool-sha",
            "b" * 40,
        ]
    )
    captured = capsys.readouterr()
    assert (
        rc == 4 and captured.err.strip() == "command=authority verdict=filesystem rc=4"
    )
    assert captured.out == ""
