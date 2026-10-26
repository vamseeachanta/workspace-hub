#!/usr/bin/env python3
"""Offline, exact-path coverage of an explicit counted-read snapshot.

Registry input is YAML or JSON with an ``assets`` list. Each asset requires a
unique ``asset_key`` and ``canonical_path``; ``human_entry_point`` and
``agent_entry_point`` may be absent or null. Other registry metadata is ignored.
Paths shared by different assets are ambiguous and rejected, even if unread.

Counted-read JSON has this explicit envelope (synthetic example):
  {"scope": "fixed observation window", "completeness": "partial",
   "providers": {"example": {"top_reads": [{"path": "docs/a", "count": 3}]}}}
Each provider supplies exactly one of ``reads`` or ``top_reads``. Counts are
positive integers, with one row per path per provider. ``top_reads`` requires
``partial`` completeness. Raw audit output must be wrapped deliberately; it is
never assumed complete. ``complete`` asserts completeness only within ``scope``;
the reporter cannot independently verify that assertion or infer global coverage.

Coverage is covered read counts / all supplied read counts, not unique paths or
registry assets. Percent means multiplication by 100 by definition; a decimal
place scales by another 10. Integer half-up rounding avoids float overflow and
represents one-decimal percentages consistently. Empty denominators yield null.
Unresolved means no exact registry match, not a missing file or temporal drift.
No paths are resolved, opened or normalized except the explicit CLI file paths.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

import yaml


PATH_FIELDS = ("canonical_path", "human_entry_point", "agent_entry_point")
SCOPE_NOTE = "alias, external-candidate and historical-trend classification are deferred"


def _unique_mapping(pairs):
    result = {}
    for key, value in pairs:
        try:
            if key in result:
                raise ValueError("duplicate mapping key")
            result[key] = value
        except TypeError as error:
            raise ValueError("mapping keys must be scalar") from error
    return result


class _RegistryLoader(yaml.SafeLoader):
    """Reject duplicate keys before YAML parsing can silently discard them."""


def _yaml_mapping(loader, node):
    return _unique_mapping(
        (loader.construct_object(key), loader.construct_object(value))
        for key, value in node.value
    )


_RegistryLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _yaml_mapping)


def load_registry(path: Path) -> dict:
    """Read only the named registry; JSON is also valid YAML."""
    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=_RegistryLoader)
    except yaml.YAMLError as error:
        raise ValueError("invalid registry YAML or JSON") from error


def _reject_constant(_value):
    raise ValueError("non-finite JSON values are invalid")


def load_counted_reads(path: Path) -> dict:
    return json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=_unique_mapping,
        parse_constant=_reject_constant,
    )


def _text(value, label):
    if not isinstance(value, str) or not value or value != value.strip() or not value.isprintable():
        raise ValueError(f"{label} must be nonempty text without surrounding whitespace or controls")
    return value


def _registry_index(registry):
    if not isinstance(registry, dict) or not isinstance(registry.get("assets"), list):
        raise ValueError("registry must contain an assets list")
    keys = set()
    index = {}
    for asset in registry["assets"]:
        if not isinstance(asset, dict):
            raise ValueError("asset must be a mapping")
        key = _text(asset.get("asset_key"), "asset_key")
        if key in keys:
            raise ValueError("duplicate asset_key")
        keys.add(key)
        for field in PATH_FIELDS:
            path = asset.get(field)
            if field != "canonical_path" and path is None:
                continue
            path = _text(path, field)
            if path in index and index[path]["asset_key"] != key:
                raise ValueError("ambiguous registry path shared by different assets")
            entry = index.setdefault(path, {"asset_key": key, "matched_fields": []})
            entry["matched_fields"].append(field)
    for entry in index.values():
        entry["matched_fields"].sort()
    return index


def _percentage(covered, total):
    if not total:
        return None
    # Definition in module contract: 100 percent units * 10 decimal units.
    tenths, remainder = divmod(covered * 1000, total)
    if remainder * 2 >= total:  # Half-up: twice the remainder reaches one divisor.
        tenths += 1
    return tenths / 10


def _totals(covered, unresolved, completeness):
    total = covered + unresolved
    percent = _percentage(covered, total)
    return {
        "read_count": total,
        "covered_count": covered,
        "unresolved_count": unresolved,
        "observed_coverage_percent": percent,
        "scope_coverage_percent": percent if completeness == "complete" else None,
        "state": completeness if total else "empty",
    }


def build_report(registry: dict, snapshot: dict) -> dict:
    """Validate the entire input before producing a deterministic report."""
    index = _registry_index(registry)
    if not isinstance(snapshot, dict) or set(snapshot) != {"scope", "completeness", "providers"}:
        raise ValueError("snapshot requires exactly scope, completeness and providers")
    scope = _text(snapshot["scope"], "scope")
    completeness = snapshot["completeness"]
    if completeness not in ("complete", "partial"):
        raise ValueError("completeness must be complete or partial")
    providers = snapshot["providers"]
    if not isinstance(providers, dict):
        raise ValueError("providers must be a mapping")
    for provider in providers:
        _text(provider, "provider")

    results = {}
    covered_total = unresolved_total = 0
    for provider in sorted(providers):
        data = providers[provider]
        if not isinstance(data, dict) or set(data) not in ({"reads"}, {"top_reads"}):
            raise ValueError("provider requires exactly one reads or top_reads list")
        field = next(iter(data))
        if field == "top_reads" and completeness != "partial":
            raise ValueError("top_reads requires partial completeness")
        rows = data[field]
        if not isinstance(rows, list):
            raise ValueError("counted reads must be a list")
        observations = []
        seen = set()
        covered = unresolved = 0
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"path", "count"}:
                raise ValueError("read row requires exactly path and count")
            path = _text(row["path"], "read path")
            count = row["count"]
            if type(count) is not int or count <= 0:
                raise ValueError("read count must be a positive integer")
            if path in seen:
                raise ValueError("duplicate read path within provider")
            seen.add(path)
            match = index.get(path)
            if match is None:
                unresolved += count
            else:
                covered += count
            observations.append({
                "path": path, "count": count,
                "asset_key": match["asset_key"] if match else None,
                "matched_fields": list(match["matched_fields"]) if match else [],
            })
        results[provider] = {
            "input_kind": field,
            "totals": _totals(covered, unresolved, completeness),
            "observations": sorted(observations, key=lambda row: row["path"]),
        }
        covered_total += covered
        unresolved_total += unresolved
    return {
        "scope": scope, "completeness": completeness, "scope_note": SCOPE_NOTE,
        "totals": _totals(covered_total, unresolved_total, completeness),
        "providers": results,
    }


def _cell(value):
    text = html.escape(str(value))
    for character in ("\\", "|", "`", "*", "_", "[", "]"):
        text = text.replace(character, "\\" + character)
    return text


def _percent_text(value):
    return "N/A" if value is None else f"{value:.1f}%"


def _total_row(label, totals):
    return (
        f"| {label} | {totals['read_count']} | {totals['covered_count']} | "
        f"{totals['unresolved_count']} | {_percent_text(totals['observed_coverage_percent'])} | "
        f"{_percent_text(totals['scope_coverage_percent'])} | {totals['state']} |"
    )


def render_markdown(report: dict) -> str:
    lines = [
        "# Cross-registry read coverage", "",
        f"Scope: {_cell(report['scope'])}", "",
        f"Completeness: {report['completeness']}", "",
        "Denominator: supplied read counts, not unique paths or registry assets.", "",
        "Partial snapshot: percentages describe only supplied reads; scope coverage is unavailable."
        if report["completeness"] == "partial" else
        "Complete snapshot: scope coverage relies on the supplied completeness assertion.",
        "Neither mode establishes coverage outside the declared scope.", "",
        "Empty input: coverage is N/A; no coverage percentage is established without observations.", "",
        f"Scope note: {report['scope_note']}.", "",
        "| Provider | Reads | Covered | Unresolved | Observed coverage | Scope coverage | State |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for provider, data in report["providers"].items():
        lines.append(_total_row(_cell(provider), data["totals"]))
    lines.extend([_total_row("**Total**", report["totals"]), "", "## Counted observations", "",
                  "Unresolved means no exact match; it does not establish filesystem absence or temporal drift.", "",
                  "| Provider | Path | Reads | Asset | Matching fields |",
                  "| --- | --- | ---: | --- | --- |"])
    for provider, data in report["providers"].items():
        for row in data["observations"]:
            lines.append(
                f"| {_cell(provider)} | {_cell(row['path'])} | {row['count']} | "
                f"{_cell(row['asset_key']) if row['asset_key'] else 'unresolved'} | "
                f"{', '.join(_cell(field) for field in row['matched_fields']) or 'none'} |"
            )
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--counted-reads", required=True, type=Path)
    parser.add_argument("--json-output", required=True, type=Path)
    parser.add_argument("--markdown-output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        paths = [args.registry, args.counted_reads, args.json_output, args.markdown_output]
        resolved = [path.resolve() for path in paths]
        if len(set(resolved)) != len(resolved) or any(
            left.exists() and right.exists() and left.samefile(right)
            for position, left in enumerate(paths) for right in paths[position + 1:]
        ):
            raise ValueError("input and output paths must be distinct")
        report = build_report(load_registry(args.registry), load_counted_reads(args.counted_reads))
        json_text = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        markdown_text = render_markdown(report)
        args.json_output.write_text(json_text, encoding="utf-8")
        args.markdown_output.write_text(markdown_text, encoding="utf-8")
    except (OSError, ValueError) as error:
        # Do not echo input values, source excerpts or filesystem locators.
        parser.error(f"invalid input or output ({type(error).__name__}); no coverage claim made")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
