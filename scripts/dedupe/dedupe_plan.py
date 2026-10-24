"""Produce duplicate-removal candidates as documents only; no commands are executed."""

import argparse
import fnmatch
import html
import shlex
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from dedupe._common import (
        FORMAT_VERSION,
        atomic_write_output,
        distinct_outputs,
        identity,
        json_text,
        read_json,
        valid_digest,
        validate_record,
    )
else:
    from ._common import (
        FORMAT_VERSION,
        atomic_write_output,
        distinct_outputs,
        identity,
        json_text,
        read_json,
        valid_digest,
        validate_record,
    )

NOTICE = (
    "Nothing has been deleted. Removal needs a separate explicit decision by the "
    "maintainer. Recheck both files immediately before any action."
)


def validate_policy(policy):
    if not isinstance(policy, dict):
        raise TypeError("policy must be an object")
    protect = policy.get("protect", [])
    criteria = policy.get("keep_preference", [])
    if not isinstance(protect, list) or not all(isinstance(p, str) for p in protect):
        raise ValueError("protect must be a list of globs")
    if not isinstance(criteria, list):
        raise TypeError("keep_preference must be an ordered list")
    for criterion in criteria:
        if isinstance(criterion, str) and criterion in ("shorter_path", "older_mtime"):
            continue
        if not isinstance(criterion, dict) or len(criterion) != 1:
            raise ValueError("invalid keep preference")
        key = next(iter(criterion))
        if key not in ("labels", "path_prefixes"):
            raise ValueError("unknown keep preference")
        values = criterion[key]
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            raise ValueError("preference values must be a list of strings")
    return criteria, protect


def criterion_value(row, criterion):
    if criterion == "shorter_path":
        return len(row["path"])
    if criterion == "older_mtime":
        return row["mtime"]
    key = next(iter(criterion))
    preferences = criterion[key]
    for index, preference in enumerate(preferences):
        if (key == "labels" and row["label"] == preference) or (
            key == "path_prefixes" and row["path"].startswith(preference)
        ):
            return index
    return len(preferences)


def criterion_name(criterion):
    if isinstance(criterion, str):
        return " ".join(criterion.split("_"))
    return "label order" if "labels" in criterion else "path prefix order"


def make_plan(source, policy):
    criteria, protect = validate_policy(policy)
    if not isinstance(source, dict) or source.get("version") != FORMAT_VERSION:
        raise ValueError("unsupported groups format")
    verified_groups = []
    identities = set()
    for category in ("across_labels", "within_label"):
        if not isinstance(source.get(category), list):
            raise TypeError("missing verified group category")
        for group in source[category]:
            if (
                not isinstance(group, dict)
                or group.get("status") != "verified"
                or group.get("basis") != "full_sha256"
                or not valid_digest(group.get("sha256"))
                or not isinstance(group.get("files"), list)
                or len(group["files"]) < 2
            ):
                raise ValueError("invalid verified group")
            for row in group["files"]:
                validate_record(row)
                if (
                    row.get("manifest_complete") is not True
                    or "error" in row
                    or row["stage"] != "full"
                    or row["sha256"] != group["sha256"]
                    or row["size"] != group.get("size")
                ):
                    raise ValueError(
                        "unverified or inconsistent file in verified group"
                    )
                key = identity(row)
                if key in identities:
                    raise ValueError("repeated file identity")
                identities.add(key)
            verified_groups.append(group)
    candidates = source.get("candidate_groups")
    if not isinstance(candidates, list):
        raise TypeError("missing candidate groups")
    root_keys = sorted(
        {(r["label"], r["root"]) for g in verified_groups for r in g["files"]}
    )
    # README.md, Verification commands: ordinal variables start at one.
    variables = {key: f"ROOT_{index}" for index, key in enumerate(root_keys, start=1)}

    def protected(row):
        qualified = f"{row['label']}:{row['root']}/{row['path']}"
        return any(
            fnmatch.fnmatchcase(row["path"], pattern)
            or fnmatch.fnmatchcase(qualified, pattern)
            for pattern in protect
        )

    def rank(row):
        return tuple(criterion_value(row, c) for c in criteria) + identity(row)

    def shell_path(row):
        variable = variables[(row["label"], row["root"])]
        return '"${' + variable + '}"/' + shlex.quote(row["path"])

    planned = []
    for group in sorted(verified_groups, key=lambda g: (g["size"], g["sha256"])):
        files = sorted(group["files"], key=identity)
        protected_files = [r for r in files if protected(r)]
        keep = min(protected_files or files, key=rank)
        removal = []
        retained = []
        for row in files:
            if row is keep:
                continue
            if protected(row):
                retained.append({**row, "reason": "protected by policy"})
                continue
            reason = "deterministic label/root/path tie-break"
            if protected_files:
                reason = "protected copy retained"
            else:
                for criterion in criteria:
                    if criterion_value(keep, criterion) != criterion_value(
                        row, criterion
                    ):
                        reason = "keep preference: " + criterion_name(criterion)
                        break
            removal.append(
                {
                    **row,
                    "reason": reason,
                    "verification_command": f"sha256sum -- {shell_path(keep)} {shell_path(row)}",
                }
            )
        planned.append(
            {
                "size": group["size"],
                "sha256": group["sha256"],
                "keep": keep,
                "keep_reason": "protected by policy"
                if protected_files
                else (
                    "ordered keep preferences; deterministic label/root/path tie-break"
                ),
                "retained": retained,
                "candidates": removal,
            }
        )
    return {
        "version": FORMAT_VERSION,
        "notice": NOTICE,
        "roots": [
            {"variable": variable, "label": label, "root": root}
            for (label, root), variable in variables.items()
        ],
        "groups": planned,
        "unverified_groups": len(candidates),
    }


