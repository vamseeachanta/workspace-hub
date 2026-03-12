""":"
exec uv run --no-project python "$0" "$@"
":"""
"""dep_graph.py — WRK dependency graph visualisation.

Reads blocked_by fields from pending/working/blocked WRK items and renders:
  - ASCII critical-path table (to terminal)
  - DOT file (optional, via --dot <path>)
  - Summary line for /work list footer (via --summary)

Usage:
  dep-graph.py [--category <name>] [--critical-path] [--dot <path>] [--summary]
"""
import argparse
import graphlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


class CycleError(Exception):
    """Raised when a dependency cycle is detected."""


@dataclass
class WRKItem:
    wrk_id: str
    title: str
    status: str
    category: str
    blocked_by: list[str]


@dataclass
class GraphResult:
    unblocked: list[str]
    critical_path: list[str]
    chain_length: int
    all_ids: set[str] = field(default_factory=set)


@dataclass
class FeatureTreeItem:
    id: str
    title: str
    status: str
    type: str          # "feature" | "task"
    children: list     # list of child WRK IDs
    parent: str        # parent feature WRK ID or ""
    orchestrator: str
    blocked_by: list


# ---------------------------------------------------------------------------
# Frontmatter parsing (adapted from generate-index.py)
# ---------------------------------------------------------------------------

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


def _parse_frontmatter(text: str) -> dict[str, str | list[str]]:
    """Extract key fields from YAML frontmatter."""
    parts = text.split("---", 2)
    if len(parts) < 2:
        return {}
    fm = parts[1]

    result: dict[str, str | list[str]] = {}

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
            # bare `blocked_by:` with no inline value — leave unset so multiline fallback runs
        else:
            result[key] = _parse_fm_value(val)

    # Handle multi-line blocked_by list
    if "blocked_by" not in result:
        block = re.search(r"^blocked_by:\s*\n((?:\s+-[^\n]*\n?)*)", fm, re.MULTILINE)
        if block:
            items = re.findall(r"^\s+-\s+(\S+)", block.group(1), re.MULTILINE)
            result["blocked_by"] = [v.strip('"').strip("'") for v in items]

    return result


# ---------------------------------------------------------------------------
# Item discovery
# ---------------------------------------------------------------------------

QUEUE_ROOT = Path(__file__).resolve().parent.parent.parent / ".claude" / "work-queue"


def _resolve_queue_root(override: str | None = None) -> Path:
    """Return the queue root path, using override if supplied."""
    if override:
        return Path(override)
    return QUEUE_ROOT


def _discover_archived_ids(queue_root: Path | None = None) -> set[str]:
    """Return WRK IDs present in archive/ or archived/ directories."""
    root = queue_root or QUEUE_ROOT
    archived: set[str] = set()
    for dirname in ("archive", "archived"):
        d = root / dirname
        if d.is_dir():
            for f in d.rglob("WRK-*.md"):
                archived.add(f.stem)
    return archived


def _discover_items(
    category_filter: str | None = None,
    queue_root: Path | None = None,
) -> list[WRKItem]:
    """Read WRK items from pending/, working/, blocked/."""
    root = queue_root or QUEUE_ROOT
    items: list[WRKItem] = []
    for folder in ("pending", "working", "blocked"):
        d = root / folder
        if not d.is_dir():
            continue
        for f in sorted(d.glob("WRK-*.md")):
            try:
                text = f.read_text(encoding="utf-8")
            except OSError:
                continue
            fm = _parse_frontmatter(text)
            wrk_id = f.stem
            status = str(fm.get("status", folder.rstrip("/")))
            category = str(fm.get("category", ""))
            title = str(fm.get("title", ""))
            raw_blocked = fm.get("blocked_by", [])
            blocked_by = raw_blocked if isinstance(raw_blocked, list) else _parse_inline_list(str(raw_blocked))

            if category_filter and category.lower() != category_filter.lower():
                continue

            items.append(WRKItem(
                wrk_id=wrk_id,
                title=title,
                status=status,
                category=category,
                blocked_by=blocked_by,
            ))
    return items


