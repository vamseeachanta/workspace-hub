"""Equation promoter — renders typed Python functions from equation records."""

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from scripts.data.doc_intelligence.promoters.coordinator import (
    PromoteResult,
    register_promoter,
)
from scripts.data.doc_intelligence.promoters.text_utils import (
    content_hash,
    sanitize_identifier,
    source_citation,
    write_atomic,
)

# Domain → output sub-path under digitalmodel/src/digitalmodel/
DOMAIN_MODULE_MAP = {
    "naval-architecture": "naval_architecture/equations.py",
    "structural": "structural/equations.py",
    "hydrodynamics": "hydrodynamics/equations.py",
    "cathodic-protection": "cathodic_protection/equations.py",
}


@dataclass
class ParsedParam:
    """A single parsed parameter from a 'where' clause."""

    name: str
    description: str
    unit: str


@dataclass
class ParsedEquation:
    """Fully parsed equation ready for code generation."""

    function_name: str
    display_name: str
    formula: str
    params: List[ParsedParam]
    return_description: str
    return_unit: str
    citation: str
    domain: str


def parse_equation(record: dict) -> Optional[ParsedEquation]:
    """Parse an equation record into structured form.

    Expected text format:
        "Name: formula, where p1 is desc [unit], p2 is desc [unit]. Returns result in unit."

    Returns None if parsing fails.
    """
    text = record.get("text", "")
    source = record.get("source", {})
    domain = record.get("domain", "unknown")

    # Step 1: split on first ":" to get name and body
    colon_idx = text.find(":")
    if colon_idx == -1:
        return None
    display_name = text[:colon_idx].strip()
    body = text[colon_idx + 1:].strip()

    # Step 2: extract formula (before "where")
    where_match = re.search(r",?\s*where\s+", body, re.IGNORECASE)
    if where_match is None:
        return None
    formula = body[:where_match.start()].strip().rstrip(",")

    # Step 3: extract 'where' clause and 'Returns' clause
    after_where = body[where_match.end():]
    returns_match = re.search(r"\.\s*Returns?\s+", after_where, re.IGNORECASE)
    if returns_match is None:
        return None
    where_clause = after_where[:returns_match.start()].strip().rstrip(".")
    returns_clause = after_where[returns_match.end():].strip().rstrip(".")

    # Step 4: parse parameters from where clause
    params = _parse_params(where_clause)
    if not params:
        return None

    # Step 5: parse return info — "result in unit"
    ret_match = re.match(r"(.+?)\s+in\s+(.+)", returns_clause, re.IGNORECASE)
    if ret_match:
        return_description = ret_match.group(1).strip()
        return_unit = ret_match.group(2).strip()
    else:
        return_description = returns_clause
        return_unit = ""

    function_name = sanitize_identifier(display_name)
    if not function_name:
        return None

    return ParsedEquation(
        function_name=function_name,
        display_name=display_name,
        formula=formula,
        params=params,
        return_description=return_description,
        return_unit=return_unit,
        citation=source_citation(source),
        domain=domain,
    )


def _parse_params(where_clause: str) -> List[ParsedParam]:
    """Parse 'param is description [unit]' entries from a where clause."""
    # Split on comma to get individual param definitions
    raw_parts = re.split(r",\s*", where_clause)
    params = []
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(
            r"(\w+)\s+is\s+(.+?)\s*\[([^\]]+)\]",
            part,
            re.IGNORECASE,
        )
        if m:
            params.append(ParsedParam(
                name=m.group(1),
                description=m.group(2).strip(),
                unit=m.group(3).strip(),
            ))
    return params


def render_function(eq: ParsedEquation) -> str:
    """Render a single equation as a typed Python function with docstring."""
    # Build parameter list
    param_sig = ", ".join(f"{p.name}: float" for p in eq.params)

    # Build docstring
    lines = []
    lines.append(f'def {eq.function_name}({param_sig}) -> float:')
    lines.append(f'    """{eq.display_name} ({eq.citation}).')
    lines.append("")
    lines.append(f"    {eq.formula}")
    lines.append("")
    lines.append("    Parameters")
    lines.append("    ----------")
    for p in eq.params:
        lines.append(f"    {p.name} : float")
        lines.append(f"        {p.description} [{p.unit}].")
    lines.append("")
    lines.append("    Returns")
    lines.append("    -------")
    lines.append("    float")
    unit_suffix = f" [{eq.return_unit}]" if eq.return_unit else ""
    lines.append(f"        {eq.return_description.capitalize()}{unit_suffix}.")
    lines.append('    """')

    # Build body: extract RHS from formula (after "=")
    eq_parts = eq.formula.split("=", 1)
    if len(eq_parts) == 2:
        expr = eq_parts[1].strip()
    else:
        expr = " * ".join(p.name for p in eq.params)
    lines.append(f"    return {expr}")

    return "\n".join(lines)


def render_module(equations: List[ParsedEquation], domain: str) -> str:
    """Render a complete Python module from a list of parsed equations."""
    # Build the function bodies first to compute content hash
    func_blocks = [render_function(eq) for eq in equations]
    body = "\n\n\n".join(func_blocks) + "\n"

    # Module-level docstring with content hash
    domain_label = domain.replace("-", " ").title()
    header = (
        f'"""{domain_label} Equations — auto-promoted from doc-intelligence.\n'
        f"\n"
        f"# content-hash: {content_hash(body)}\n"
        f'"""\n'
    )
    return header + "\n\n" + body


def promote_equations(
    records: List[dict],
    project_root: Path,
    dry_run: bool = False,
) -> PromoteResult:
    """Promote equation records into typed Python modules.

    Groups equations by domain and writes one module per domain.
    """
    result = PromoteResult()

    if not records:
        return result

    # Group records by domain
    by_domain: dict[str, List[ParsedEquation]] = defaultdict(list)
    for rec in records:
        parsed = parse_equation(rec)
        if parsed is None:
            result.errors.append(
                f"Failed to parse equation: {rec.get('text', '')[:60]}..."
            )
            continue
        by_domain[parsed.domain].append(parsed)

    # Render and write one module per domain
    for domain, equations in sorted(by_domain.items()):
        rel_path = DOMAIN_MODULE_MAP.get(
            domain,
            f"{sanitize_identifier(domain)}/equations.py",
        )
        out_path = (
            project_root / "digitalmodel" / "src" / "digitalmodel" / rel_path
        )
        content = render_module(equations, domain)
        written = write_atomic(out_path, content, dry_run=dry_run)
        target = str(out_path)
        if written:
            result.files_written.append(target)
        else:
            result.files_skipped.append(target)

    return result


register_promoter("equations", promote_equations)