def render_markdown(plan):
    def display(row):
        return html.escape(json_text([row["label"], row["root"], row["path"]]))

    lines = [
        "# Dedupe plan",
        "",
        f"**{NOTICE}**",
        "",
        "Candidates are proposals only. Protected copies remain retained.",
        "Hash equality addresses content, not metadata. No action is authorized.",
        "",
        "## Root bindings",
        "",
        (
            "Set each variable to its corresponding root before running a verification "
            "command. Compare both results with the expected digest; a successful command "
            "alone does not establish equality. For roots on separate systems, run each "
            "path's hash at its root and compare the results."
        ),
        "",
    ]
    for root in plan["roots"]:
        lines.append(
            f"- {root['variable']}: label {html.escape(json_text(root['label']))}, "
            f"root index {root['root']}"
        )
    for group in plan["groups"]:
        lines.extend(
            [
                "",
                f"## Content {group['sha256']}",
                "",
                f"Size: {group['size']} bytes.",
                f"Keep: {display(group['keep'])}. Reason: {group['keep_reason']}.",
            ]
        )
        for row in group["retained"]:
            lines.append(f"Retain: {display(row)}. Reason: {row['reason']}.")
        for row in group["candidates"]:
            lines.extend(
                [
                    "",
                    f"REMOVAL CANDIDATE: {display(row)}. Reason: {row['reason']}.",
                    f"Expected SHA-256 for both: {group['sha256']}",
                    "",
                    # Markdown readers normalize line separators, even in code.
                    # Preserve the JSON command; withhold an unfaithful display.
                    (
                        "Verification command withheld: filename contains a line "
                        "separator; inspect the JSON command without normalization."
                        if any(
                            char in row["verification_command"]
                            for char in "\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029"
                        )
                        else "    " + row["verification_command"]
                    ),
                ]
            )
    lines.extend(["", f"Unverified groups excluded: {plan['unverified_groups']}.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("groups")
    parser.add_argument("--policy", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-json", required=True)
    args = parser.parse_args()
    try:
        distinct_outputs([args.out, args.out_json], inputs=[args.groups, args.policy])
        plan = make_plan(read_json(args.groups), read_json(args.policy))
        atomic_write_output(args.out_json, json_text(plan) + "\n")
        atomic_write_output(args.out, render_markdown(plan))
    except (ValueError, TypeError, OSError) as exc:
        parser.exit(2, f"planning failed: {type(exc).__name__}\n")


if __name__ == "__main__":
    main()
