#!/usr/bin/env python3
"""One explicitly authorized Windows pilot; no unattended installation or fleet rollout."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import subprocess

from claude_native_probe import (guard_controls, project_state, protected_admission_state,
                                protected_state, run_probe, sha, write_json)
from claude_runtime_state import REQUIRED_CHECKS, provider_environment, provider_version
from claude_runtime_transaction import Transaction
from claude_native_restore import recovery_reference

CANONICAL_TOKEN = "feedback_edit_tool_freshness_window_after_writes"
REPOSITORY_TOKEN = "docs/standards/MODEL_RELEASE_READINESS_CONTRACT.md"


def check_auth(cli):
    forbidden = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
                 "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
                 "CLAUDE_CONFIG_DIR")
    if any(os.environ.get(key) for key in forbidden):
        raise ValueError("Provider override environment is not authorized")
    result = subprocess.run([str(cli), "auth", "status", "--json"],
                            capture_output=True, text=True, timeout=15, check=True)
    auth = json.loads(result.stdout)
    if (not auth.get("loggedIn") or auth.get("authMethod") != "claude.ai"
            or auth.get("apiProvider") != "firstParty" or auth.get("subscriptionType") != "max"):
        raise ValueError("Existing subscription authentication required; no credential changes")


def suppressors(cwd, home):
    allowed_global = home / ".claude/CLAUDE.md"
    for parent in dict.fromkeys((cwd, *cwd.parents, home, *home.parents)):
        for name in ("CLAUDE.md", "CLAUDE.local.md", ".claude/CLAUDE.md"):
            path = parent / name
            if path != allowed_global and os.path.lexists(path):
                raise ValueError("Ancestor instruction suppressor; no migration")
    if os.path.lexists(home / ".claude/CLAUDE.local.md"):
        raise ValueError("Unexpected user-level local instructions; preserve and stop")


def make_fixtures(output):
    fixture = output / "fixture"
    nested = fixture / "nested"
    nested.mkdir(parents=True)
    cases = []
    for name, directory in (("root", fixture), ("nested", nested)):
        token = name + "_" + secrets.token_hex(16)
        with (directory / "AGENTS.md").open("x", encoding="utf-8") as stream:
            stream.write("For deployment_probe, project_token is " + token + ".\n")
        cases.append((name, directory, token))
    return cases


def check_preservation(home, expected, output, name):
    actual = protected_state(home)
    write_json(output / (name + ".protected.json"), actual)
    if actual != expected:
        raise ValueError("Protected state changed; preserved for investigation")


def trials(cli, cases, output, prefix, token, home, baseline, repeats=1, global_mode="canary"):
    records = []
    for name, cwd, project_token in cases:
        for number in range(repeats):
            label = prefix + "-" + name + "-" + str(number)
            for _, directory, _ in cases:
                suppressors(directory, home)
            check_preservation(home, baseline, output, label + "-before")
            verdict = run_probe(cli, cwd, output, label, token, project_token,
                                global_mode=global_mode,
                                project_mode="repository" if name == "repository" else "fixture")
            if verdict.get("status") != "PASS" or verdict.get("tokens") != {
                    "global_token": token, "project_token": project_token}:
                raise ValueError("Probe evidence does not establish expected loaded instructions")
            for _, directory, _ in cases:
                suppressors(directory, home)
            check_preservation(home, baseline, output, label + "-after")
            records.append({"phase": prefix, "case": name, "verdict": verdict, "protected": "PASS"})
    return records


def rollback_trial(tx, cli, cases, output, token, home, baseline, bounds):
    tx.begin(output / "trial-runtime.md")
    records = trials(cli, cases, output, "positive", token, home, baseline, repeats=2)
    records += trials(cli, cases, output, "bounds", bounds, home, baseline, global_mode="bounds")
    check_preservation(home, baseline, output, "park-before")
    tx.park_native()
    check_preservation(home, baseline, output, "park-after")
    records += trials(cli, cases, output, "negative", "NOT_LOADED", home, baseline, repeats=2)
    tx.restore_native()
    readback = tx.rollback()
    write_json(output / "rollback-readback.json", readback)
    check_preservation(home, baseline, output, "rollback-after")
    if readback.get("phase") != "ROLLED_BACK":
        raise ValueError("Rollback not established")
    return records, readback


def remove_owned(path, identity):
    if os.path.lexists(path):
        current = path.lstat()
        if (current.st_dev, current.st_ino) != (identity.st_dev, identity.st_ino):
            raise ValueError("Receipt identity changed; preserve concurrent replacement")
        path.unlink()


def publish_replica(path, data, publication):
    with path.open("xb") as stream:
        identity = os.fstat(stream.fileno())
        publication["replica_identity"] = identity
        try:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            stream.close()
            remove_owned(path, identity)
            raise
    return identity


def publish_receipt(repo, home, output, version, baseline, final_readback, cli, checks,
                    project_baseline, publication):
    if any(checks.get(key) != "PASS" for key in REQUIRED_CHECKS):
        raise ValueError("Required evidence not established")
    source = repo / "config/agents/claude/SOUL.runtime.md"
    evidence = evidence_files(output)
    receipt = {
        "schema_version": 1, "evidence_class": "live-provider",
        "home": str(home), "source": str(source.resolve()), "source_sha256": sha(source),
        "provider_version": version, "observed_at": datetime.now(timezone.utc).isoformat(),
        "provider_cli": str(cli), "provider_sha256": sha(cli),
        "environment": provider_environment(),
        "checks": checks,
        "evidence_root": str(output), "evidence": evidence,
        "protected": protected_admission_state(home), "protected_full": baseline,
        "project_root": str(repo), "project_protected": project_baseline,
        "limits": "One Windows pilot, startup and guarded lazy fixture; no fleet qualification. Existing project lifecycle hooks may produce logs; zero repository side effects are not claimed.",
        "readback": final_readback,
        "recovery": recovery_reference(Path(final_readback["journal"])),
    }
    # Local consumption receipt is a replica of this private evidence, not an approval.
    pending = output / "pending-verification.json"
    replica = home / ".claude/workspace-soul-verification.json"
    write_json(pending, receipt)
    identity = None
    try:
        identity = publish_replica(replica, pending.read_bytes(), publication)
        if sha(replica) != sha(pending):
            raise ValueError("Receipt replica readback mismatch")
        os.link(pending, output / "verification-receipt.json")
    except BaseException:
        # A replica without the authoritative evidence filename cannot verify.
        # Remove only exact owned bytes; preserve concurrent drift for reconciliation.
        if identity is not None:
            remove_owned(replica, identity)
        raise
    return {"state": "NATIVE_VERIFIED", "receipt": str(output / "verification-receipt.json")}


def evidence_files(output):
    records = []
    for parent, directories, files in os.walk(output, followlinks=False):
        for name in directories + files:
            path = Path(parent) / name
            if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 1024:
                raise ValueError("Evidence link requires reconciliation")
        for name in files:
            path = Path(parent) / name
            records.append({"path": path.relative_to(output).as_posix(), "sha256": sha(path)})
    return sorted(records, key=lambda item: item["path"])


def persistent_preflight(repo, home, source, legacy_sha256):
    git = repo / ".git"
    legacy = home / ".claude/CLAUDE.md"
    if not git.is_dir() or git.is_symlink():
        raise ValueError("Persistent primary checkout required; worktree Git files are refused")
    if not legacy.is_symlink() or legacy.resolve() != source.resolve():
        raise ValueError("Legacy must already resolve to the persistent canonical source")
    if sha(source) != legacy_sha256:
        raise ValueError("Unreviewed canonical source change")
    if CANONICAL_TOKEN not in source.read_text(encoding="utf-8"):
        raise ValueError("Canonical positive sentinel missing")
    if REPOSITORY_TOKEN not in (repo / "AGENTS.md").read_text(encoding="utf-8"):
        raise ValueError("Governed repository readiness instruction missing")


def derive_checks(records, rollback, final_readback, lazy, controls):
    def observed(phase, case):
        matches = [r for r in records if r["phase"] == phase and r["case"] == case]
        return len(matches) == (2 if phase.startswith("final-") else 1) and all(
            r["verdict"]["status"] == "PASS" for r in matches)
    checks = {"native_root": observed("final-restored", "root"),
              "native_nested": observed("final-restored", "nested"),
              "governed_repository": observed("final-restored", "repository"),
              "global_positive": all(observed("final-positive", c) for c in ("root", "nested", "repository")),
              "global_negative": all(observed("final-negative", c) for c in ("root", "nested", "repository")),
              "protected_preserved": bool(records) and all(r["protected"] == "PASS" for r in records),
              "final_readback": final_readback.get("phase") == "FINALIZED",
              "rollback_verified": rollback.get("phase") == "ROLLED_BACK"}
    checks["global_bounds"] = all(observed("bounds", c) for c in ("root", "nested", "repository"))
    checks["native_lazy"] = (lazy == {"positive": "PASS", "negative": "PASS"}
                             and controls == {"allow": "PASS", "deny": "PASS"})
    return {key: "PASS" if value else "FAIL" for key, value in checks.items()}


def lazy_trials(cli, cases, output, home, baseline):
    root = output / "fixture"
    nested = root / "nested"
    instruction = nested / "AGENTS.md"
    parked = output / "parked-lazy-AGENTS.md"
    token = "lazy_" + secrets.token_hex(16)
    with instruction.open("a", encoding="utf-8") as stream:
        stream.write("\nFor deployment_probe, lazy_token is " + token + ".\n")
    target = nested / "harmless.txt"
    target.write_text("Harmless lazy discovery trigger; no instruction tokens.\n")
    identity = instruction.lstat()
    results = {}
    try:
        for phase, expected in (("positive", token), ("negative", "NOT_LOADED")):
            if phase == "negative":
                current = instruction.lstat()
                if parked.exists() or (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns) != (
                        identity.st_dev, identity.st_ino, identity.st_size, identity.st_mtime_ns):
                    raise ValueError("Lazy instruction drift")
                instruction.rename(parked)
            for _, directory, _ in cases:
                suppressors(directory, home)
            check_preservation(home, baseline, output, "lazy-" + phase + "-before")
            verdict = run_probe(cli, root, output, "lazy-" + phase, CANONICAL_TOKEN, expected,
                                global_mode="canonical", project_mode="lazy", read_path=target)
            if verdict.get("status") != "PASS" or verdict.get("tokens") != {
                    "global_token": CANONICAL_TOKEN, "project_token": expected}:
                raise ValueError("Lazy instruction evidence mismatch")
            check_preservation(home, baseline, output, "lazy-" + phase + "-after")
            for _, directory, _ in cases:
                suppressors(directory, home)
            results[phase] = "PASS"
    finally:
        if parked.exists():
            current = parked.lstat()
            if os.path.lexists(instruction) or (current.st_dev, current.st_ino) != (identity.st_dev, identity.st_ino):
                raise ValueError("Lazy fixture recovery blocked by drift")
            parked.rename(instruction)
    write_json(output / "lazy-checks.json", results)
    return results


def prepare_pilot(repo, home, output, journal_parent, cli, legacy_sha256):
    source = repo / "config/agents/claude/SOUL.runtime.md"
    if os.path.lexists(home / ".claude/workspace-soul-verification.json"):
        raise ValueError("Existing receipt requires read-only reconciliation")
    if os.path.lexists(output):
        raise ValueError("Existing output requires read-only reconciliation")
    for suffix in ("-rollback", "-apply"):
        if os.path.lexists(journal_parent / (output.name + suffix)):
            raise ValueError("Existing journal requires read-only reconciliation")
    persistent_preflight(repo, home, source, legacy_sha256)
    check_auth(cli)
    version, cli_sha = provider_version(cli), sha(cli)
    baseline = protected_state(home)
    project_baseline = project_state(repo)
    for directory in (home, repo, output / "fixture", output / "fixture/nested"):
        suppressors(directory, home)
    output.mkdir(parents=True)
    journal_parent = Path(journal_parent).resolve()
    journal_parent.mkdir(parents=True, exist_ok=True)
    cases = make_fixtures(output)
    cases.append(("repository", repo, REPOSITORY_TOKEN))
    write_json(output / "prestate-protected.json", baseline)
    write_json(output / "prestate-project.json", project_baseline)
    token = "global_" + secrets.token_hex(16)
    beginning = "beginning_" + secrets.token_hex(16)
    trial_bytes = (("For deployment_probe, beginning_token is " + beginning + ".\n").encode()
                   + source.read_bytes() + ("\nFor deployment_probe, global_token is " + token + ".\n").encode())
    with (output / "trial-runtime.md").open("xb") as stream:
        stream.write(trial_bytes)
    trials(cli, cases, output, "preflight", "NOT_LOADED", home, baseline)
    controls = guard_controls(cli, output)
    check_preservation(home, baseline, output, "controls-after")
    return source, version, cli_sha, baseline, cases, token, beginning, controls, project_baseline


def invalidate_authority(output, home, publication):
    authority, pending = output / "verification-receipt.json", output / "pending-verification.json"
    if os.path.lexists(authority):
        if not pending.is_file() or pending.is_symlink():
            raise ValueError("No owned receipt identity; reconciliation required")
        remove_owned(authority, pending.lstat())
    if "replica_identity" in publication:
        remove_owned(home / ".claude/workspace-soul-verification.json", publication["replica_identity"])


def recover_pilot(tx, output, home, publication, original):
    outcomes = {}
    for name, action in (("invalidation", lambda: invalidate_authority(output, home, publication)),
                         ("rollback", lambda: tx.rollback() if tx.phase not in ("NEW", "ROLLED_BACK") else None)):
        try:
            outcomes[name] = {"status": "PASS", "result": action()}
        except BaseException as failure:
            outcomes[name] = {"status": "ERROR", "type": type(failure).__name__, "reason": str(failure)}
    marker = output / ("BLOCKED-" + secrets.token_hex(12) + ".json")
    try:
        write_json(marker, {"owner": "FOUNDATION", "original_type": type(original).__name__,
                           "original_reason": str(original), "outcomes": outcomes,
                           "time": datetime.now(timezone.utc).isoformat(), "retry": False})
    except BaseException as failure:
        original.add_note("Recovery completed/attempted; marker unavailable: " + type(failure).__name__)


def execute(repo, home, output, journal_parent, cli, legacy_sha256):
    repo, home, output = Path(repo).resolve(), Path(home).resolve(), Path(output).resolve()
    cli, journal_parent = Path(cli).resolve(), Path(journal_parent).resolve()
    source, version, cli_sha, baseline, cases, token, beginning, controls, project_baseline = prepare_pilot(
        repo, home, output, journal_parent, cli, legacy_sha256)
    tx = Transaction(home, source, journal_parent / (output.name + "-rollback"), legacy_sha256)
    tx.capture()
    publication = {}
    try:
        records, rollback = rollback_trial(tx, cli, cases, output, token, home, baseline, beginning + "|" + token)
        tx = Transaction(home, source, journal_parent / (output.name + "-apply"), legacy_sha256)
        tx.capture()
        tx.begin(output / "trial-runtime.md")
        records += trials(cli, cases, output, "apply-positive", token, home, baseline)
        tx.finalize()
        records += trials(cli, cases, output, "final-positive", CANONICAL_TOKEN, home, baseline,
                          repeats=2, global_mode="canonical")
        tx.park_native()
        records += trials(cli, cases, output, "final-negative", "NOT_LOADED", home, baseline,
                          repeats=2, global_mode="canonical")
        tx.restore_native()
        records += trials(cli, cases, output, "final-restored", CANONICAL_TOKEN, home, baseline,
                          repeats=2, global_mode="canonical")
        lazy = lazy_trials(cli, cases, output, home, baseline)
        if project_state(repo) != project_baseline:
            raise ValueError("Project/ancestor settings changed; preserve and rollback")
        write_json(output / "poststate-project.json", project_baseline)
        if provider_version(cli) != version or sha(cli) != cli_sha:
            raise ValueError("Provider changed during trial")
        final_readback = tx.readback()
        write_json(output / "final-readback.json", final_readback)
        write_json(output / "observed-checks.json", records)
        checks = derive_checks(records, rollback, final_readback, lazy, controls)
        return publish_receipt(repo, home, output, version, baseline, final_readback, cli, checks,
                               project_baseline, publication)
    except BaseException as original:
        recover_pilot(tx, output, home, publication, original)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--legacy-sha256", required=True)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute or os.name != "nt":
        parser.error("Explicit execution is Windows-only; approval comes from the user, not this flag")
    home = Path.home()
    journals = Path(os.environ["LOCALAPPDATA"]) / "workspace-hub/transactions"
    print(json.dumps(execute(args.repo, home, args.output, journals, args.cli, args.legacy_sha256)))


if __name__ == "__main__":
    main()