# ---------------------------------------------------------------------------
# Feature tree helpers
# ---------------------------------------------------------------------------

_ALL_QUEUE_DIRS = ("pending", "working", "blocked", "archived", "archive", "done")


def _parse_children_list(fm: dict, raw_text: str) -> list[str]:
    """Extract children: list from frontmatter, supporting inline and block-list formats."""
    raw = fm.get("children")
    if isinstance(raw, list):
        return [str(c).strip() for c in raw if str(c).strip()]
    if isinstance(raw, str) and raw.strip():
        # Non-empty inline scalar — may be "[WRK-A, WRK-B]" or a single ID
        return _parse_inline_list(raw)
    # Empty scalar or None: try block-list in raw frontmatter text
    parts = raw_text.split("---", 2)
    if len(parts) >= 2:
        block = re.search(r"^children:\s*\n((?:\s+-[^\n]*\n?)*)", parts[1], re.MULTILINE)
        if block:
            return [v.strip().strip('"').strip("'")
                    for v in re.findall(r"^\s+-\s+(\S+)", block.group(1), re.MULTILINE)]
    return []


def _find_wrk_file(wrk_id: str, queue_root: Path) -> Path | None:
    """Search all queue dirs (including archive/YYYY-MM/ subdirs) for wrk_id.md."""
    for dirname in _ALL_QUEUE_DIRS:
        d = queue_root / dirname
        if not d.is_dir():
            continue
        # direct child
        candidate = d / f"{wrk_id}.md"
        if candidate.exists():
            return candidate
        # dated subdirs (e.g. archive/2026-03/)
        for sub in d.iterdir():
            if sub.is_dir():
                candidate = sub / f"{wrk_id}.md"
                if candidate.exists():
                    return candidate
    return None


def _load_feature_tree_item(wrk_id: str, queue_root: Path) -> FeatureTreeItem | None:
    """Load a FeatureTreeItem from any queue directory. Returns None if not found."""
    path = _find_wrk_file(wrk_id, queue_root)
    if path is None:
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    fm = _parse_frontmatter(text)
    children = _parse_children_list(fm, text)
    raw_blocked = fm.get("blocked_by", [])
    blocked_by = raw_blocked if isinstance(raw_blocked, list) else _parse_inline_list(str(raw_blocked))
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


def format_feature_tree(feature: FeatureTreeItem, queue_root: Path) -> str:
    """Render ASCII tree for a feature WRK and its children."""
    lines: list[str] = []
    title_str = f"  {feature.title}" if feature.title else ""
    lines.append(f"{feature.id} [{feature.status}]{title_str}")

    child_ids = feature.children
    for idx, child_id in enumerate(child_ids):
        is_last = idx == len(child_ids) - 1
        prefix = "└──" if is_last else "├──"
        child = _load_feature_tree_item(child_id, queue_root)
        if child is None:
            lines.append(f"{prefix} {child_id} [missing]")
            continue
        parts: list[str] = [f"{prefix} {child_id} [{child.status}]"]
        if child.title:
            parts.append(f"  {child.title}")
        extras: list[str] = []
        if child.blocked_by:
            blockers = ", ".join(child.blocked_by) if isinstance(child.blocked_by, list) else str(child.blocked_by)
            extras.append(f"blocked_by: {blockers}")
        if child.orchestrator:
            extras.append(f"agent: {child.orchestrator}")
        if extras:
            parts.append(f"  ({', '.join(extras)})")
        lines.append("".join(parts))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Graph computation
# ---------------------------------------------------------------------------

