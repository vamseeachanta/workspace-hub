#!/usr/bin/env python3
"""equivalence_state.py — share per-machine fingerprints via a dedicated git ref.

Mirrors the proven ``dispatch_leader.py`` GitLeaderStateStore idiom: state lives in
a dedicated ref (``equivalence-state``) written with git plumbing (hash-object /
mktree / commit-tree) and pushed with ``--force-with-lease`` — so it never churns
``main``. The ref's tree holds one ``<machine_id>.json`` blob per box (#3516).

Part of the machine-equivalence drift sentinel (#3059, epic #3058).
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from equivalence_schema import (
    FingerprintValidationError,
    _reject_constant,
    _require_optional_number,
    require_rfc3339,
    validate_fingerprint,
)

DEFAULT_REF = "equivalence-state"

# Pre-#3516 blobs were keyed by ROLE — two same-role boxes (ace-win-1/2, both
# contribute-minimal) would silently clobber each other. Blobs are now keyed by
# registry machine id; these legacy names are self-cleaned on each publish.
LEGACY_ROLE_NAMES = {"full", "contribute", "contribute-minimal", "none", "unknown"}
PUBLISH_HEALTH_KEYS = {"schema_version", "ts", "phase", "duration_s", "rc"}


def resolve_identity(registry_path, hostname):
    """(machine_id, role) for a hostname from config/workstations/registry.yaml.
    Matches hostname or hostname_aliases case-insensitively; role = schedule_variant.
    Collision-safe fallback ("unknown-<hostname>", "unknown") on any failure so two
    unregistered boxes can never share a blob name (#3516)."""
    fallback = (f"unknown-{hostname}", "unknown")
    try:
        with open(registry_path) as fh:
            text = fh.read()
        try:
            import yaml
            data = yaml.safe_load(text) or {}
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from equivalence_compare import _parse_registry_minimal
            data = _parse_registry_minimal(text)
        want = str(hostname).lower()
        for machine_id, m in sorted((data.get("machines") or {}).items()):
            m = m or {}
            names = {str(m.get("hostname") or "").lower(), str(machine_id).lower()}
            names |= {str(a).lower() for a in (m.get("hostname_aliases") or [])}
            if want in names:
                return (machine_id, str(m.get("schedule_variant") or "unknown"))
        return fallback
    except Exception:  # noqa: BLE001 — degrade to collision-safe fallback by design
        return fallback


class StoreUnavailable(RuntimeError):
    pass


class PublishHealthValidationError(ValueError):
    pass


def validate_publish_health(content):
    try:
        data = json.loads(content, parse_constant=_reject_constant)
    except (json.JSONDecodeError, TypeError, FingerprintValidationError) as exc:
        raise PublishHealthValidationError(f"invalid publish-health JSON: {exc}") from exc
    if not isinstance(data, dict) or set(data) != PUBLISH_HEALTH_KEYS:
        raise PublishHealthValidationError("publish health has an invalid key set")
    version = data["schema_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != 1:
        raise PublishHealthValidationError("schema_version must be integer 1")
    if not isinstance(data["phase"], str) or data["phase"] not in {"fingerprint", "publish"}:
        raise PublishHealthValidationError("phase must be fingerprint or publish")
    try:
        require_rfc3339(data["ts"])
    except FingerprintValidationError as exc:
        raise PublishHealthValidationError(str(exc)) from exc
    try:
        _require_optional_number(data["duration_s"], "duration_s")
    except FingerprintValidationError as exc:
        raise PublishHealthValidationError(str(exc)) from exc
    if data["duration_s"] is None:
        raise PublishHealthValidationError("duration_s cannot be null")
    rc = data["rc"]
    if isinstance(rc, bool) or not isinstance(rc, int) or not 0 <= rc <= 4:
        raise PublishHealthValidationError("rc must be an integer in 0..4")
    return data


def _atomic_json(path, data, validator):
    target = os.path.abspath(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=f".{os.path.basename(target)}.",
                                     dir=os.path.dirname(target), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, indent=1, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        with open(temp_path, encoding="utf-8") as handle:
            validator(handle.read())
        os.replace(temp_path, target)
    finally:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass


def prepare_fingerprint(path, publish_health_path):
    with open(path, encoding="utf-8") as handle:
        fingerprint = validate_fingerprint(handle.read())
    try:
        with open(publish_health_path, encoding="utf-8") as handle:
            health = validate_publish_health(handle.read())
    except (OSError, PublishHealthValidationError):
        health = None
    fingerprint["last_publish_duration_s"] = (
        health["duration_s"] if health and health["phase"] == "publish" else None
    )
    _atomic_json(path, fingerprint, validate_fingerprint)


def write_publish_health(path, phase, duration_s, rc):
    data = {
        "schema_version": 1,
        "ts": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "duration_s": duration_s,
        "rc": rc,
    }
    validate_publish_health(json.dumps(data, allow_nan=False))
    _atomic_json(path, data, validate_publish_health)


def _git(repo, *args, _input=None, _env=None, _text=True):
    env = {**os.environ, **_env} if _env else None
    return subprocess.run(["git", "-C", repo, *args], input=_input,
                          capture_output=True, text=_text, env=env)


# The equivalence-state ref is a disconnected plumbing-built chain: the
# pre-push hook can never attribute its diff (no merge-base with main) and
# gates every publish as a new-branch RUN_ALL — a 60+ min full-suite run that
# keeps the ref from ever landing (#3500, sub-case of #3198). Push with the
# hook's audited soft bypass; each use is logged to pre-push-bypass.jsonl.
_PUSH_ENV = {"GIT_PRE_PUSH_SKIP": "1"}


def _fetch_tip(repo, remote, ref):
    """Return the commit SHA of the remote ref, or None if it doesn't exist yet."""
    ls = _git(repo, "ls-remote", "--exit-code", remote, ref)
    if ls.returncode == 2:
        return None
    if ls.returncode != 0:
        raise StoreUnavailable(f"git ls-remote failed: {ls.stderr.strip()[:200]}")
    tracking = f"refs/equivalence-tracking/{ref}"
    f = _git(repo, "fetch", "--quiet", remote, f"+{ref}:{tracking}")
    if f.returncode != 0:
        raise StoreUnavailable(f"git fetch failed: {f.stderr.strip()[:200]}")
    rev = _git(repo, "rev-parse", "--verify", "--quiet", tracking)
    return rev.stdout.strip() or None


def _tree_entries(repo, parent):
    """Return every top-level entry with exact mode/type/name preservation."""
    if parent is None:
        return {}
    ls = _git(repo, "ls-tree", "-z", parent, _text=False)
    if ls.returncode != 0:
        stderr = ls.stderr.decode(errors="replace") if isinstance(ls.stderr, bytes) else ls.stderr
        raise StoreUnavailable(f"git ls-tree failed: {stderr.strip()[:200]}")
    out = {}
    raw = ls.stdout.encode() if isinstance(ls.stdout, str) else ls.stdout
    for line in raw.split(b"\0"):
        meta, _, name_raw = line.partition(b"\t")
        parts = meta.split()
        if not line:
            continue
        if len(parts) != 3 or not name_raw:
            raise StoreUnavailable("git ls-tree returned a malformed entry")
        name = name_raw.decode("utf-8", errors="surrogateescape")
        out[name] = tuple(part.decode("ascii") for part in parts)
    return out


def collect(repo, *, remote="origin", ref=DEFAULT_REF):
    """Return list of fingerprint dicts currently published by all boxes."""
    parent = _fetch_tip(repo, remote, ref)
    fps = []
    for name, entry in _tree_entries(repo, parent).items():
        mode, kind, sha = entry
        if kind != "blob" or not name.endswith(".json"):
            continue
        show = _git(repo, "cat-file", "-p", sha)
        if show.returncode == 0:
            try:
                fps.append(validate_fingerprint(show.stdout))
            except FingerprintValidationError as exc:
                raise StoreUnavailable(f"invalid fingerprint entry {name}: {exc}") from exc
    return fps


def _drop_own_legacy(repo, entries, name, own_host):
    if not own_host:
        return
    candidates = [n for n in entries
                  if n.endswith(".json")
                  and n[:-len(".json")] in LEGACY_ROLE_NAMES and n != name]
    for legacy in candidates:
        show = _git(repo, "cat-file", "-p", entries[legacy][2])
        if show.returncode != 0:
            continue
        try:
            if str(json.loads(show.stdout).get("hostname") or "").lower() == own_host:
                del entries[legacy]
        except ValueError:
            pass


def _commit_fingerprint(repo, entries, name, content, machine, parent):
    hashed = _git(repo, "hash-object", "-w", "--stdin", _input=content)
    if hashed.returncode != 0:
        raise StoreUnavailable(f"hash-object failed: {hashed.stderr.strip()[:200]}")
    entries[name] = ("100644", "blob", hashed.stdout.strip())
    tree_input = b"".join(
        f"{mode} {kind} {sha}\t".encode("ascii")
        + entry.encode("utf-8", errors="surrogateescape") + b"\0"
        for entry, (mode, kind, sha) in sorted(
            entries.items(), key=lambda item: item[0].encode("utf-8", errors="surrogateescape")
        )
    )
    made_tree = _git(repo, "mktree", "-z", _input=tree_input, _text=False)
    if made_tree.returncode != 0:
        stderr = (made_tree.stderr.decode(errors="replace")
                  if isinstance(made_tree.stderr, bytes) else made_tree.stderr)
        raise StoreUnavailable(f"mktree failed: {stderr.strip()[:200]}")
    tree = (made_tree.stdout.decode("ascii").strip()
            if isinstance(made_tree.stdout, bytes) else made_tree.stdout.strip())
    args = ["commit-tree", tree, "-m", f"chore(equivalence): {machine} fingerprint"]
    if parent:
        args += ["-p", parent]
    committed = _git(repo, *args)
    if committed.returncode != 0:
        raise StoreUnavailable(f"commit-tree failed: {committed.stderr.strip()[:200]}")
    return committed.stdout.strip()


def _push_fingerprint(repo, remote, ref, commit, parent):
    args = ["push", remote, f"{commit}:refs/heads/{ref}"]
    if parent:
        args.append(f"--force-with-lease=refs/heads/{ref}:{parent}")
    return _git(repo, *args, _env=_PUSH_ENV)


def publish(repo, machine, content, *, remote="origin", ref=DEFAULT_REF, retries=3):
    """Publish <machine>.json with CAS retry and self-clean legacy role keys."""
    fingerprint = validate_fingerprint(content)
    if fingerprint["machine_id"] != machine:
        raise FingerprintValidationError("machine_id does not match the publish key")
    name = f"{machine}.json"
    for _ in range(retries):
        parent = _fetch_tip(repo, remote, ref)
        entries = _tree_entries(repo, parent)
        _drop_own_legacy(repo, entries, name, fingerprint["hostname"].lower())
        commit = _commit_fingerprint(repo, entries, name, content, machine, parent)
        pushed = _push_fingerprint(repo, remote, ref, commit, parent)
        if pushed.returncode == 0:
            return True
        output = (pushed.stdout + pushed.stderr).lower()
        retryable = ("rejected", "non-fast-forward", "stale info",
                     "fetch first", "already exists")
        if not any(marker in output for marker in retryable):
            raise StoreUnavailable(f"push failed: {pushed.stderr.strip()[:200]}")
    return False


def _argument_parser():
    ap = argparse.ArgumentParser(description="Publish/collect equivalence fingerprints via git ref")
    ap.add_argument("cmd", choices=[
        "publish", "collect", "resolve-identity", "validate", "prepare", "write-health",
    ])
    ap.add_argument("--repo", default=".")
    ap.add_argument("--machine", help="machine id for publish blob name (#3516)")
    ap.add_argument("--role", help="DEPRECATED for publish (used as blob key when --machine absent)")
    ap.add_argument("--registry", help="registry.yaml for resolve-identity")
    ap.add_argument("--hostname", help="hostname for resolve-identity")
    ap.add_argument("--file", help="fingerprint JSON file to publish")
    ap.add_argument("--health", help="publish-health JSON path")
    ap.add_argument("--phase", choices=["fingerprint", "publish"])
    ap.add_argument("--duration", type=float)
    ap.add_argument("--rc", type=int)
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--ref", default=DEFAULT_REF)
    return ap


def _run_command(a, ap):
    if a.cmd == "resolve-identity":
        if not a.registry or not a.hostname:
            ap.error("resolve-identity requires --registry and --hostname")
        machine, role = resolve_identity(a.registry, a.hostname)
        print(f"{machine} {role}")
        return 0
    if a.cmd == "validate":
        if not a.file:
            ap.error("validate requires --file")
        with open(a.file, encoding="utf-8") as handle:
            validate_fingerprint(handle.read())
        print("valid")
        return 0
    if a.cmd == "prepare":
        if not a.file or not a.health:
            ap.error("prepare requires --file and --health")
        prepare_fingerprint(a.file, a.health)
        return 0
    if a.cmd == "write-health":
        if not a.health or a.phase is None or a.duration is None or a.rc is None:
            ap.error("write-health requires --health, --phase, --duration, and --rc")
        write_publish_health(a.health, a.phase, a.duration, a.rc)
        return 0
    if a.cmd == "publish":
        key = a.machine or a.role
        if not key or not a.file:
            ap.error("publish requires --machine (or legacy --role) and --file")
        with open(a.file, encoding="utf-8") as handle:
            content = handle.read()
        ok = publish(a.repo, key, content, remote=a.remote, ref=a.ref)
        print("published" if ok else "publish lost CAS race after retries", file=sys.stderr)
        return 0 if ok else 1
    print(json.dumps(collect(a.repo, remote=a.remote, ref=a.ref), indent=1))
    return 0


def main(argv=None):
    ap = _argument_parser()
    a = ap.parse_args(argv)
    try:
        return _run_command(a, ap)
    except StoreUnavailable as e:
        print(f"equivalence-state unavailable: {e}", file=sys.stderr)
        return 3
    except FingerprintValidationError as e:
        print(f"invalid fingerprint: {e}", file=sys.stderr)
        return 2
    except PublishHealthValidationError as e:
        print(f"invalid publish health: {e}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"equivalence state I/O failed: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
