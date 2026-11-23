"""
Six rubric scorer functions for html_to_markdown conversion quality.

All scores in [0.0, 1.0]. Two callers given the same (actual_md, expected_md, html)
MUST produce bit-identical scores (modulo scipy version variance on dim 1 — see
test #11 tolerance band).

Dimensions 2-5 use the shared empty_safe_ratio() helper.
Dimension 1 uses an explicit both-empty -> 1.0 clause.
Dimension 6 uses an explicit both-empty -> 1.0 clause before its edit-distance ratio
and does NOT call empty_safe_ratio — its formula is an edit-distance ratio, not a
match-count ratio; retrofitting would change the output unit.
"""

import re
from typing import Any

# ── Shared helper ─────────────────────────────────────────────────────────────

def empty_safe_ratio(actual_tokens: list, oracle_tokens: list, match_count: int) -> float:
    """Denominator-safe match-count ratio used by dims 2-5.

    Contract:
      both empty               -> 1.0  (trivially well-matched)
      oracle empty, actual non-empty -> 0.0  (spurious content)
      oracle non-empty, actual empty -> 0.0  (falls through: 0 / max(|o|, 1))
      otherwise                -> match_count / max(len(oracle_tokens), 1)

    NOTE: dim 6 (list nesting) does NOT call this helper. Its formula is
    `1 - tree_edit_distance / max(size)`, an edit-distance ratio, not a
    match-count ratio. Do NOT retrofit dim 6 to call empty_safe_ratio.
    """
    a, o = len(actual_tokens), len(oracle_tokens)
    if a == 0 and o == 0:
        return 1.0
    if o == 0 and a > 0:
        return 0.0
    return match_count / max(o, 1)


# ── Heading extraction ────────────────────────────────────────────────────────

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


def _extract_headings(md: str) -> list[tuple[int, str]]:
    return [
        (len(m.group(1)), m.group(2).strip())
        for m in _HEADING_RE.finditer(md)
    ]


# ── Dim 1: Heading preservation ───────────────────────────────────────────────

def heading_scorer(actual_md: str, oracle_md: str, _html: str) -> float:
    """Jaccard (0.7) + Kendall-tau order (0.3) on (level, text) heading tuples.

    v6 NOTE: oracle .md files use HTML-comment provenance metadata
    (<!-- key: value -->), so this regex CANNOT match metadata lines.
    Test #14 enforces this contract.
    """
    A = _extract_headings(actual_md)
    O = _extract_headings(oracle_md)

    set_A, set_O = set(A), set(O)

    # Jaccard over sets
    union = set_A | set_O
    if not union:
        J = 1.0
    else:
        J = len(set_A & set_O) / len(union)

    # Kendall-tau order on common elements
    common = set_A & set_O
    if len(common) < 2:
        K = 1.0
    else:
        from scipy.stats import kendalltau
        rank_A = {h: i for i, h in enumerate(A) if h in common}
        rank_O = {h: i for i, h in enumerate(O) if h in common}
        common_list = sorted(common, key=lambda h: rank_O[h])
        vec_A = [rank_A[h] for h in common_list]
        vec_O = [rank_O[h] for h in common_list]
        tau = kendalltau(vec_A, vec_O).statistic
        K = (tau + 1) / 2

    return 0.7 * J + 0.3 * K


# ── Dim 2: Link resolution ────────────────────────────────────────────────────

_LINK_RE = re.compile(r"\[(?:[^\]]*)\]\(([^)]+)\)")


def _extract_hrefs(md: str) -> list[str]:
    return _LINK_RE.findall(md)


def link_scorer(actual_md: str, oracle_md: str, _html: str) -> float:
    """Match-count ratio of href multisets.

    Score = empty_safe_ratio(H_a, H_o, |H_a ∩ H_o|).
    Anchor, mailto, and https links are all counted in the same bucket.
    """
    H_a = _extract_hrefs(actual_md)
    H_o = _extract_hrefs(oracle_md)

    # multiset intersection: count of each href in both
    from collections import Counter
    cnt_a = Counter(H_a)
    cnt_o = Counter(H_o)
    match_count = sum(min(cnt_a[h], cnt_o[h]) for h in cnt_o)

    return empty_safe_ratio(H_a, H_o, match_count)


# ── Dim 3: Table fidelity ─────────────────────────────────────────────────────

_TABLE_ROW_RE = re.compile(r"^\|(.+)\|$", re.MULTILINE)


def _extract_table_cells(md: str) -> list[str]:
    cells: list[str] = []
    for m in _TABLE_ROW_RE.finditer(md):
        row_cells = [c.strip() for c in m.group(1).split("|")]
        cells.extend(row_cells)
    return cells


def table_scorer(actual_md: str, oracle_md: str, _html: str) -> float:
    """Row-major flattened cell match at common prefix positions.

    Score = empty_safe_ratio(G_a, G_o, prefix_match_count).
    """
    G_a = _extract_table_cells(actual_md)
    G_o = _extract_table_cells(oracle_md)

    prefix_len = min(len(G_a), len(G_o))
    match_count = sum(1 for i in range(prefix_len) if G_a[i] == G_o[i])

    return empty_safe_ratio(G_a, G_o, match_count)


