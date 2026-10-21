#!/usr/bin/env python3
"""Build closure-record drafts from an explicitly bounded issue snapshot.

Source: docs/governance/issue-closing-procedure.md, A.4, C.3, C.4 and D.1.
No engineering constants or numerical acceptance criteria are introduced.
The only optional network operation verifies issue references with GET requests.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import subprocess
import sys
import time
from collections.abc import Callable
from functools import partial
from typing import TextIO

import check_issue_closures as checker

IDENTITY = re.compile(r"([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#([1-9][0-9]*)\Z")
SUCCESSOR_WORDS = re.compile(r"\b(duplicate|superseded)\b", re.IGNORECASE)


def target(identity: str) -> tuple[str, int]:
    match = IDENTITY.fullmatch(identity) if isinstance(identity, str) else None
    if not match or any(part in {".", ".."} for part in match[1].split("/")):
        raise ValueError("issue identity must be repository/slug#positive-number")
    return match[1], int(match[2])


def identity(issue: dict) -> str:
    value = f"{issue['repository_slug']}#{issue['number']}"
    target(value)
    return value


def _terminal(start: str, index: dict, mappings: dict) -> tuple[str | None, str]:
    visited = set()
    current = start
    while current in index and current not in visited:
        visited.add(current)
        item = index[current]
        if item.get("state", "").lower() == "open" and not item.get("reopened"):
            return current, "open"
        if item.get("state", "").lower() != "closed":
            break
        # A.4: a COMPLETED state alone is insufficient; all closure rules apply.
        if checker.evaluate_issue(item, list(index.values()))["verdict"] == "PASS":
            return current, "properly closed"
        current = mappings.get(current)
    return None, "unresolved"


def _recovery(entry: dict) -> dict:
    original = entry.get("original_body")
    verified = (entry.get("original_verified") is True
                and isinstance(original, str) and bool(entry.get("original_source")))
    replacing = entry.get("replacing_scope")
    return {
        "issue": entry["issue"],
        "status": "verified original supplied" if verified else checker.NOT_EVALUATED,
        "original_source": entry.get("original_source"),
        "restore_body": original if verified else None,
        "draft_comment": (
            "Restore the verified original body only after maintainer approval."
            if verified else
            "Restoration is NOT_EVALUATED: an exact original body with a verified source is required; "
            "an edit summary does not establish the original body."
        ),
        "new_issue_body": (
            f"Replacement scope separated from {entry['issue']}.\n\n{replacing}"
            if replacing else "NOT_EVALUATED: replacement scope has not been supplied."
        ),
    }


def _retirement(entry: dict, index: dict) -> dict:
    action = entry.get("action")
    reason = entry.get("reason")
    reference = entry.get("retirement_reference")
    destination = entry.get("destination")
    qualified = bool(reason) and (
        (action == "close" and bool(reference) and reference in index)
        or (action == "move" and destination != entry["issue"]
            and destination in index and index[destination].get("state", "").lower() == "open")
    )
    return {**entry, "status": "proposed" if qualified else checker.NOT_EVALUATED,
            "draft_comment": (
                f"Proposed {action}: {reason}. Reference: {reference or destination}."
                if qualified else "NOT_EVALUATED: a reason and retirement reference or open destination are required."
            )}


def build_drafts(data: dict) -> dict:
    """Prepare proposals; supplied metadata is evidence to review, not authority."""
    issues = [checker.normalize_issue(item) for item in data.get("issues", [])]
    index = {identity(item): item for item in issues}
    if len(index) != len(issues):
        raise ValueError("duplicate issue identity")
    mappings = data.get("successors", {})
    refs = set(index)
    for source, destination in mappings.items():
        target(source)
        target(destination)
        refs.update((source, destination))
    output = {"draft_only": True, "successors": [], "recoveries": [],
              "imports": [], "retired": [], "decisions": [],
              "reference_validation": checker.NOT_EVALUATED}

    def decision(issue_ref: str, action: str) -> None:
        output["decisions"].append({"issue": issue_ref, "question": f"{action}? Yes / No"})

    for ref, item in sorted(index.items()):
        if item.get("state", "").lower() != "closed":
            continue
        if item["state_reason"] == "DUPLICATE" or SUCCESSOR_WORDS.search(checker.text_blob(item)):
            successor, status = _terminal(mappings.get(ref), index, mappings)
            if successor == ref:
                successor, status = None, "unresolved"
            draft = (f"Proposed successor: {successor} ({status}); confirm that unfinished scope is carried forward."
                     if successor else "No qualified successor is established. Proposed disposition: none: reopen.")
            output["successors"].append({"issue": ref, "successor": successor or "none: reopen",
                                         "status": status, "draft_comment": draft})
            decision(ref, f"Approve the proposed successor disposition for {ref}")
        import_rule = checker.check_import_closure(item)
        delivered, tests, _ = checker.evidence_status(item)
        if import_rule.verdict == "FAIL" and not (delivered and tests):
            output["imports"].append({"issue": ref, "proposed_label": "closure:unverified",
                                      "draft_comment": "Delivery is not established by the supplied evidence; propose closure:unverified pending assessment."})
            decision(ref, f"Propose closure:unverified for {ref}")

    for entry in data.get("recoveries", []):
        target(entry["issue"])
        if entry["issue"] not in index:
            raise ValueError("recovery issue is outside the snapshot")
        output["recoveries"].append(_recovery(entry))
        decision(entry["issue"], f"Restore the original body of {entry['issue']} once source verification is complete")
        decision(entry["issue"], f"Create a separate issue for the replacement scope of {entry['issue']}")

    for entry in data.get("retired", []):
        if entry["issue"] not in index or index[entry["issue"]].get("state", "").lower() != "open":
            raise ValueError("retirement triage requires an open issue in the snapshot")
        for key in ("retirement_reference", "destination"):
            if entry.get(key):
                target(entry[key])
                refs.add(entry[key])
        output["retired"].append(_retirement(entry, index))
        decision(entry["issue"], f"Approve retirement disposition for {entry['issue']}")

    # Restored bodies and replacement scope are proposed text; closure evidence
    # stays with the source record and may cite PRs rather than issue identities.
    origins = {ref: "structured" for ref in refs}
    for item in output["recoveries"]:
        repository, _ = target(item["issue"])
        for key in ("restore_body", "new_issue_body"):
            for mentioned in checker.issue_references(item.get(key) or ""):
                ref = mentioned if "#" in mentioned else f"{repository}#{mentioned}"
                target(ref)
                refs.add(ref)
                origins.setdefault(ref, "proposed_text")
    output["references"] = sorted(refs)
    output["reference_origins"] = {ref: origins[ref] for ref in sorted(refs)}
    output["coverage"] = data.get("coverage", "Supplied snapshot only; exhaustive collection is not established.")
    return output


def read_issue(repository: str, number: int, *, retries: int = 5,
               retry_delay: float = 60) -> dict:
    """Read one issue; retry only transient server failures, never mutations."""
    # Operational defaults follow the transient-server-error retry policy.
    for attempt in range(retries + 1):
        result = subprocess.run(["gh", "api", "--method", "GET",
                                 f"repos/{repository}/issues/{number}"],
                                capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return json.loads(result.stdout)
        if attempt < retries and re.search(r"\bHTTP (502|503|504)\b", result.stderr):
            time.sleep(retry_delay)
            continue
        raise RuntimeError("Issue API request failed; reference remains unverified")
    raise RuntimeError("Issue API retries exhausted")


def verify_references(refs: list[str], reader: Callable = read_issue, *,
                      origins: dict[str, str] | None = None) -> dict:
    results = {}
    for ref in sorted(set(refs)):
        repository, number = target(ref)
        try:
            raw = reader(repository, number)
            if not isinstance(raw, dict):
                results[ref] = {"status": "FAIL", "state": None}
                continue
            canonical = f"https://github.com/{repository}/issues/{number}"
            valid = (type(raw.get("number")) is int and raw["number"] == number and "pull_request" not in raw
                     and str(raw.get("html_url", "")).lower() == canonical.lower())
            text_pull = ((origins or {}).get(ref) == "proposed_text"
                         and type(raw.get("number")) is int and raw["number"] == number and "pull_request" in raw
                         and str(raw.get("html_url", "")).lower()
                         == f"https://github.com/{repository}/pull/{number}".lower())
            status = "PASS (pull request)" if text_pull else "PASS" if valid else "FAIL"
            results[ref] = {"status": status,
                            "state": raw.get("state") if status.startswith("PASS") else None}
        except (RuntimeError, json.JSONDecodeError):
            results[ref] = {"status": checker.NOT_EVALUATED, "state": None}
    return results


def write_successor_csv(rows: list[dict], stream: TextIO) -> None:
    writer = csv.DictWriter(stream, fieldnames=["issue", "successor", "status", "draft_comment"],
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-live", action="store_true", help="GET each cited issue through gh.")
    parser.add_argument("--successor-csv", action="store_true", help="Print successor CSV instead of JSON.")
    parser.add_argument("--retries", type=int, default=5,
                        help="Retries after the first GET for HTTP 502/503/504 (0 to 10; default: 5).")
    parser.add_argument("--retry-delay", type=float, default=60,
                        help="Seconds between transient-error retries (0 to 300; default: 60).")
    args = parser.parse_args(argv)
    if not 0 <= args.retries <= 10:
        parser.error("--retries must be between 0 and 10")
    if not math.isfinite(args.retry_delay) or not 0 <= args.retry_delay <= 300:
        parser.error("--retry-delay must be finite and between 0 and 300")
    try:
        result = build_drafts(json.load(sys.stdin))
    except ValueError as exc:
        parser.error(str(exc))
    failed = False
    if args.verify_live:
        result["reference_validation"] = verify_references(
            result["references"], partial(read_issue, retries=args.retries, retry_delay=args.retry_delay),
            origins=result["reference_origins"])
        failed = any(row["status"] not in ("PASS", "PASS (pull request)") for row in result["reference_validation"].values())
    if args.successor_csv:
        write_successor_csv(result["successors"], sys.stdout)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
