#!/usr/bin/env python3
"""Value-withholding CLI for legal-rule authority bootstrap operations."""

from __future__ import annotations

import argparse
import base64
import os
import stat
import sys
from pathlib import Path

from rule_authority import (
    audit,
    authority,
    codec,
    envelope,
    private_io,
    promotion,
    protection,
)


def _read(path, maximum=codec.MAX_DOC):
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise codec.AuthorityError("schema")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(maximum + 1)
        after = os.fstat(fd)
        if len(data) > maximum or (before.st_dev, before.st_ino) != (
            after.st_dev,
            after.st_ino,
        ):
            raise codec.AuthorityError("schema")
        return data
    finally:
        os.close(fd)


def _key(args):
    if bool(getattr(args, "key_file", None)) == bool(getattr(args, "key_env", None)):
        raise codec.AuthorityError("config")
    if args.key_file:
        raw = private_io.read_private_file(args.key_file, 128)
        if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
            raise codec.AuthorityError("config")
        encoded = raw[:-1]
    else:
        encoded = os.environ.get(args.key_env, "").encode("ascii")
    try:
        value = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise codec.AuthorityError("config") from exc
    if base64.b64encode(value) != encoded or len(value) != 32:
        raise codec.AuthorityError("config")
    return value


def _public(args):
    registry = codec.parse_registry(_read(args.registry))
    policy = codec.parse_policy(_read(args.policy))
    if (registry["generation"], registry["authority_revision"]) != (
        policy["generation"],
        policy["authority_revision"],
    ):
        raise codec.AuthorityError("schema")
    return registry, policy


def cmd_validate(args):
    _public(args)
    print("command=validate-public verdict=verified rc=0")


def cmd_verify(args):
    registry, policy = _public(args)
    private_map = codec.parse_map(_read(args.map, codec.MAX_MAP), registry)
    manifest = codec.parse_manifest(_read(args.manifest))
    anchor = codec.parse_anchor(_read(args.anchor))
    ledger = codec.parse_ledger(_read(args.ledger))
    key = _key(args)
    authority.verify_bundle(
        registry,
        policy,
        private_map,
        manifest,
        key,
        anchor,
        ledger,
        args.tool_sha,
        args.head_oid,
    )
    print(
        f"command=verify generation={manifest['generation']} revision={manifest['authority_revision']} verdict=verified rc=0"
    )


def cmd_seal(args):
    registry, policy = _public(args)
    private_map = codec.parse_map(_read(args.map, codec.MAX_MAP), registry)
    key = _key(args)
    manifest = authority.build_manifest(registry, policy, private_map, key)
    anchor = codec.parse_anchor(_read(args.current_anchor))
    ledger = codec.parse_ledger(_read(args.ledger))
    authority.verify_ledger(ledger, key)
    tip = ledger["entries"][-1]
    identity = ("generation", "authority_revision", "manifest_mac")
    if any(anchor[key] != tip[key] for key in identity):
        raise codec.AuthorityError("integrity")
    if manifest["generation"] != anchor["generation"] + 1:
        raise codec.AuthorityError("integrity")
    new_ledger = authority.append_ledger(ledger, manifest, key)
    out = Path(args.out_dir)
    private_io.write_private_files(
        out,
        {
            "authority-manifest.json": codec.canonical_bytes(manifest),
            "generation-ledger.json": codec.canonical_bytes(new_ledger),
        },
    )
    print(
        f"command=seal generation={manifest['generation']} revision={manifest['authority_revision']} verdict=sealed rc=0"
    )


def _authority_dir(args):
    directory = Path(args.authority_dir)
    registry = codec.parse_registry(_read(args.registry))
    policy = codec.parse_policy(_read(args.policy))
    private_map = codec.parse_map(
        _read(directory / "map.json", codec.MAX_MAP), registry
    )
    manifest = codec.parse_manifest(_read(directory / "manifest.json"))
    anchor = codec.parse_anchor(_read(directory / "anchor.json"))
    ledger = codec.parse_ledger(_read(directory / "ledger.json"))
    args.key_file = directory / "key.b64"
    key = _key(args)
    tool_sha = getattr(args, "tool_sha", None) or anchor["tool_sha"]
    head_oid = getattr(args, "commit", None)
    authority.verify_bundle(
        registry, policy, private_map, manifest, key, anchor, ledger, tool_sha, head_oid
    )
    mapped = {
        item["rule_id"]: base64.b64decode(item["pattern_b64"])
        for item in private_map["rules"]
    }
    rules = [{**item, "pattern": mapped[item["rule_id"]]} for item in registry["rules"]]
    rules.extend(
        {
            "match_mode": "exact-bytes",
            "pattern": token,
            "rule_id": "structural",
            "severity": "block",
            "target": "both",
        }
        for token in authority.structural_tokens(
            private_map, manifest, key, anchor=anchor, ledger=ledger
        )
    )
    return registry, policy, manifest, key, rules


