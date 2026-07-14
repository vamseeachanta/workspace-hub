#!/usr/bin/env python3
"""Emit a deterministic, byte-capped cross-provider memory read-back slice.

Only the git-tracked ``.claude/memory`` snapshot is read. Entries are selected
at whole-entry boundaries with protected capacity for institutional knowledge,
operational feedback, and current context.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

CLAUDE_ONLY_SLUGS = (
    "claude_in_chrome",
    "gmail",
    "claude_desktop",
    "gif_creator",
    "chatgpt_share",
    "output_style",
    "mcp_scope",
)
DEFAULT_CAPS = {"codex": 7000, "hermes": 2000, "gemini": 7000}
SUPPORTED_CAP_MIN = min(DEFAULT_CAPS.values())
INSTITUTIONAL_PERCENT = 15
OPERATIONAL_PERCENT = 50
_HEADER = "<!-- MANAGED by curate_readback_slice.py — do not hand-edit; regenerate via bridge-hermes-claude.sh -->\n\n"
_INDEX_RE = re.compile(r"^- \[(?P<title>.+?)\]\((?P<slug>[^)]+?)\.md\)\s*—\s*(?P<desc>.*)$")
_STALE_TERMINAL_RE = re.compile(r'\*stale:\s*[^*]+\*\s*$')
_MANIFEST_KEYS = {"schema_version", "must_retain_operational_slugs"}
_DEFAULT_PRIORITY_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "agents" / "memory-readback-priorities.yaml"
)


@dataclass(frozen=True)
class Entry:
    text: str
    byte_length: int
    ordinal: int
    slug: str | None
    source: str
    entry_class: str


def _byte_len(text: str) -> int:
    return len(text.encode("utf-8"))


def _truncate_utf8(text: str, cap: int) -> str:
    return text.encode("utf-8")[: max(cap, 0)].decode("utf-8", errors="ignore")


def _is_claude_only(slug: str) -> bool:
    return any(token in slug for token in CLAUDE_ONLY_SLUGS)


def _entry(text: str, ordinal: int, slug: str | None, source: str, entry_class: str) -> Entry:
    normalized = text.rstrip("\n") + "\n"
    return Entry(normalized, _byte_len(normalized), ordinal, slug, source, entry_class)


def _collect_entries(source_dir: Path) -> list[Entry]:
    """Collect auto-memory rows first, then eligible top-level knowledge bullets."""
    entries: list[Entry] = []
    auto = source_dir / "claude-auto-memory.md"
    if auto.exists():
        for line in auto.read_text(encoding="utf-8", errors="replace").splitlines():
            match = _INDEX_RE.match(line.strip())
            if not match:
                continue
            slug = match.group("slug")
            if _is_claude_only(slug):
                continue
            entry_class = "operational" if slug.startswith("feedback_") else "context"
            entries.append(_entry(line.strip(), len(entries), slug, "auto-memory", entry_class))

    knowledge = source_dir / "KNOWLEDGE.md"
    if knowledge.exists():
        for line in knowledge.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("- ") or _STALE_TERMINAL_RE.search(line):
                continue
            entries.append(_entry(line, len(entries), None, "knowledge", "institutional"))
    return entries


def _omitted_marker(count: int) -> str:
    noun = "entry" if count == 1 else "entries"
    return f"_[{count} {noun} omitted: oversize/over-cap]_\n"


def _class_allocations(usable_budget: int) -> dict[str, int]:
    institutional = usable_budget * INSTITUTIONAL_PERCENT // 100
    operational = usable_budget * OPERATIONAL_PERCENT // 100
    return {
        "institutional": institutional,
        "operational": operational,
        "context": usable_budget - institutional - operational,
    }


def _load_priority_slugs(path: Path) -> tuple[str, ...]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"invalid priority manifest {path}: {exc}") from exc
    if not isinstance(payload, dict) or set(payload) != _MANIFEST_KEYS:
        raise ValueError(f"priority manifest must contain exactly {sorted(_MANIFEST_KEYS)}")
    if payload["schema_version"] != 1:
        raise ValueError("priority manifest schema_version must be 1")
    slugs = payload["must_retain_operational_slugs"]
    if not isinstance(slugs, list) or any(not isinstance(slug, str) or not slug for slug in slugs):
        raise ValueError("must_retain_operational_slugs must be a list of non-empty strings")
    return _validate_priority_slug_list(tuple(slugs))


def _validate_priority_slug_list(slugs: tuple[str, ...]) -> tuple[str, ...]:
    if any(not isinstance(slug, str) or not slug for slug in slugs):
        raise ValueError("priority slugs must be non-empty strings")
    if len(slugs) != len(set(slugs)):
        raise ValueError("priority manifest contains duplicate slugs")
    if any(not slug.startswith("feedback_") for slug in slugs):
        raise ValueError("priority manifest slugs must classify as operational feedback")
    if any(_is_claude_only(slug) for slug in slugs):
        raise ValueError("priority manifest contains a Claude-only filtered slug")
    return slugs


def _validate_priorities(
    entries: list[Entry], priority_slugs: tuple[str, ...], operational_budget: int
) -> list[Entry]:
    by_slug: dict[str, list[Entry]] = {}
    for entry in entries:
        if entry.slug in priority_slugs:
            by_slug.setdefault(entry.slug or "", []).append(entry)
    missing = [slug for slug in priority_slugs if slug not in by_slug]
    duplicated = [slug for slug, matches in by_slug.items() if len(matches) != 1]
    if missing:
        raise ValueError(f"priority slug missing or filtered from source: {', '.join(missing)}")
    if duplicated:
        raise ValueError(f"priority slug duplicated in source: {', '.join(duplicated)}")
    selected = [by_slug[slug][0] for slug in priority_slugs]
    required_bytes = sum(entry.byte_length for entry in selected)
    if required_bytes > operational_budget:
        raise ValueError(
            f"priority entries require {required_bytes} bytes, exceeding operational reservation "
            f"of {operational_budget} bytes"
        )
    return selected


def _pack_within(entries: Iterable[Entry], budget: int, selected: set[int]) -> int:
    used = 0
    for entry in entries:
        if entry.ordinal in selected or entry.byte_length > budget - used:
            continue
        selected.add(entry.ordinal)
        used += entry.byte_length
    return used


def _select_supported(
    entries: list[Entry], usable: int, priority_slugs: tuple[str, ...]
) -> set[int]:
    allocations = _class_allocations(usable)
    required = _validate_priorities(entries, priority_slugs, allocations["operational"])
    selected = {entry.ordinal for entry in required}
    used_by_class = {
        "institutional": 0,
        "operational": sum(entry.byte_length for entry in required),
        "context": 0,
    }
    for entry_class in ("institutional", "operational", "context"):
        class_entries = (entry for entry in entries if entry.entry_class == entry_class)
        remaining = allocations[entry_class] - used_by_class[entry_class]
        used_by_class[entry_class] += _pack_within(class_entries, remaining, selected)

    selected_bytes = sum(entry.byte_length for entry in entries if entry.ordinal in selected)
    _pack_within(entries, usable - selected_bytes, selected)
    return selected


def curate(
    source_dir,
    target: str,
    cap: int,
    *,
    priority_slugs: tuple[str, ...] | None = None,
    priority_path: Path | None = None,
) -> str:
    """Build a capped slice; supported production caps enforce priorities fail-closed."""
    entries = _collect_entries(Path(source_dir))
    header_bytes = _byte_len(_HEADER)
    marker_reserve = _byte_len(_omitted_marker(len(entries))) if entries else 0
    usable = max(0, cap - header_bytes - marker_reserve)

    # Sub-production custom caps are diagnostic: preserve bounded legacy behavior
    # without claiming manifest-priority or three-class guarantees.
    if cap < SUPPORTED_CAP_MIN:
        selected: set[int] = set()
        _pack_within(entries, usable, selected)
    else:
        if priority_slugs is not None and priority_path is not None:
            raise ValueError("provide priority_slugs or priority_path, not both")
        priorities = (
            _validate_priority_slug_list(tuple(priority_slugs))
            if priority_slugs is not None
            else _load_priority_slugs(priority_path or _DEFAULT_PRIORITY_PATH)
        )
        selected = _select_supported(entries, usable, priorities)

    chosen = sorted((entry for entry in entries if entry.ordinal in selected), key=lambda entry: entry.ordinal)
    omitted = len(entries) - len(chosen)
    body = _HEADER + "".join(entry.text for entry in chosen)
    if omitted:
        body += _omitted_marker(omitted)
    if _byte_len(body) > cap:
        # This only applies to deliberately degraded tiny caps; supported caps
        # reserve the pessimistic maximum-count marker before packing.
        return _truncate_utf8(body, cap)
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=list(DEFAULT_CAPS), required=True)
    parser.add_argument("--source-dir", default=".claude/memory")
    parser.add_argument("--cap", type=int, default=0, help="UTF-8 byte cap (0 = target default)")
    args = parser.parse_args()
    sys.stdout.write(curate(args.source_dir, args.target, args.cap or DEFAULT_CAPS[args.target]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
