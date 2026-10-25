# /// script
# dependencies = ["pyyaml"]
# ///
"""Read a catalog, compute a public-safe delta and prepare human review material.

Policy sources: issue 3302 (weekly draft-only workflow), issue 3305
(canonical-first projection), and docs/architecture/agent-data-handling-contract.md.
No network, subprocess, repository edits, scheduling or publication is performed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STATUSES = {"live_public", "live_private", "internal", "roadmap"}
SURFACES = {"resume", "linkedin", "website", "readme"}
# Residency mapping is the contract in issues 3302/3305, not delivery evidence.
RESIDENCY = {"public-sandbox": "live_public", "client-wiki": "live_private", "none": "internal"}
TOKEN = re.compile(r"[a-z][a-z0-9_:-]*\Z")


def token(value):
    if not isinstance(value, str) or not TOKEN.fullmatch(value):
        raise ValueError("invalid catalog identifier")
    return value


def mapping(value):
    if not isinstance(value, dict):
        raise TypeError("expected mapping")
    return value


def array(value):
    if not isinstance(value, list):
        raise TypeError("expected list")
    return value


def report_url(value):
    """Accept concrete HTTPS locators; never copy credentials or URL parameters."""
    if not isinstance(value, str) or any(c in value for c in "<> {}\\\r\n\t"):
        return False
    try:
        url = urlsplit(value)
        return bool(url.scheme == "https" and url.hostname and url.path
                    and not url.username and not url.password and not url.query
                    and not url.fragment and "..." not in url.path)
    except ValueError:
        return False


def normalize_canonical(catalog, evidence=None):
    catalog = mapping(catalog)
    evidence = mapping(evidence if evidence is not None else {})
    rows = array(catalog.get("records"))
    count = catalog.get("private_internal_count", 0)
    if type(count) is not int or count < 0:
        raise ValueError("invalid private aggregate count")
    paths, seen = [], set()
    for row in rows:
        row = mapping(row)
        status = row.get("status")
        if status not in STATUSES:
            raise ValueError("unknown catalog status")
        # Reject private fields before reading or copying their identifiers.
        if status in {"live_private", "internal"}:
            count += 1
            continue
        ref = token(row.get("ref"))
        if ref in seen:
            raise ValueError("duplicate public identifier")
        seen.add(ref)
        domain = row.get("domain")
        if domain is not None:
            token(domain)
        subdomains = sorted({token(s) for s in array(row.get("subdomains", []))})
        kind = row.get("kind")
        if kind not in {"workflow", "roadmap"}:
            raise ValueError("invalid public row kind")
        if kind == "roadmap" and status != "roadmap":
            raise ValueError("roadmap row cannot carry live status")
        proof = evidence.get(ref, {})
        mapping(proof)
        url = proof.get("public_report_url")
        claimable = status == "live_public" and proof.get("reviewed") is True and report_url(url)
        item = {"ref": ref, "kind": kind, "channel_domain": domain,
                "subdomains": subdomains, "status": status,
                "claimable_public": bool(claimable),
                "claim_check": "EVALUATED" if claimable else "NOT_EVALUATED"}
        if claimable:
            item["public_report_url"] = url
        paths.append(item)
    return {"paths": sorted(paths, key=lambda p: p["ref"]), "private_internal_count": count}


def normalize_routing(catalog, evidence=None):
    catalog = mapping(catalog)
    workflows = mapping(catalog.get("workflows"))
    bound = mapping(catalog.get("channel_domain_subdomains"))
    rows, covered = [], set()
    for ref, workflow in workflows.items():
        workflow = mapping(workflow)
        status = RESIDENCY.get(workflow.get("artifact_residency"))
        if status is None:
            raise ValueError("unknown artifact residency")
        route = mapping(workflow.get("route") or {})
        domain = route.get("channel_domain")
        if domain:
            covered.add(domain)
        # Hidden rows contribute only to an aggregate; no descriptions or scopes survive.
        row = {"status": status}
        if status == "live_public":
            row.update(ref=ref, kind="workflow", domain=domain,
                       subdomains=route.get("subdomains") or [])
        rows.append(row)
    for domain, subdomains in bound.items():
        if domain not in covered:
            rows.append({"ref": f"roadmap:{token(domain)}", "kind": "roadmap",
                         "domain": domain, "subdomains": subdomains or [], "status": "roadmap"})
    return normalize_canonical({"records": rows}, evidence)


def normalize_snapshot(snapshot):
    """Validate previous state through the same whitelist; never echo raw snapshot data."""
    snapshot = mapping(snapshot)
    rows, evidence = [], {}
    for p in array(snapshot.get("paths")):
        p = mapping(p)
        rows.append({**p, "domain": p.get("channel_domain")})
        if p.get("claimable_public") is True:
            evidence[p.get("ref")] = {"public_report_url": p.get("public_report_url"), "reviewed": True}
    return normalize_canonical({"records": rows,
                                "private_internal_count": snapshot.get("private_internal_count", 0)},
                               evidence)


def compute_delta(current, snapshot, *, evidence_available=True):
    current = normalize_snapshot(current)
    snapshot = normalize_snapshot(snapshot)
    before = {p["ref"]: p for p in snapshot["paths"]}
    after = {p["ref"]: p for p in current["paths"]}
    new = sorted(after.keys() - before.keys())
    removed = sorted(before.keys() - after.keys())
    common = sorted(after.keys() & before.keys())
    changed = [{"ref": r, "from": before[r]["status"], "to": after[r]["status"]}
               for r in common if before[r]["status"] != after[r]["status"]]
    eligible_before = {r for r, p in before.items() if p["claimable_public"]}
    catalog_withdrawals = {r for r in eligible_before
                           if r not in after or after[r]["status"] != "live_public"}
    eligible_after = {r for r, p in after.items() if p["claimable_public"]} if evidence_available else set()
    evidence_fields = {"claimable_public", "claim_check", "public_report_url"}

    def comparable(row):
        return row if evidence_available else {k: v for k, v in row.items() if k not in evidence_fields}
    # Issue 3302: weekly additions/removals are set differences, counts are cardinalities.
    return {"claim_check": "EVALUATED" if evidence_available else "NOT_EVALUATED",
            "claim_reason": ("The evidence mapping was read." if evidence_available
                             else "Reviewed report evidence is unavailable."),
            "counts": {"current_total": len(after),
                       "current_live_public": sum(p["status"] == "live_public" for p in after.values()),
                       "claimable_public": len(eligible_after) if evidence_available else None, "new": len(new),
                       "removed": len(removed), "status_changed": len(changed),
                       "private_internal_count": current["private_internal_count"]},
            "new_paths": [after[r] for r in new],
            "new_live_public": [after[r] for r in sorted(eligible_after - eligible_before)],
            "new_roadmap": [after[r] for r in new if after[r]["status"] == "roadmap"],
            "removed_paths": [before[r] for r in removed], "status_changed": changed,
            "metadata_changed": [r for r in common if comparable(before[r]) != comparable(after[r])],
            "withdrawn_public": [before[r] for r in sorted(
                eligible_before - eligible_after if evidence_available else catalog_withdrawals)]}


def draft_packet(delta):
    additions = [{"ref": p["ref"], "public_report_url": p["public_report_url"]}
                 for p in delta["new_live_public"]]
    return {"publish_allowed": False, "public_additions": additions,
            "claim_check": delta["claim_check"], "claim_reason": delta["claim_reason"],
            "public_count": delta["counts"]["claimable_public"],
            "withdrawals": [p["ref"] for p in delta["withdrawn_public"]],
            "review_metadata": delta["metadata_changed"],
            "new_paths": delta["new_paths"], "removed_paths": delta["removed_paths"],
            "status_changed": delta["status_changed"],
            "surfaces": {
                "resume": "Draft recent-work bullets supported by each reviewed report.",
                "linkedin": "Draft Featured links and About count; submit as a document for review.",
                "website": "Draft API catalog rows with reviewed report links and count.",
                "readme": "Draft catalog-link counts using only the public_count."},
            "required_gates": ["messaging review", "rights and personal-data review",
                               "secret scan", "open draft PR per repository"]}


def digest(value):
    # Same canonical JSON encoding as the repository data-handling contract.
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def validate_receipt(receipt, current, previous):
    """Validate recorded review evidence; local JSON cannot authenticate remote PR state."""
    receipt = mapping(receipt)
    if (receipt.get("current_digest") != digest(current)
            or receipt.get("previous_digest") != digest(previous)
            or receipt.get("content_reviewed") is not True):
        raise ValueError("review receipt does not match this comparison")
    covered = set()
    for pr in array(receipt.get("draft_prs")):
        pr = mapping(pr)
        url = pr.get("url")
        if not isinstance(url, str) or not re.fullmatch(
                r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/pull/[1-9][0-9]*", url):
            raise ValueError("invalid draft PR locator")
        if pr.get("isDraft") is not True or pr.get("state") != "OPEN":
            raise ValueError("all recorded PRs must be open drafts")
        for surface in array(pr.get("surfaces")):
            if surface not in SURFACES:
                raise ValueError("unknown surface in review receipt")
            covered.add(surface)
    if covered != SURFACES:
        raise ValueError("draft PR evidence must cover every surface")


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON field")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def read_yaml(path):
    class UniqueLoader(yaml.SafeLoader):
        pass

    def unique(loader, node):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node)
            if key in result:
                raise ValueError("duplicate YAML field")
            result[key] = loader.construct_object(value_node)
        return result

    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique)
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueLoader)


def atomic_snapshot(path, value):
    """Replace only an existing snapshot; failed writes preserve previous state."""
    if not path.is_file():
        raise ValueError("snapshot update requires an existing regular file")
    linked = any(p.is_symlink() or getattr(p, "is_junction", lambda: False)()
                 or getattr(p.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
                 for p in (path, *path.absolute().parents))
    if linked:
        raise ValueError("snapshot update requires an existing regular file")
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, encoding="utf-8",
                                     newline="\n", prefix=".snapshot-", delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("auto", "canonical", "derive"), default="auto")
    sibling = Path(os.environ.get("DECKHAND_REPO", ROOT.parent / "deckhand"))
    parser.add_argument("--canonical", type=Path, default=Path(os.environ.get(
        "DECKHAND_API_CATALOG", sibling / "docs/deckhand/api-catalog.json")))
    parser.add_argument("--catalog", type=Path, default=Path(os.environ.get(
        "DECKHAND_CATALOG", sibling / "config/deckhand/routing/domain-workflows.yaml")))
    parser.add_argument("--snapshot", type=Path, default=HERE / "state/api-catalog-snapshot.json")
    parser.add_argument("--evidence", type=lambda value: Path(value) if value else None,
                        default=os.environ.get("DECKHAND_API_EVIDENCE"),
                        help="Private reviewed evidence; defaults to DECKHAND_API_EVIDENCE")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--emit-current", action="store_true")
    mode.add_argument("--draft-packet", action="store_true")
    mode.add_argument("--update-snapshot", action="store_true")
    parser.add_argument("--review-receipt", type=Path)
    args = parser.parse_args(argv)
    try:
        try:
            evidence = mapping(read_json(args.evidence)) if args.evidence else None
        except OSError:
            evidence = None
        evidence_available = evidence is not None
        source = args.source
        if source == "auto":
            source = "canonical" if args.canonical.exists() else "derive"
        if source == "canonical":
            current = normalize_canonical(read_json(args.canonical), evidence)
        else:
            current = normalize_routing(read_yaml(args.catalog), evidence)
        current["source"] = source
        previous = read_json(args.snapshot) if args.snapshot.exists() else {"paths": []}
        delta = compute_delta(current, previous, evidence_available=evidence_available)
        output = current if args.emit_current else draft_packet(delta) if args.draft_packet else delta
        output = {**output, "current_digest": digest(current), "previous_digest": digest(previous)}
        if args.update_snapshot:
            if not evidence_available:
                raise ValueError("snapshot update requires available reviewed evidence")
            if not args.review_receipt:
                raise ValueError("snapshot update requires a review receipt")
            validate_receipt(read_json(args.review_receipt), current, previous)
            atomic_snapshot(args.snapshot, current)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, yaml.YAMLError):
        # Parser and filesystem exception messages may contain private text or absolute paths.
        print("Catalog comparison failed: check input schema, source availability and review evidence.",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
