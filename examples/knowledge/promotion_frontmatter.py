"""Emit synthetic YAML frontmatter mappings demonstrating section 10.1.

Authority: docs/document-intelligence/durable-vs-transient-knowledge-boundary.md,
section 10.1. This example does not impose a wiki schema; each wiki's own
frontmatter authority remains binding. It cannot establish that promotion or
source qualification occurred. The processing-status enum in the standards
provenance document is a different unresolved recommendation, not artifact
lineage, and is not represented here.

sources lists editorial source identifiers, separate from page identity in
doc_key. promoted_from references the transient artifact from which content was
promoted. last_updated is the page update date, not evidence of promotion time
or source qualification. YAML serialization is checked, not the referenced
artifacts, rights, source contents or promotion criteria.

The literal inputs are specified independently in
tests/knowledge/test_promotion_frontmatter_example.py. Titles, dates, locators,
source identifiers and hex keys are synthetic; keys illustrate the baseline
form and are not verified content digests. No wiki checkout, source document or
network is needed. Output is a YAML document stream of frontmatter mappings,
not complete Markdown pages.

Run from the checkout with:
    uv run --no-project --with pyyaml python examples/knowledge/promotion_frontmatter.py
The script can also be invoked by its resolved path from any working directory.
"""

from __future__ import annotations

import argparse

import yaml


EXAMPLES = (
    {
        "title": "Synthetic issue finding",
        "doc_key": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "sources": ["synthetic-source:reference-alpha"],
        "promoted_from": "issue:123",
        "last_updated": "2026-01-12",
    },
    {
        "title": "Synthetic handoff finding",
        "doc_key": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "sources": ["synthetic-source:reference-beta"],
        "promoted_from": "docs/handoffs/synthetic-handoff.md",
        "last_updated": "2026-02-16",
    },
    {
        "title": "Synthetic recurring finding",
        "doc_key": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        "sources": ["synthetic-source:reference-gamma"],
        "promoted_from": "reports/recurring/synthetic-review-2026-03-09.md",
        "last_updated": "2026-03-10",
    },
)


def render_examples() -> str:
    """Check complete mapping equality after serializing the literal inputs."""
    output = yaml.safe_dump_all(EXAMPLES, explicit_start=True, sort_keys=False)
    if tuple(yaml.safe_load_all(output)) != EXAMPLES:
        raise ValueError("YAML roundtrip changed the illustrative mappings")
    return output


def main() -> None:
    """Describe scope on request, otherwise emit the checked YAML stream."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(render_examples(), end="")


if __name__ == "__main__":
    main()