# ── Dim 4: Code-block fidelity ────────────────────────────────────────────────

_CODE_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)


def _extract_code_blocks(md: str) -> list[tuple[str, str]]:
    return [
        (m.group(1), _normalize_code(m.group(2)))
        for m in _CODE_BLOCK_RE.finditer(md)
    ]


def _normalize_code(body: str) -> str:
    return "\n".join(line.rstrip() for line in body.splitlines())


def code_scorer(actual_md: str, oracle_md: str, _html: str) -> float:
    """Ordered list match of (lang_tag, body_normalized) code block pairs.

    Score = empty_safe_ratio(B_a, B_o, match_count).
    match_i = 1 iff lang tag equals AND body equals (after rstrip per line).
    """
    B_a = _extract_code_blocks(actual_md)
    B_o = _extract_code_blocks(oracle_md)

    match_count = sum(1 for a, o in zip(B_a, B_o) if a == o)

    return empty_safe_ratio(B_a, B_o, match_count)


# ── Dim 5: Image alt-text ─────────────────────────────────────────────────────

_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def _extract_images(md: str) -> dict[str, str]:
    """Returns {normalized_src: alt_text} (last occurrence wins on dup src)."""
    result: dict[str, str] = {}
    for m in _IMAGE_RE.finditer(md):
        alt, src = m.group(1), _normalize_src(m.group(2))
        result[src] = alt
    return result


def _normalize_src(src: str) -> str:
    return src.strip().rstrip("/")


def image_scorer(actual_md: str, oracle_md: str, _html: str) -> float:
    """Src-keyed alt-text match.

    Score = empty_safe_ratio(M_a.keys(), M_o.keys(), match_count).
    match_i = 1 iff src ∈ common AND alt_a[src] == alt_o[src].
    Unmatched oracle srcs contribute 0 to numerator, still counted in denominator.
    """
    M_a = _extract_images(actual_md)
    M_o = _extract_images(oracle_md)

    common = set(M_a.keys()) & set(M_o.keys())
    match_count = sum(1 for src in common if M_a[src] == M_o[src])

    return empty_safe_ratio(list(M_a.keys()), list(M_o.keys()), match_count)


# ── Dim 6: List nesting ───────────────────────────────────────────────────────

_LIST_LINE_RE = re.compile(r"^([ \t]*)[-*]|\d+\.", re.MULTILINE)


def _extract_depth_tree(md: str) -> list[int]:
    """Returns list of depths (0-indexed) for each list item line."""
    depths: list[int] = []
    for line in md.splitlines():
        m = re.match(r"^([ \t]*)[-*]", line) or re.match(r"^([ \t]*)\d+\.", line)
        if m:
            indent = len(m.group(1).expandtabs(4))
            depths.append(indent // 2)
    return depths


def _tree_edit_distance(tree_a: list[int], tree_b: list[int]) -> int:
    """Zhang-Shasha tree edit distance via the zss package.

    Trees are encoded as flat depth lists and converted to zss.Node trees.
    """
    try:
        import zss
    except ImportError:
        return abs(len(tree_a) - len(tree_b))

    def build_zss_tree(depths: list[int]) -> Any:
        if not depths:
            return zss.Node("root")
        root = zss.Node("root")
        stack: list[tuple[int, Any]] = [(-1, root)]
        for depth in depths:
            node = zss.Node(str(depth))
            while len(stack) > 1 and stack[-1][0] >= depth:
                stack.pop()
            stack[-1][1].addkid(node)
            stack.append((depth, node))
        return root

    t_a = build_zss_tree(tree_a)
    t_b = build_zss_tree(tree_b)
    return zss.simple_distance(t_a, t_b)


def list_scorer(actual_md: str, oracle_md: str, _html: str) -> float:
    """Zhang-Shasha tree edit distance on list depth trees.

    NOTE: does NOT call empty_safe_ratio. Formula is an edit-distance ratio,
    not a match-count ratio. Do NOT retrofit to call empty_safe_ratio —
    the output unit is incompatible.

    Both-empty -> 1.0 (page with no lists scores 1.0, not 0.0).
    Otherwise: 1 - distance / max(size_a, size_b, 1).
    """
    T_a = _extract_depth_tree(actual_md)
    T_b = _extract_depth_tree(oracle_md)

    if not T_a and not T_b:
        return 1.0

    dist = _tree_edit_distance(T_a, T_b)
    size = max(len(T_a), len(T_b), 1)
    return max(0.0, 1.0 - dist / size)


# ── Public registry ───────────────────────────────────────────────────────────

RUBRIC_DIMENSIONS = ["heading", "link", "table", "code", "image", "list"]

SCORERS: dict[str, Any] = {
    "heading": heading_scorer,
    "link": link_scorer,
    "table": table_scorer,
    "code": code_scorer,
    "image": image_scorer,
    "list": list_scorer,
}