def compute_graph(
    items: list[WRKItem],
    archived_ids: set[str] | None = None,
    category_filter: str | None = None,
) -> GraphResult:
    """Build dependency graph and compute critical path.

    Args:
        items: WRK items to include.
        archived_ids: IDs known to be archived (treated as satisfied blockers).
        category_filter: When set, cross-category blockers are kept as opaque
            dependencies (item is NOT considered unblocked).

    Raises:
        CycleError: If a dependency cycle is detected.
    """
    if archived_ids is None:
        archived_ids = set()

    # Apply category filter — cross-category blockers become opaque
    if category_filter:
        items = [i for i in items if i.category.lower() == category_filter.lower()]

    all_ids = {item.wrk_id for item in items}
    item_map = {item.wrk_id: item for item in items}

    # Build predecessor map: node -> set of predecessors (things that block it)
    predecessors: dict[str, set[str]] = {item.wrk_id: set() for item in items}
    for item in items:
        for blocker in item.blocked_by:
            if blocker in all_ids:
                predecessors[item.wrk_id].add(blocker)
            elif blocker not in archived_ids:
                # Dangling or cross-category ref — treat as opaque blocker
                # Use a sentinel key to keep the node blocked
                predecessors[item.wrk_id].add(f"__external__{blocker}")

    # Topological sort — raises graphlib.CycleError on cycles
    # Only pass known nodes (not external sentinels) to TopologicalSorter
    internal_predecessors = {
        nid: {p for p in preds if not p.startswith("__external__")}
        for nid, preds in predecessors.items()
    }
    try:
        ts = graphlib.TopologicalSorter(internal_predecessors)
        topo_order = list(ts.static_order())
    except graphlib.CycleError as exc:
        raise CycleError(f"Dependency cycle detected: {exc}") from exc

    # DP: compute depth (chain length ending at each node)
    depth: dict[str, int] = {}
    for node in topo_order:
        if node not in all_ids:
            continue
        internal_preds = internal_predecessors.get(node, set())
        if internal_preds:
            depth[node] = 1 + max(depth.get(p, 0) for p in internal_preds)
        else:
            depth[node] = 1

    # Critical path: find node with max depth, walk back
    if not depth:
        return GraphResult(unblocked=[], critical_path=[], chain_length=0, all_ids=all_ids)

    max_node = max(depth, key=lambda n: depth[n])
    max_depth = depth[max_node]

    # Reconstruct path by greedy backtracking
    critical_path: list[str] = [max_node]
    current = max_node
    while True:
        preds = internal_predecessors.get(current, set())
        if not preds:
            break
        prev = max(preds, key=lambda p: depth.get(p, 0))
        critical_path.append(prev)
        current = prev
    critical_path.reverse()

    # Unblocked: items with no unsatisfied blockers AND not in 'blocked' folder/status
    unblocked: list[str] = []
    for item in items:
        if item.status == "blocked":
            continue
        total_preds = predecessors.get(item.wrk_id, set())
        if not total_preds:
            unblocked.append(item.wrk_id)

    # Sort by WRK ID number
    def _wrk_num(wrk_id: str) -> int:
        m = re.search(r"\d+", wrk_id)
        return int(m.group()) if m else 0

    unblocked.sort(key=_wrk_num)

    return GraphResult(
        unblocked=unblocked,
        critical_path=critical_path,
        chain_length=max_depth,
        all_ids=all_ids,
    )


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_summary(result: GraphResult) -> str:
    """Single-line summary for /work list footer."""
    n = len(result.unblocked)
    chain = result.chain_length
    if result.critical_path:
        path_str = " → ".join(result.critical_path[:3])
        if len(result.critical_path) > 3:
            path_str += f" → ... → {result.critical_path[-1]}"
        return f"[dep-graph] {n} unblocked, longest chain: {chain} nodes ({path_str})"
    return f"[dep-graph] {n} unblocked, longest chain: {chain} nodes"


