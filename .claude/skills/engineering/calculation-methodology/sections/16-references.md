# 16 — References

## Purpose

List all documents, standards, data sources, and software cited in the
calculation. References ensure traceability and allow reviewers to verify
source material. Normative and informative references must be distinguished.

## Schema Fields

```yaml
references:
  normative:
    - id: string               # citation key (e.g., "REF-01")
      type: enum               # standard | regulation | specification | data_sheet
      title: string
      document_number: string
      edition: string          # edition year or revision
      publisher: string
      cited_in: [string]       # sections where this reference is used
  informative:
    - id: string
      type: enum               # textbook | paper | report | software_manual
      title: string
      author: string
      year: string
      publisher: string
      cited_in: [string]
  project_documents:
    - id: string
      type: enum               # data_sheet | drawing | report | specification
      document_number: string
      title: string
      revision: string
      cited_in: [string]
```

## Required Content

- Every standard cited in section 03 must appear here with edition
- Every data source cited in section 05 must appear here
- Normative vs informative classification for all references
- Citation keys that match the references used in the calculation body

## Quality Checklist

- [ ] All standards from the design basis (section 03) are listed with edition year
- [ ] Normative references are separated from informative references
- [ ] Project documents include revision numbers
- [ ] No orphan references (every ref is cited somewhere in the document)
- [ ] No orphan citations (every citation in the body has a matching reference)

## Example Snippet

```yaml
references:
  normative:
    - id: "REF-01"
      type: standard
      title: "Submarine Pipeline Systems"
      document_number: "DNV-ST-F101"
      edition: "2021-08"
      publisher: "Det Norske Veritas"
      cited_in: ["section 03", "section 07", "section 08"]
    - id: "REF-02"
      type: standard
      title: "Gas Transmission and Distribution Piping Systems"
      document_number: "ASME B31.8"
      edition: "2022"
      publisher: "ASME"
      cited_in: ["section 11"]
  informative:
    - id: "REF-03"
      type: textbook
      title: "Submarine Pipeline Design, Analysis, and Installation"
      author: "Bai, Y. and Bai, Q."
      year: "2014"
      publisher: "Gulf Professional Publishing"
      cited_in: ["section 07"]
  project_documents:
    - id: "REF-04"
      type: data_sheet
      document_number: "DS-PL-001"
      title: "12-inch Export Pipeline Data Sheet"
      revision: "B"
      cited_in: ["section 05"]
```

## Common Mistakes

- Standard listed without edition year — different editions have different criteria
- Normative and informative references mixed together
- Reference cited in the body but missing from the reference list
- Project documents listed without revision — reviewer cannot verify currency
- Software used for calculations not listed (version and validation status)
