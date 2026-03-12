"""feature_tree.py — Feature WRK tree data model and rendering helpers.

Extracted from dep_graph.py to keep that module under the 400-line hard limit.
"""
import re
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class FeatureTreeItem:
    id: str
    title: str
    status: str
    type: str           # "feature" | "task"
    children: list      # list of child WRK IDs
    parent: str         # parent feature WRK ID or ""
    orchestrator: str
    blocked_by: list


# ---------------------------------------------------------------------------
# Internal helpers (shared with dep_graph.py callers)
# ---------------------------------------------------------------------------

_ALL_QUEUE_DIRS = ("pending", "working", "blocked", "archived", "archive", "done")


def _parse_fm_value(raw: str) -> str:
    """Strip quotes and whitespace from a scalar YAML value."""
    return raw.strip().strip('"').strip("'")


def _parse_inline_list(raw: str) -> list[str]:
    """Parse '[WRK-001, WRK-002]' or 'WRK-001' into a list."""
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [v.strip().strip('"').strip("'") for v in inner.split(",") if v.strip()]
    if raw in ("", "null", "~"):
        return []
    return [raw.strip()]


def _parse_frontmatter_ft(text: str) -> dict:
    """Extract key fields from YAML frontmatter (feature-tree subset)."""
    parts = text.split("---", 2)
    if len(parts) < 2:
        return {}
    fm = parts[1]

    result: dict = {}
    for line in fm.splitlines():
        m = re.match(r"^(\w[\w_-]*):\s*(.*)", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if key == "blocked_by":
            if val.startswith("["):
                result[key] = _parse_inline_list(val)
            elif val:
                result[key] = _parse_inline_list(val)
        else:
            result[key] = _parse_fm_value(val)

    if "blocked_by" not in result:
        block = re.search(r"^blocked_by:\s*\n((?:\s+-[^\n]*\n?)*)", fm, re.MULTILINE)
        if block:
            items = re.findall(r"^\s+-\s+(\S+)", block.group(1), re.MULTILINE)
            result["blocked_by"] = [v.strip('"').strip("'") for v in items]

    return result


def _parse_children_list(fm: dict, raw_text: str) -> list[str]:
    """Extract children: list from frontmatter, supporting inline and block-list."""
    raw = fm.get("children")
    if isinstance(raw, list):
        return [str(c).strip() for c in raw if str(c).strip()]
    if isinstance(raw, str) and raw.strip():
        return _parse_inline_list(raw)
    # Empty scalar or None: try block-list in raw frontmatter text
    parts = raw_text.split("---", 2)
    if len(parts) >= 2:
        block = re.search(
            r"^children:\s*\n((?:\s+-[^\n]*\n?)*)", parts[1], re.MULTILINE
        )
        if block:
            return [
                v.strip().strip('"').strip("'")
                for v in re.findall(r"^\s+-\s+(\S+)", block.group(1), re.MULTILINE)
            ]
    return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def find_wrk_in_queue(wrk_id: str, queue_root: Path) -> "Path | None":
    """Search all queue dirs (including archive/YYYY-MM/ subdirs) for wrk_id.md."""
    for dirname in _ALL_QUEUE_DIRS:
        d = queue_root / dirname
        if not d.is_dir():
            continue
        candidate = d / f"{wrk_id}.md"
        if candidate.exists():
            return candidate
        for sub in d.iterdir():
            if sub.is_dir():
                candidate = sub / f"{wrk_id}.md"
                if candidate.exists():
                    return candidate
    return None


def load_feature_tree(wrk_id: str, queue_root: Path) -> "FeatureTreeItem | None":
    """Load a FeatureTreeItem from any queue directory. Returns None if not found."""
    path = find_wrk_in_queue(wrk_id, queue_root)
    if path is None:
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    fm = _parse_frontmatter_ft(text)
    children = _parse_children_list(fm, text)
    raw_blocked = fm.get("blocked_by", [])
    blocked_by = (
        raw_blocked if isinstance(raw_blocked, list) else _parse_inline_list(str(raw_blocked))
    )
    return FeatureTreeItem(
        id=wrk_id,
        title=str(fm.get("title", "")),
        status=str(fm.get("status", "unknown")),
        type=str(fm.get("type", "task")),
        children=children,
        parent=str(fm.get("parent", "")),
        orchestrator=str(fm.get("orchestrator", "")),
        blocked_by=blocked_by if isinstance(blocked_by, list) else [],
    )


def render_feature_tree(feature: FeatureTreeItem, queue_root: Path) -> str:
    """Render ASCII tree for a feature WRK and its children."""
    lines: list[str] = []
    title_str = f"  {feature.title}" if feature.title else ""
    lines.append(f"{feature.id} [{feature.status}]{title_str}")

    child_ids = feature.children
    for idx, child_id in enumerate(child_ids):
        is_last = idx == len(child_ids) - 1
        prefix = "└──" if is_last else "├──"
        child = load_feature_tree(child_id, queue_root)
        if child is None:
            lines.append(f"{prefix} {child_id} [missing]")
            continue
        parts: list[str] = [f"{prefix} {child_id} [{child.status}]"]
        if child.title:
            parts.append(f"  {child.title}")
        extras: list[str] = []
        if child.blocked_by:
            blockers = (
                ", ".join(child.blocked_by)
                if isinstance(child.blocked_by, list)
                else str(child.blocked_by)
            )
            extras.append(f"blocked_by: {blockers}")
        if child.orchestrator:
            extras.append(f"agent: {child.orchestrator}")
        if extras:
            parts.append(f"  ({', '.join(extras)})")
        lines.append("".join(parts))
    return "\n".join(lines)
