#!/usr/bin/env python3
"""Foundation-only report/apply/rollback; claim verification belongs to orchestration.

Run with python -B in the prepared uv environment. Report writes stdout only.
Receipts describe operations, never authenticated permission. Six replacements
are journaled individually; no whole-set atomicity or hostile-race claim is made.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess

import materialize_profile_fs as fs
from materialize_profile_schema import (PAYLOADS, ROOTS, collisions, profile_entries,
                                        git_read, repository_top)


def report(source_root, source_revision, profile, target_root, provider, transaction_dir):
    source, target = fs.checked(source_root), fs.checked(target_root)
    profile = fs.checked(profile)
    if not profile.is_relative_to(source) or not source.is_dir() or not target.is_dir():
        raise ValueError("invalid source/profile/target roots")
    if provider not in ROOTS:
        raise ValueError("unsupported provider")
    fs.disjoint(fs.within(source, ".claude/skills"), fs.within(target, ROOTS[provider]))
    transaction = fs.validate_transaction(transaction_dir, source, target)
    repository_top(source)
    revision = git_read(source, "rev-parse", "HEAD")
    if revision.returncode:
        raise ValueError("source revision could not be verified")
    head = revision.stdout.decode("ascii").strip()
    if head != source_revision:
        raise ValueError("source revision mismatch")
    profile_hash, entries, historical = profile_entries(source, profile, provider)
    collisions(target, provider, entries)
    for entry in entries:
        entry["preimage"] = fs.preimage(fs.within(target, entry["target"]))
        entry["state"] = "absent" if entry["preimage"] is None else (
            "identical" if entry["preimage"] == entry["sha256"] else "replaceable-preimage")
    return {"schema_version": 1, "source_root": str(source), "target_root": str(target),
            "transaction_dir": str(transaction), "source_revision": head, "profile": str(profile),
            "profile_sha256": profile_hash, "historical_profile_sha256": historical,
            "provider": provider, "entries": entries, "claim": "operator-asserted; not authenticated by utility"}


def bind(manifest, source_root, target_root, transaction_dir):
    if manifest.get("schema_version") != 1 or manifest.get("provider") not in ROOTS:
        raise ValueError("invalid transaction manifest")
    supplied = {"source_root": fs.checked(source_root), "target_root": fs.checked(target_root),
                "transaction_dir": fs.checked(transaction_dir, missing=True)}
    for key, value in supplied.items():
        if str(value) != manifest.get(key):
            raise ValueError("manifest root rebinding rejected")
    fs.validate_transaction(supplied["transaction_dir"], supplied["source_root"], supplied["target_root"])
    expected = {ROOTS[manifest["provider"]] + "/" + p for p in PAYLOADS}
    entries = manifest.get("entries", [])
    if len(entries) != 6 or {entry.get("target") for entry in entries} != expected:
        raise ValueError("manifest destination set rejected")
    return supplied["source_root"], supplied["target_root"], supplied["transaction_dir"]


def validate_apply(manifest, source, target, transaction):
    current = report(source, manifest["source_revision"], Path(manifest["profile"]), target,
                     manifest["provider"], transaction)
    expected_binding = {k: v for k, v in manifest.items() if k != "entries"}
    if expected_binding != {k: v for k, v in current.items() if k != "entries"}:
        raise ValueError("source/profile binding changed")
    for old, fresh in zip(manifest["entries"], current["entries"]):
        if {k: v for k, v in old.items() if k not in {"preimage", "state"}} != {
                k: v for k, v in fresh.items() if k not in {"preimage", "state"}}:
            raise ValueError("payload mapping/source changed")
    if all(entry["state"] == "identical" for entry in current["entries"]):
        return True
    if current != manifest:
        raise ValueError("destination preimage changed; request a fresh report")
    return False


def stage(source, target, transaction, receipt):
    for index, entry in enumerate(receipt["manifest"]["entries"]):
        raw = fs.within(source, entry["source"]).read_bytes()
        if fs.digest(raw) != entry["sha256"]:
            raise ValueError("source changed before staging")
        before = fs.preimage(fs.within(target, entry["target"]))
        if before != entry["preimage"]:
            raise ValueError("destination changed before staging")
        if before is not None:
            prior = fs.within(target, entry["target"]).read_bytes()
            if fs.digest(prior) != before:
                raise ValueError("preimage changed during capture")
            fs.durable_file(transaction / f"{index:04d}.preimage", prior)
        fs.durable_file(transaction / f"{index:04d}.payload", raw)
        receipt["writes"].append({"index": index, "state": "staged"})
        fs.save_journal(transaction, receipt)


def install(target, transaction, receipt):
    entries = receipt["manifest"]["entries"]
    for item in receipt["writes"]:
        index = item["index"]
        entry = entries[index]
        destination = fs.within(target, entry["target"])
        fs.create_descendants(destination.parent, target, transaction, receipt)
        item["state"] = "replace-intent"
        fs.save_journal(transaction, receipt)
        fs.replace_payload(transaction / f"{index:04d}.payload", destination, entry["preimage"])
        if fs.preimage(destination) != entry["sha256"]:
            raise ValueError("postimage verification failed")
        item["state"] = "written"
        fs.save_journal(transaction, receipt)


def apply_report(manifest, source_root, target_root, transaction_dir):
    source, target, transaction = bind(manifest, source_root, target_root, transaction_dir)
    if validate_apply(manifest, source, target, transaction):
        return {"status": "noop", "manifest": manifest, "claim": manifest["claim"]}
    fs.checked(transaction.parent)
    transaction.mkdir()  # Exclusive leaf creation; parent is orchestration-owned.
    fs.checked(transaction)
    receipt = {"status": "staging", "manifest": manifest, "directories": [], "writes": []}
    try:
        fs.save_journal(transaction, receipt)
        stage(source, target, transaction, receipt)
        receipt["status"] = "applying"
        fs.save_journal(transaction, receipt)
        install(target, transaction, receipt)
        receipt["status"] = "complete"
        fs.save_journal(transaction, receipt)
        return receipt
    except Exception as error:
        receipt["status"] = "interrupted"
        receipt["error"] = type(error).__name__ + ": " + str(error)
        fs.save_journal(transaction, receipt)
        raise


def rollback_candidates(receipt, target, transaction):
    candidates = []
    for item in receipt["writes"]:
        index = item["index"]
        if type(index) is not int or not 0 <= index < 6:
            raise ValueError("invalid journal index")
        entry = receipt["manifest"]["entries"][index]
        destination = fs.within(target, entry["target"])
        actual = fs.preimage(destination)
        if actual == entry["preimage"]:
            continue
        if actual != entry["sha256"] or item["state"] not in {"replace-intent", "written"}:
            raise ValueError("rollback would overwrite a later writer")
        backup = transaction / f"{index:04d}.preimage"
        if entry["preimage"] is not None and fs.preimage(backup) != entry["preimage"]:
            raise ValueError("rollback backup missing or changed")
        candidates.append((entry, destination, backup))
    return candidates


def rollback(receipt, source_root, target_root, transaction_dir):
    _, target, transaction = bind(receipt["manifest"], source_root, target_root, transaction_dir)
    fs.checked(transaction)
    candidates = rollback_candidates(receipt, target, transaction)
    receipt["status"] = "rollback-intent"
    fs.save_journal(transaction, receipt)
    for index, (entry, destination, backup) in enumerate(candidates):
        if fs.preimage(destination) != entry["sha256"]:
            raise ValueError("rollback concurrent change")
        if entry["preimage"] is None:
            destination.unlink()
        else:
            staged = transaction / f"rollback-{index:04d}.payload"
            fs.durable_file(staged, fs.checked(backup).read_bytes())
            fs.replace_payload(staged, destination, entry["sha256"])
        if fs.preimage(destination) != entry["preimage"]:
            raise ValueError("rollback readback mismatch")
    remove_owned_directories(receipt, target)
    receipt["status"] = "rolled-back"
    fs.save_journal(transaction, receipt)
    return receipt


def remove_owned_directories(receipt, target):
    provider_root = fs.within(target, ROOTS[receipt["manifest"]["provider"]])
    for item in reversed(receipt["directories"]):
        if not item["created"]:
            continue
        path = fs.within(target, item["path"])
        if path == target or not (path.is_relative_to(provider_root) or provider_root.is_relative_to(path)):
            raise ValueError("journal directory outside provider ancestry")
        if path.exists():
            if fs.directory_identity(path) != item.get("identity"):
                raise ValueError("created directory identity changed")
            path.rmdir()  # Never recursive; a later writer's children prevent removal.


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(fs.checked(path).read_bytes(), object_pairs_hook=unique)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source-root", "target-root", "transaction-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-revision")
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--provider", choices=sorted(ROOTS), default="codex")
    parser.add_argument("--manifest", type=Path)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--rollback", action="store_true")
    modes.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        roots = (args.source_root, args.target_root, args.transaction_dir)
        if args.apply or args.rollback:
            if args.manifest is None:
                raise ValueError("explicit manifest required")
            value = load_json(args.manifest)
            result = rollback(value, *roots) if args.rollback else apply_report(value, *roots)
        else:
            if not args.source_revision or args.profile is None:
                raise ValueError("report requires source revision and profile")
            result = report(args.source_root, args.source_revision, args.profile,
                            args.target_root, args.provider, args.transaction_dir)
        print(json.dumps(result, sort_keys=True, ensure_ascii=True))
        return 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "error", "error": str(error)}, ensure_ascii=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
