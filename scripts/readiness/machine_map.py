#!/usr/bin/env python3
"""Private inventory tooling; only the project command emits public metadata.

Protocol fields and enums: docs/readiness/machine-map.md, schema version 1.
Security boundary: issue #3498, Security posture and Scope (2026).
No credential reads, provider execution, remote probes or Git mutations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import stat
import subprocess
import tempfile
from datetime import UTC, datetime
from html import escape
from pathlib import Path

PUBLIC_ROOT = Path(__file__).resolve().parents[2]
ABSENT = {"present": False, "updated_at": None, "content_hash": None}
ROLES = {"producer", "executor", "portable", "other"}
KINDS = {"unit", "timer", "cron", "agent"}
STATES = {"active", "inactive", "failed", "present", "absent", "not_evaluated"}
PROVIDERS = {"gh", "claude", "codex", "gemini", "hermes"}


def slug(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", value):
        raise ValueError("invalid inventory name")
    return value


def timestamp(value):
    # RFC 3339 (2002), section 5.6: offset hours 00..23 and minutes 00..59.
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)", value
    ):
        raise ValueError("invalid observation timestamp")
    dt = datetime.fromisoformat(value)
    if dt.utcoffset() is None:
        raise ValueError("observation needs timezone")
    return dt


def fields(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError("invalid inventory fields")


def unique_rows(rows):
    if not isinstance(rows, list):
        raise TypeError("inventory rows must be a list")
    names = [slug(row["name"]) for row in rows]
    if len(names) != len(set(names)):
        raise ValueError("duplicate inventory name")


def validate_map(value):
    fields(value, {"schema_version", "machine", "role", "source", "updated_at",
                   "data_sources", "services", "auth_surfaces"})
    # Version tag is a protocol identifier, not a measured numeric quantity.
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise ValueError("unsupported inventory schema")
    slug(value["machine"])
    if value["role"] not in ROLES or value["source"] not in {"self-report", "seeded-manual"}:
        raise ValueError("invalid inventory provenance")
    timestamp(value["updated_at"])
    for key in ("data_sources", "services"):
        if not isinstance(value[key], list):
            raise TypeError("inventory rows must be a list")
        for row in value[key]:
            fields(row, {"name", "reachable"} if key == "data_sources" else {"name", "kind", "state"})
            if key == "data_sources":
                if type(row["reachable"]) is not bool and row["reachable"] != "not_evaluated":
                    raise ValueError("invalid reachability")
            elif row["kind"] not in KINDS or row["state"] not in STATES:
                raise ValueError("invalid service observation")
        unique_rows(value[key])
    auth = value["auth_surfaces"]
    if not isinstance(auth, dict) or not set(auth) <= PROVIDERS or any(type(v) is not bool for v in auth.values()):
        raise ValueError("invalid authentication surface")
    return value


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def read_json(path):
    # JSON is a YAML subset; rejecting duplicate fields avoids ambiguous identities.
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs)


def private_area(root):
    if root is None:
        raise ValueError("private destination is required")
    root = Path(root).resolve(strict=True)
    if root == PUBLIC_ROOT or root.is_relative_to(PUBLIC_ROOT) or PUBLIC_ROOT.is_relative_to(root):
        raise ValueError("private destination overlaps public repository")
    area = root / "machine-ecosystem"
    if is_link(area) or not area.is_dir():
        raise ValueError("private destination is not initialized")
    marker = area / "private.json"
    if is_link(marker) or read_json(marker) != {"visibility": "private"}:
        raise ValueError("private destination acknowledgement is required")
    return area


def is_link(path):
    if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
        return True
    try:
        # Python 3.11 lacks is_junction; reject all Windows reparse points.
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def safe_target(area, relative):
    target = area / relative
    # Refuse every symlink component, even one that currently resolves inside the root.
    current = target
    while current != area:
        if is_link(current):
            raise ValueError("inventory destination contains a symlink")
        current = current.parent
    if not target.resolve().is_relative_to(area):
        raise ValueError("inventory destination escapes private root")
    return target


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode()


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Restrictive file permissions apply to both private YAML and private HTML.
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".map-", delete=False) as stream:
        stream.write(content)
        temporary = Path(stream.name)
    temporary.replace(path)


def write_map(root, value):
    validate_map(value)
    area = private_area(root)
    path = safe_target(area, Path("machines") / f'{value["machine"]}.yaml')
    normalized = {**value, "data_sources": sorted(value["data_sources"], key=lambda r: r["name"]),
                  "services": sorted(value["services"], key=lambda r: r["name"])}
    if path.exists():
        previous = validate_map(read_json(path))
        if {k: v for k, v in previous.items() if k != "updated_at"} == {
            k: v for k, v in normalized.items() if k != "updated_at"
        }:
            return False
    atomic_write(path, encode(normalized))
    return True


def project(root, machine):
    slug(machine)
    try:
        area = private_area(root)
        path = safe_target(area, Path("machines") / f"{machine}.yaml")
        raw = path.read_bytes()
        value = validate_map(json.loads(raw, object_pairs_hook=_pairs))
        if value["machine"] != machine:
            return dict(ABSENT)
        # SHA-256 is the issue's content identity; hash the bytes actually stored.
        return {"present": True, "updated_at": value["updated_at"],
                "content_hash": hashlib.sha256(raw).hexdigest()}
    except (OSError, ValueError, TypeError, KeyError):
        return dict(ABSENT)


def path_presence(path):
    try:
        Path(path).stat()
        return True
    except FileNotFoundError:
        return False
    except OSError:
        return "not_evaluated"


def service_state(row, timeout):
    kind = row["kind"]
    if kind == "agent":
        exists = path_presence(row["path"])
        return "present" if exists is True else "absent" if exists is False else "not_evaluated"
    try:
        if kind in {"unit", "timer"}:
            # Query state only; never start a service or invoke a provider or solver.
            result = subprocess.run(["systemctl", "is-active", "--", row["target"]],
                                    capture_output=True, text=True, timeout=timeout, check=False)
            state = result.stdout.strip()
            return state if state in {"active", "inactive", "failed"} else "not_evaluated"
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True,
                                timeout=timeout, check=False)
        if result.returncode != 0:
            return "not_evaluated"
        # Only an exact trailing marker identifies a configured job; no command is retained.
        marker = f'# machine-map:{row["target"]}'
        found = any(line.strip() and not line.lstrip().startswith("#") and
                    line.rstrip().endswith(marker) for line in result.stdout.splitlines())
        return "present" if found else "absent"
    except (OSError, subprocess.TimeoutExpired):
        return "not_evaluated"


def collect(machine, config, at):
    slug(machine)
    timestamp(at)
    fields(config, {"role", "probe_timeout_seconds", "data_sources", "services", "auth_surfaces"})
    timeout = config["probe_timeout_seconds"]
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("positive finite probe timeout is required")
    if config["role"] not in ROLES:
        raise ValueError("invalid dispatch role")
    if not isinstance(config["data_sources"], list) or not isinstance(config["services"], list):
        raise TypeError("probe rows must be lists")
    for row in config["data_sources"]:
        fields(row, {"name", "path"})
        if not isinstance(row["path"], str) or not Path(row["path"]).is_absolute():
            raise ValueError("data probe requires absolute local path")
    for row in config["services"]:
        if not isinstance(row, dict):
            raise TypeError("service probe must be an object")
        kind = row.get("kind")
        if kind not in KINDS:
            raise ValueError("invalid service kind")
        fields(row, {"name", "kind", "path" if kind == "agent" else "target"})
        if kind == "agent":
            if not isinstance(row["path"], str) or not Path(row["path"]).is_absolute():
                raise ValueError("agent probe requires absolute local path")
        elif not isinstance(row["target"], str) or not re.fullmatch(r"[a-zA-Z0-9_.@-]+", row["target"]):
            raise ValueError("invalid service target")
    unique_rows(config["data_sources"])
    unique_rows(config["services"])
    auth = config["auth_surfaces"]
    if not isinstance(auth, list) or any(p not in PROVIDERS for p in auth) or len(auth) != len(set(auth)):
        raise ValueError("invalid authentication surface configuration")
    result = {"schema_version": 1, "machine": machine, "role": config["role"],
              "source": "self-report", "updated_at": at,
              "data_sources": [{"name": row["name"], "reachable": path_presence(row["path"])}
                               for row in config["data_sources"]],
              "services": [{"name": row["name"], "kind": row["kind"],
                            "state": service_state(row, timeout)} for row in config["services"]],
              "auth_surfaces": {p: shutil.which(p) is not None for p in auth}}
    return validate_map(result)


def build_matrix(root, roster):
    area = private_area(root)
    if not isinstance(roster, list) or len(roster) != len(set(roster)):
        raise ValueError("unique active roster is required")
    records = {}
    for machine in roster:
        slug(machine)
        pointer = project(root, machine)
        if pointer["present"]:
            path = safe_target(area, Path("machines") / f"{machine}.yaml")
            records[machine] = validate_map(read_json(path))
    sources = sorted({r["name"] for v in records.values() for r in v["data_sources"]})
    services = sorted({(r["kind"], r["name"]) for v in records.values() for r in v["services"]})
    headers = ["Machine", "Role", "Source", "Updated", "Content hash"] + sources + [
        f"{kind}:{name}" for kind, name in services]
    rows = []
    for machine in sorted(roster):
        if machine not in records:
            cells = [machine] + ["MISSING-EVIDENCE"] * (len(headers) - 1)
        else:
            r = records[machine]
            data = {d["name"]: str(d["reachable"]).lower() for d in r["data_sources"]}
            states = {(s["kind"], s["name"]): s["state"] for s in r["services"]}
            cells = [machine, r["role"], r["source"], r["updated_at"], project(root, machine)["content_hash"]]
            cells += [data.get(name, "not_evaluated") for name in sources]
            cells += [states.get(key, "not_evaluated") for key in services]
        rows.append("<tr>" + "".join(f"<td>{escape(c)}</td>" for c in cells) + "</tr>")
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<title>Private machine ecosystem</title><h1>Private machine ecosystem</h1>'
            '<p>Local observations and manual assertions; presence does not establish authorization '
            'or application access. Missing observations remain not evaluated.</p><table><thead><tr>'
            + "".join(f"<th>{escape(h)}</th>" for h in headers)
            + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></html>\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["collect", "seed", "project", "build"])
    parser.add_argument("--machine")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--at")
    args = parser.parse_args()
    root = os.environ.get("MACHINE_MAP_ADMIN_ROOT")
    try:
        if args.command == "project":
            print(json.dumps(project(root, args.machine), sort_keys=True))
            return
        area = private_area(root)
        if args.input is None or not args.input.resolve().is_relative_to(area):
            raise ValueError("input must be inside the private inventory directory")
        if args.command == "build":
            html = build_matrix(root, read_json(args.input))
            path = safe_target(area, Path("matrix.html"))
            if not path.exists() or path.read_bytes() != html.encode():
                atomic_write(path, html.encode())
            print("built")
            return
        value = read_json(args.input)
        if args.command == "collect":
            at = args.at or datetime.now(UTC).isoformat()
            value = collect(args.machine, value, at)
        elif not isinstance(value, dict) or value.get("source") != "seeded-manual":
            raise ValueError("manual seed must declare its provenance")
        print("changed" if write_map(root, value) else "unchanged")
    except (OSError, ValueError, TypeError, KeyError):
        # Exceptions may contain private paths or raw data: never echo them.
        parser.exit(1, "machine-map: invalid or unavailable private inventory input\n")


if __name__ == "__main__":
    main()
