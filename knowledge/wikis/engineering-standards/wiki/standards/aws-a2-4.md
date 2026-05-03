---
title: "AWS A2.4 — Standard Symbols for Welding, Brazing, and Nondestructive Examination — bounded summary"
tags: ["aws", "standards", "welding", "symbols", "nde", "metadata-only"]
added: 2026-05-03
last_updated: 2026-05-03
domain: engineering-standards
code_id: aws-a2-4
publisher: AWS
publisher_full: "American Welding Society"
revision: "2007"
revision_source: "/mnt/ace/O&G-Standards/AWS/AWS A2.4/AWS A2.4 (2007) Standard Symbols for Welding, Brazing, and Nondestructive Examination.pdf"
publisher_current_edition: "2020"
verified_on: 2026-05-03
public_url: https://pubs.aws.org/
sources:
  - "/mnt/ace/O&G-Standards/AWS/AWS A2.4/AWS A2.4 (2007) Standard Symbols for Welding, Brazing, and Nondestructive Examination.pdf"
extraction_policy: metadata-only
raw_copy_allowed: false
aws_doc_number: "A2.4"
ledger_id: AWS-A2.4
cross_references:
  - { code_id: "aws-d1-1", relation: "references", note: "D1.1 contract drawings invoke A2.4 welding-symbol conventions" }
  - { code_id: "aws-d1-2", relation: "references", note: "D1.2 aluminum-structure drawings invoke A2.4 welding-symbol conventions" }
---

# AWS A2.4 — Standard Symbols for Welding, Brazing, and Nondestructive Examination

## Scope
Standard graphical symbology for indicating welding, brazing, and nondestructive examination requirements on engineering drawings. Establishes a left-side / right-side reference-line convention for arrow-side and other-side weld features, supplementary symbols for finish and contour, dimensional placement, and a parallel symbology for NDE methods. Reference document — not a fabrication code — and is invoked by every AWS structural and fabrication code that uses drawings.

## Why this page exists
Resolver target for digitalmodel `Citation` instances per `.claude/rules/calc-citation-contract.md`. No live caller in `digitalmodel/src/` cites A2.4 today; this page is corpus-driven and future-needed because every AWS welding code referenced in the codebase invokes A2.4 symbol conventions on contract drawings. The schema field `code_id` is overloaded to mean `standards-document-id` for both AWS Codes and AWS Standards (taxonomy distinguishes them; schema field name is generic). Contains no clause text, no symbol tables, and no figure reproductions.

## Where to find the full text
- Raw PDF: `/mnt/ace/O&G-Standards/AWS/AWS A2.4/AWS A2.4 (2007) Standard Symbols for Welding, Brazing, and Nondestructive Examination.pdf` (read-only, vendor-derivative; do not copy into git per #2482)
- Publisher catalog: https://pubs.aws.org/ (registration required for purchase/download)
- Internal callers: no live caller; future-needed for any drawing-symbol resolver or NDE-symbology workflow

## Edition gap discipline
On-disk edition is 2007. Publisher-current edition is 2020 (subject to verification at the publisher portal). Calc-callers and drafting-resolver users MUST verify against the publisher-current edition before relying on symbol semantics; this wiki page reflects the on-disk corpus only.

## Cross-references
- [[aws-d1-1]] — references A2.4 symbology on structural-steel contract drawings
- [[aws-d1-2]] — references A2.4 symbology on aluminum-structure contract drawings
- [Calc citation contract](../../../../../.claude/rules/calc-citation-contract.md)