def cmd_audit_tree(args):
    _registry, policy, manifest, key, rules = _authority_dir(args)
    result = audit.audit_tree(
        args.repo, args.commit, args.required_ref, rules, policy["limits"]
    )
    transaction = private_io.write_complete_transaction(
        Path(args.out_dir),
        args.transaction_id,
        {"tree-report.json": codec.canonical_bytes(result)},
        key,
        manifest,
        coverage={"tree": result["coverage"]},
        snapshots={"commit": args.commit},
    )
    verdict = "finding" if result["findings"] else "clean"
    print(
        f"command=audit-tree generation={manifest['generation']} objects={result['objects_examined']} coverage=complete verdict={verdict} rc={1 if result['findings'] else 0}"
    )
    if result["findings"]:
        raise SystemExit(1)
    return transaction


def cmd_cleanup(args):
    private_io.cleanup_incomplete(Path(args.parent), args.transaction_id)
    print("command=cleanup-incomplete verdict=complete rc=0")


def cmd_audit_history(args):
    _registry, policy, manifest, key, rules = _authority_dir(args)
    remote = os.environ.get(args.remote_url_env, "")
    result = audit.audit_history(remote, Path(args.mirror_dir), rules, policy["limits"])
    result["github_coverage"] = {
        "state": "unknown-residual",
        "reason": "bounded-adapters-unavailable",
    }
    private_io.write_complete_transaction(
        Path(args.out_dir),
        args.transaction_id,
        {"history-report.json": codec.canonical_bytes(result)},
        key,
        manifest,
        coverage={"git": "scanned", "github": "unknown-residual"},
        snapshots={},
    )
    print(
        f"command=audit-history generation={manifest['generation']} objects={result['objects_examined']} coverage=residual verdict=unknown rc=3"
    )
    raise codec.AuthorityError("integrity")


def cmd_materialize(args):
    envelope.materialize(_read(args.envelope, 32768), args.out_dir)
    print("command=materialize-envelope verdict=complete rc=0")


def cmd_promote(args):
    promotion.validate(
        args.current_envelope_env,
        args.pending_envelope_env,
        args.expected_head,
        args.expected_tree,
        _read(args.preview),
    )
    print("command=promote verdict=ready rc=0")


def cmd_verify_protection(args):
    protection.verify_readback(
        codec.parse_canonical(_read(args.preview)),
        codec.parse_canonical(_read(args.environment_response)),
        codec.parse_canonical(_read(args.ruleset_response)),
    )
    print("command=verify-protection verdict=verified rc=0")


def _common(parser):
    parser.add_argument("--registry", required=True)
    parser.add_argument("--policy", required=True)


def build_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-public")
    _common(validate)
    validate.set_defaults(func=cmd_validate)
    verify = sub.add_parser("verify")
    _common(verify)
    for name in ("map", "manifest", "anchor", "ledger", "tool-sha"):
        verify.add_argument(f"--{name}", required=True)
    verify.add_argument("--head-oid")
    keys = verify.add_mutually_exclusive_group(required=True)
    keys.add_argument("--key-file")
    keys.add_argument("--key-env")
    verify.set_defaults(func=cmd_verify)
    seal = sub.add_parser("seal")
    _common(seal)
    for name in ("map", "current-anchor", "ledger", "out-dir"):
        seal.add_argument(f"--{name}", required=True)
    seal.add_argument("--key-file", required=True)
    seal.set_defaults(func=cmd_seal)
    tree = sub.add_parser("audit-tree")
    _common(tree)
    for name in (
        "repo",
        "commit",
        "required-ref",
        "authority-dir",
        "out-dir",
        "transaction-id",
        "tool-sha",
    ):
        tree.add_argument(f"--{name}", required=True)
    tree.set_defaults(func=cmd_audit_tree)
    cleanup = sub.add_parser("cleanup-incomplete")
    cleanup.add_argument("--parent", required=True)
    cleanup.add_argument("--transaction-id", required=True)
    cleanup.set_defaults(func=cmd_cleanup)
    history = sub.add_parser("audit-history")
    _common(history)
    for name in (
        "remote-url-env",
        "github-repo",
        "authority-dir",
        "mirror-dir",
        "out-dir",
        "github-token-env",
        "transaction-id",
    ):
        history.add_argument(f"--{name}", required=True)
    history.set_defaults(func=cmd_audit_history)
    materialize = sub.add_parser("materialize-envelope")
    materialize.add_argument("--envelope", required=True)
    materialize.add_argument("--out-dir", required=True)
    materialize.set_defaults(func=cmd_materialize)
    promote = sub.add_parser("promote")
    for name in (
        "current-envelope-env",
        "pending-envelope-env",
        "expected-head",
        "expected-tree",
        "preview",
    ):
        promote.add_argument(f"--{name}", required=True)
    promote.set_defaults(func=cmd_promote)
    readback = sub.add_parser("verify-protection")
    for name in ("preview", "environment-response", "ruleset-response"):
        readback.add_argument(f"--{name}", required=True)
    readback.set_defaults(func=cmd_verify_protection)
    return parser


def main(argv=None):
    try:
        args = build_parser().parse_args(argv)
        args.func(args)
        return 0
    except codec.AuthorityError as exc:
        category = (
            str(exc) if str(exc) in {"schema", "config", "filesystem"} else "integrity"
        )
        rc = (
            4
            if category == "filesystem"
            else 2
            if category in {"schema", "config"}
            else 3
        )
        print(f"command=authority verdict={category} rc={rc}", file=sys.stderr)
        return rc
    except (OSError, UnicodeError):
        print("command=authority verdict=filesystem rc=4", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
