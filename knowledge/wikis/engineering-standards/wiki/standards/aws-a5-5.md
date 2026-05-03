---
title: "AWS A5.5 — Specification for Low-Alloy Steel Electrodes for Shielded Metal Arc Welding — bounded summary"
tags: ["aws", "standards", "welding", "filler-metal", "smaw", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: aws-a5-5
publisher: AWS
publisher_full: "American Welding Society"
revision: "1996"
revision_source: "/mnt/ace/O&G-Standards/AWS/AWS-A5-5.pdf (cover page reads ANSI/AWS A5.5-96; 1996 ANSI-approved edition with 2001 reissue print, verified 2026-05-03 via PyMuPDF cover-page extraction)"
publisher_current_edition: "2014"
verified_on: 2026-05-03
public_url: https://pubs.aws.org/
sources:
  - "/mnt/ace/O&G-Standards/AWS/AWS-A5-5.pdf"
extraction_policy: metadata-only
raw_copy_allowed: false
aws_doc_number: "A5.5"
ledger_id: AWS-A5.5
cross_references:
  - { code_id: "aws-d1-1", relation: "references", note: "D1.1 references A5-series filler-metal specifications for matching electrode classification on structural welds" }
  - { code_id: "asme-bpvc-ix", relation: "references", note: "BPVC Section IX procedure qualification cites filler-metal classifications from the AWS A5 series" }
---

# AWS A5.5 — Specification for Low-Alloy Steel Electrodes for Shielded Metal Arc Welding

## Scope
Filler-metal specification for low-alloy steel covered electrodes used in shielded metal arc welding (SMAW). Establishes classification by tensile strength, deposited-weld-metal composition, position of welding, and coating type. Covers chemical composition, mechanical property requirements, manufacturing requirements, and packaging. Used to specify electrode purchase for code-compliant welding under structural and pressure codes that reference AWS filler-metal classifications.

## Why this page exists
Resolver target for digitalmodel `Citation` instances per `.claude/rules/calc-citation-contract.md`. No live caller in `digitalmodel/src/` cites A5.5 today; this page is corpus-driven and future-needed because matching filler-metal classification is a contractual requirement of every D1.1 and BPVC Section IX welding workflow that uses low-alloy steel SMAW electrodes. Contains no clause text, no classification tables, and no chemistry/mechanical-property values.

## Where to find the full text
- Raw PDF: `/mnt/ace/O&G-Standards/AWS/AWS-A5-5.pdf` (read-only, vendor-derivative; do not copy into git per #2482). PDF is the 1996 ANSI-approved edition with a 2001 reissue print as confirmed by the cover page.
- Publisher catalog: https://pubs.aws.org/ (registration required for purchase/download)
- Internal callers: no live caller; future-needed for filler-metal classification resolution in welding-procedure workflows

## Edition gap discipline
On-disk edition is 1996. Publisher-current edition is approximately A5.5/A5.5M:2014 (subject to verification at the publisher portal — no confirmed 2025 reissue surfaced as of the verification date). Calc-callers MUST verify against the publisher-current edition before any compliance use; this wiki page reflects the on-disk corpus only.

## Cross-references
- [[aws-d1-1]] — references A5-series filler-metal classifications for matching-electrode requirements
- [[asme-bpvc-ix]] — procedure qualification cites filler-metal classifications from the A5 series
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
