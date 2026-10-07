#!/usr/bin/env python3
"""Read-only Claude deployment state. Receipts are evidence, never authorization."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess


REQUIRED_CHECKS = (
    "native_root", "native_nested", "global_positive", "global_negative",
    "protected_preserved", "final_readback", "rollback_verified", "native_lazy", "global_bounds",
    "governed_repository",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provider_version(cli):
    result = subprocess.run([str(cli), "--version"], capture_output=True,
                            text=True, timeout=10, check=True)
    return result.stdout.strip()


def provider_environment():
    names = ("DISABLE_TELEMETRY", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
             "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX", "CLAUDE_CODE_USE_FOUNDRY",
             "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
             "CLAUDE_CONFIG_DIR", "CLAUDE_CODE_DISABLE_AUTO_MEMORY")
    return {name: hashlib.sha256(os.environ[name].encode()).hexdigest()
            if name in os.environ else None for name in names}


def safe_child(root, name):
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError("Invalid evidence-relative path")
    child = root / relative
    if not child.resolve().is_relative_to(root.resolve()):
        raise ValueError("Evidence escapes its declared root")
    return child


def verify_receipt(user_root, source):
    receipt_path = user_root / "workspace-soul-verification.json"
    if receipt_path.is_symlink() or receipt_path.stat().st_size > 2_000_000:
        raise ValueError("Invalid receipt file")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict) or not isinstance(receipt.get("checks"), dict):
        raise ValueError("Malformed native receipt")
    if receipt.get("schema_version") != 1 or receipt.get("evidence_class") != "live-provider":
        raise ValueError("Live-provider evidence receipt required")
    if Path(receipt["home"]).resolve() != user_root.parent.resolve():
        raise ValueError("Receipt home mismatch")
    if Path(receipt["source"]).resolve() != source.resolve():
        raise ValueError("Receipt source mismatch")
    if receipt["source_sha256"] != digest(source):
        raise ValueError("Runtime content changed since verification")
    datetime.fromisoformat(receipt["observed_at"].replace("Z", "+00:00"))
    cli = Path(receipt["provider_cli"])
    if not cli.is_absolute() or digest(cli) != receipt["provider_sha256"]:
        raise ValueError("Provider binary changed since verification")
    if receipt["provider_version"] != provider_version(cli):
        raise ValueError("Provider version changed since verification")
    if receipt.get("environment") != provider_environment():
        raise ValueError("Provider environment changed since verification")
    if any(receipt.get("checks", {}).get(key) != "PASS" for key in REQUIRED_CHECKS):
        raise ValueError("Incomplete native verification")
    verify_files(receipt, user_root)


def protected_matches(receipt, user_root):
    from claude_native_probe import protected_admission_state, marketplace_config_digest, reject_link_chain
    expected = [dict(row) for row in receipt["protected"]]
    actual = protected_admission_state(user_root.parent)
    for row in expected:
        if (row.get("path") != "plugins/known_marketplaces.json" or row.get("type") != "regular"
                or "digest_kind" in row):
            continue
        # Legacy receipts bind raw bytes. Never infer the prior registry policy.
        reference = safe_child(Path(receipt["evidence_root"]), "known-marketplaces-baseline.json")
        if not reference.exists() and not reference.is_symlink():
            reference = user_root / "plugins/known_marketplaces.json"
        reject_link_chain(reference)
        if not reference.is_file():
            raise ValueError("Authenticated marketplace baseline unavailable")
        raw = reference.read_bytes()
        if hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError("Marketplace baseline does not match the original receipt")
        row.update(sha256=marketplace_config_digest(raw), digest_kind="marketplace-config-v1")
    return expected == actual


def verify_files(receipt, user_root):
    from claude_native_probe import project_state
    from claude_native_restore import recovery_reference

    evidence_root = Path(receipt["evidence_root"])
    if not evidence_root.is_absolute() or not evidence_root.is_dir():
        raise ValueError("Evidence root unavailable")
    authority = safe_child(evidence_root, "verification-receipt.json")
    if authority.is_symlink() or digest(authority) != digest(user_root / "workspace-soul-verification.json"):
        raise ValueError("Published verification receipt is missing or differs")
    evidence = receipt.get("evidence", [])
    protected = receipt.get("protected", [])
    if not evidence or not protected:
        raise ValueError("Evidence and protected-state bindings required")
    if not protected_matches(receipt, user_root):
        raise ValueError("Protected configuration or discovery set changed")
    project = Path(receipt["project_root"])
    if project.resolve() != Path(receipt["source"]).resolve().parents[3]:
        raise ValueError("Governed project differs from the canonical source repository")
    if project_state(project) != receipt["project_protected"]:
        raise ValueError("Governed project settings changed")
    if recovery_reference(Path(receipt["recovery"]["journal"])) != receipt["recovery"]:
        raise ValueError("Recovery evidence changed")
    for entry in evidence:
        path = safe_child(evidence_root, entry["path"])
        if path.is_symlink() or digest(path) != entry["sha256"]:
            raise ValueError("Evidence bytes changed")


def inspect_runtime(repo, home):
    source = Path(repo).resolve() / "config/agents/claude/SOUL.runtime.md"
    user_root = Path(home).resolve() / ".claude"
    legacy = user_root / "CLAUDE.md"
    native = user_root / "rules/workspace-soul.md"
    result = {"state": "BLOCKED", "reason": "No managed Claude loader",
              "path": None, "source": str(source)}
    try:
        present = [p for p in (legacy, native) if p.exists() or p.is_symlink()]
        for path in present:
            if not path.is_symlink() or path.resolve(strict=True) != source.resolve(strict=True):
                raise ValueError("Unexpected managed-loader type or target")
        if native in present:
            verify_receipt(user_root, source)
            state = "DUAL_VERIFIED" if legacy in present else "NATIVE_VERIFIED"
            result.update(state=state, path=str(native), reason="Bound native evidence verified")
        elif legacy in present:
            result.update(state="LEGACY", path=str(legacy),
                          reason="Managed legacy retained; native loading not established")
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as error:
        result.update(state="BLOCKED", path=None, reason=str(error))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--home", required=True, type=Path)
    parser.add_argument("--format", choices=("json", "state", "path"), default="json")
    args = parser.parse_args()
    result = inspect_runtime(args.repo, args.home)
    valid = result["state"] in ("LEGACY", "NATIVE_VERIFIED")
    if args.format == "state":
        print(result["state"])
    elif args.format == "path":
        if valid:
            print(Path(result["path"]).as_posix())
    else:
        print(json.dumps(result, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
