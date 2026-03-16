"""Build a dependency DAG from formula cell references and classify cells.

Requires networkx. Install via: uv add networkx (or use inline script deps).
"""

from __future__ import annotations

from typing import Any, Dict, List

try:
    import networkx as nx
except ImportError:  # pragma: no cover
    nx = None  # type: ignore[assignment]


def _require_nx() -> None:
    if nx is None:
        raise ImportError(
            "networkx is required for formula_chain_builder. "
            "Install with: uv add networkx"
        )


def build_dependency_graph(formula_cells: list) -> Any:
    """Build a directed graph from formula cells.

    Each formula_cell must have 'cell_ref' and 'references' attributes/keys.
    Edge direction: referenced cell -> formula cell (dependency flows forward).

    Args:
        formula_cells: List of CellFormula objects or dicts with
            'cell_ref' and 'references' keys.

    Returns:
        networkx.DiGraph
    """
    _require_nx()
    g = nx.DiGraph()

    for cell in formula_cells:
        if hasattr(cell, "cell_ref"):
            ref = cell.cell_ref
            deps = cell.references
        else:
            ref = cell["cell_ref"]
            deps = cell.get("references", [])

        g.add_node(ref)
        for dep in deps:
            g.add_edge(dep, ref)

    return g


def classify_cells(g: Any) -> Dict[str, List[str]]:
    """Classify cells into inputs, outputs, and topological chain.

    Args:
        g: networkx.DiGraph from build_dependency_graph.

    Returns:
        Dict with keys 'inputs', 'outputs', 'chain'.
        - inputs: nodes with in-degree 0 (leaf data cells)
        - outputs: nodes with out-degree 0 (final results)
        - chain: topological sort order
    """
    _require_nx()
    inputs = [n for n in g.nodes() if g.in_degree(n) == 0]
    outputs = [n for n in g.nodes() if g.out_degree(n) == 0]

    try:
        chain = list(nx.topological_sort(g))
    except nx.NetworkXUnfeasible:
        chain = list(g.nodes())

    return {"inputs": inputs, "outputs": outputs, "chain": chain}
