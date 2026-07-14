#!/usr/bin/env python3
"""Value-withholding CLI for legal-rule authority bootstrap operations."""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path

from rule_authority import authority, codec


def _read(path, maximum=codec.MAX_DOC):
    data = Path(path).read_bytes()
    if len(data) > maximum:
        raise codec.AuthorityError("schema")
    return data


def _key(args):
    if bool(getattr(args, "key_file", None)) == bool(getattr(args, "key_env", None)):
        raise codec.AuthorityError("config")
    encoded = (
        _read(args.key_file, 128).rstrip(b"\n")
        if args.key_file
        else os.environ.get(args.key_env, "").encode("ascii")
    )
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


def _write_new(path, value):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(codec.canonical_bytes(value))


def cmd_validate(args):
    _public(args)
    print("command=validate-public verdict=verified rc=0")


def cmd_verify(args):
    registry, policy = _public(args)
    private_map = codec.parse_map(_read(args.map, codec.MAX_MAP), registry)
    manifest = codec.parse_manifest(_read(args.manifest))
    anchor = codec.parse_anchor(_read(args.anchor))
    key = _key(args)
    authority.verify_bundle(registry, policy, private_map, manifest, key, anchor)
    print(
        f"command=verify generation={manifest['generation']} revision={manifest['authority_revision']} verdict=verified rc=0"
    )


def cmd_seal(args):
    registry, policy = _public(args)
    private_map = codec.parse_map(_read(args.map, codec.MAX_MAP), registry)
    key = _key(args)
    manifest = authority.build_manifest(registry, policy, private_map, key)
    anchor = codec.parse_anchor(_read(args.current_anchor))
    ledger = codec.parse_canonical(_read(args.ledger))
    authority.verify_ledger(ledger, key)
    if manifest["generation"] != anchor["generation"] + 1:
        raise codec.AuthorityError("integrity")
    new_ledger = authority.append_ledger(ledger, manifest, key)
    out = Path(args.out_dir)
    _write_new(out / "authority-manifest.json", manifest)
    _write_new(out / "generation-ledger.json", new_ledger)
    print(
        f"command=seal generation={manifest['generation']} revision={manifest['authority_revision']} verdict=sealed rc=0"
    )


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
    for name in ("map", "manifest", "anchor"):
        verify.add_argument(f"--{name}", required=True)
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
    return parser


def main(argv=None):
    try:
        build_parser().parse_args(argv).func(build_parser().parse_args(argv))
        return 0
    except codec.AuthorityError as exc:
        category = str(exc) if str(exc) in {"schema", "config"} else "integrity"
        rc = 2 if category in {"schema", "config"} else 3
        print(f"command=authority verdict={category} rc={rc}", file=sys.stderr)
        return rc
    except (OSError, UnicodeError):
        print("command=authority verdict=filesystem rc=4", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
