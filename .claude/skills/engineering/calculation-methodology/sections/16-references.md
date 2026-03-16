# 16 — References

## Purpose

List all documents, standards, data sources, and software cited in the
calculation. References ensure traceability and allow reviewers to verify
source material.

## Schema Fields

```yaml
references:
  - string                    # each reference is a plain string
```

> **Renderer Mapping Note:** The methodology recommends categorized references
> with `normative[]`, `informative[]`, and `project_documents[]` sub-lists,
> each containing structured objects with `id`, `type`, `title`,
> `document_number`, `edition`, `publisher`, `cited_in`. The renderer treats
> `references` as a simple list of strings — each rendered as a numbered item.
> Encode the full citation (standard number, edition, title, publisher) in
> each string entry. Group normative references first, then informative,
> then project documents, using the ordering to convey priority.

## Required Content

- Every standard cited in section 03 with edition year
- Every data source cited in section 05
- Normative references listed before informative ones

## Quality Checklist

- [ ] Each entry is a plain string (not a structured dict)
- [ ] All standards from the design basis (section 03) are listed with edition
- [ ] No orphan references (every ref is cited somewhere in the document)
- [ ] No orphan citations (every citation in the body has a matching reference)
- [ ] Project documents include revision numbers

## Example Snippet

```yaml
references:
  - "DNV-RP-B401 (2011) Cathodic Protection Design"
  - "DNV-RP-B401 Table 10-1: Design current densities"
  - "DNV-RP-B401 Table 10-4: Coating breakdown constants"
  - "DNV-RP-B401 Table 10-6: Anode electrochemical properties"
  - "ASME B31.8-2022 — Gas Transmission and Distribution Piping Systems"
  - "Bai, Y. and Bai, Q. (2014) Submarine Pipeline Design, Analysis, and Installation. Gulf Professional Publishing"
  - "DS-PL-001 Rev B — 12-inch Export Pipeline Data Sheet"
```

## Common Mistakes

- Using categorized sub-lists (`normative[]`, `informative[]`, `project_documents[]`)
  instead of a simple flat list of strings
- Including structured objects with `id`, `type`, `title` fields
- Standard listed without edition year — different editions have different criteria
- Reference cited in the body but missing from the reference list
- Software used for calculations not listed (version and validation status)