def format_ascii_table(result: GraphResult, items: list[WRKItem]) -> str:
    """ASCII critical-path table."""
    item_map = {i.wrk_id: i for i in items}
    lines = [f"Critical path ({result.chain_length} nodes):"]
    path_parts = []
    for wrk_id in result.critical_path:
        item = item_map.get(wrk_id)
        if item:
            path_parts.append(f"{wrk_id} ({item.status}/{item.category})")
        else:
            path_parts.append(wrk_id)
    lines.append("  " + " → ".join(path_parts))
    lines.append("")
    lines.append(f"Unblocked items ({len(result.unblocked)}):")
    for wrk_id in result.unblocked[:20]:
        item = item_map.get(wrk_id)
        title = item.title[:60] if item else ""
        lines.append(f"  {wrk_id}: {title}")
    if len(result.unblocked) > 20:
        lines.append(f"  ... and {len(result.unblocked) - 20} more")
    return "\n".join(lines)


def format_dot(result: GraphResult, items: list[WRKItem]) -> str:
    """DOT digraph output."""
    item_map = {i.wrk_id: i for i in items}
    lines = ["digraph deps {", '  rankdir=LR;', '  node [shape=box, style=filled];']

    status_colors = {"pending": "lightblue", "working": "yellow", "blocked": "orange"}
    cp_set = set(result.critical_path)

    for item in items:
        color = status_colors.get(item.status, "white")
        border = ', penwidth=3, color=red' if item.wrk_id in cp_set else ""
        label = item.title[:40].replace('"', '\\"')
        lines.append(f'  "{item.wrk_id}" [label="{item.wrk_id}\\n{label}", fillcolor={color}{border}];')

    for item in items:
        for blocker in item.blocked_by:
            if blocker in {i.wrk_id for i in items}:
                lines.append(f'  "{blocker}" -> "{item.wrk_id}";')

    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="WRK dependency graph — visualise blocked_by chains"
    )
    parser.add_argument("--category", help="Filter to one category (cross-category blockers kept opaque)")
    parser.add_argument("--critical-path", action="store_true", help="Show only critical path, skip DOT")
    parser.add_argument("--dot", metavar="PATH", help="Write DOT file to PATH")
    parser.add_argument("--summary", action="store_true", help="Print single-line summary only (for /work list)")
    parser.add_argument("--feature", metavar="WRK-NNN", help="Render ASCII feature tree for a feature WRK")
    parser.add_argument(
        "--queue-root",
        metavar="PATH",
        help="Override queue root directory (default: auto-detect from repo)",
    )
    args = parser.parse_args()

    queue_root = _resolve_queue_root(args.queue_root)

    # --feature mode: render ASCII feature tree and exit
    if args.feature:
        feature = _load_feature_tree_item(args.feature, queue_root)
        if feature is None:
            print(f"[dep-graph] ERROR: {args.feature} not found in any queue directory", file=sys.stderr)
            sys.exit(1)
        print(format_feature_tree(feature, queue_root))
        return

    archived_ids = _discover_archived_ids(queue_root)
    items = _discover_items(category_filter=args.category, queue_root=queue_root)

    try:
        result = compute_graph(items, archived_ids=archived_ids, category_filter=args.category)
    except CycleError as exc:
        print(f"[dep-graph] ERROR: {exc}", file=sys.stderr)
        print("[dep-graph] 0 unblocked, longest chain: 0 nodes (cycle detected)")
        sys.exit(1)

    if args.summary:
        print(format_summary(result))
        return

    if args.critical_path:
        item_map = {i.wrk_id: i for i in items}
        path_parts = []
        for wrk_id in result.critical_path:
            item = item_map.get(wrk_id)
            path_parts.append(f"{wrk_id} ({item.status}/{item.category})" if item else wrk_id)
        print(f"Critical path ({result.chain_length} nodes):")
        print("  " + " → ".join(path_parts))
        return

    # ASCII output
    print(format_ascii_table(result, items))

    if args.dot:
        dot_path = Path(args.dot)
        dot_path.write_text(format_dot(result, items))
        print(f"\nDOT file written to: {dot_path}")


if __name__ == "__main__":
    main()
