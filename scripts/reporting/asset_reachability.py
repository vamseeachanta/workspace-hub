#!/usr/bin/env python3
"""Plan shared-asset reachability without changing the supplied filesystem.

Proposed local JSON contracts (not publication/provenance manifest adapters):
* Inventory: {"schema":"asset-inventory-v1","assets":["assets/example.svg"]}
* Reference manifest: {"schema":"asset-references-v1","assets":[...]}
* Index: {"schema":"asset-reference-index-v1","publication_status":"succeeded",
  "current":["current.json"],"history":[],"recovery":[]}

All locators are canonical POSIX paths relative to an explicit root. Every
listed file must exist and be regular, with no symlink/reparse components.
The current list must be nonempty; explicitly empty history/recovery lists
assert absence of retained states. Unknown fields/schemas fail closed. Repeated
asset references are set members; duplicate inventory entries are ambiguous.

Referenced = inventory intersect union(current, history, recovery); unreferenced
= inventory minus that union. References outside the inventory are unresolved.
Any invalid input or publication status other than succeeded suppresses the
entire partition and all candidates. JSON output has sorted keys and path lists.

The caller must supply complete lists and a quiescent tree: the planner cannot
establish publication success, discover omitted manifests, or provide an atomic
snapshot against concurrent filesystem changes. Candidates are advisory only.
No asset content is read and no file is deleted, moved, created or linked.
"""

import argparse
import json
import os
import stat
from pathlib import Path, PurePosixPath

from report_provenance import _path, load_manifest


class ReachabilityError(ValueError):
    """The supplied evidence cannot establish a complete partition."""


def _root(value):
    root = Path(value).absolute()
    if ".." in root.parts:
        raise ReachabilityError("invalid root")
    for component in reversed((root, *root.parents)):
        _no_link(component)
    if not root.is_dir():
        raise ReachabilityError("root is not a directory")
    return root.resolve(strict=True)


def _no_link(path):
    metadata = path.lstat()
    if (stat.S_ISLNK(metadata.st_mode)
            or getattr(metadata, "st_file_attributes", 0)
            & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise ReachabilityError("symlink or reparse path rejected")
    return metadata


def _regular_file(root, value):
    value = _path(value)
    candidate = root
    for part in PurePosixPath(value).parts:
        candidate /= part
        metadata = _no_link(candidate)
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(root) or not stat.S_ISREG(metadata.st_mode):
        raise ReachabilityError("path is not a contained regular file")
    return candidate


def _read(root, locator):
    candidate = _regular_file(root, locator)
    # O_NOFOLLOW protects the final open on supporting systems. O_NOATIME avoids
    # access-time updates on Linux; permission failures remain unresolved.
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NOATIME", 0)
    with os.fdopen(os.open(candidate, flags), "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ReachabilityError("manifest is not a regular file")
        return load_manifest(stream.read())


def _document(value, schema, fields):
    if (not isinstance(value, dict) or set(value) != {"schema", *fields}
            or value["schema"] != schema):
        raise ReachabilityError("unsupported or incomplete document")
    return value


def _paths(value):
    if not isinstance(value, list):
        raise ReachabilityError("path list required")
    return [_path(item) for item in value]


def _assets(root, locator, schema):
    document = _document(_read(root, locator), schema, {"assets"})
    paths = _paths(document["assets"])
    for path in paths:
        _regular_file(root, path)
    return paths


def _unresolved(reason):
    return {
        "status": "UNRESOLVED", "dry_run": True, "reason": reason,
        "referenced": [], "unreferenced": [], "prune_candidates": [],
    }


def plan_reachability(root, inventory, references):
    """Return a complete dry-run partition, or no candidates on any input failure.

    inventory and references identify JSON files within root, never implicit
    discovery locations. Raw filesystem errors and malformed locators are not
    included in diagnostics. Existing provenance parsing rejects duplicate JSON
    keys and non-finite values before they can hide references.
    """
    try:
        root = _root(root)
        listed = _assets(root, inventory, "asset-inventory-v1")
        assets = set(listed)
        if len(listed) != len(assets):
            raise ReachabilityError("duplicate inventory path")
        groups = {"current", "history", "recovery"}
        index = _document(
            _read(root, references), "asset-reference-index-v1",
            {"publication_status", *groups},
        )
        if index["publication_status"] != "succeeded":
            raise ReachabilityError("publication success is not established")
        reachable = set()
        for group in sorted(groups):
            manifests = _paths(index[group])
            if group == "current" and not manifests:
                raise ReachabilityError("current manifest list must not be empty")
            for locator in manifests:
                reachable.update(_assets(root, locator, "asset-references-v1"))
        if reachable - assets:
            raise ReachabilityError("reference is absent from inventory")
        unreferenced = sorted(assets - reachable)
        return {
            "status": "RESOLVED", "dry_run": True,
            "referenced": sorted(assets & reachable),
            "unreferenced": unreferenced, "prune_candidates": unreferenced.copy(),
        }
    except ReachabilityError as exc:
        return _unresolved(str(exc))
    except (OSError, ValueError, TypeError, RuntimeError):
        # Includes ProvenanceError, UnicodeError and malformed/deep JSON input.
        return _unresolved("input unavailable, unsafe or invalid")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--references", required=True)
    args = parser.parse_args(argv)
    result = plan_reachability(args.root, args.inventory, args.references)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    # Conventional shell status: zero for success, one for unresolved evidence.
    return 0 if result["status"] == "RESOLVED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
