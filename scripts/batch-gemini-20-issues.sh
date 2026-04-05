#!/bin/bash
# Gemini batch execution: 20 issues across 4 batches
# Auto-generated 2026-04-05
set -e

cd /mnt/local-analysis/workspace-hub

# Resolve alias — h-router-gemini expands to this
h-router-gemini() {
  hermes chat --provider openrouter -m google/gemini-2.5-pro "$@"
}

echo "=== BATCH 1 (5 issues: #1776 #1655 #1653 #1658 #1770) ==="
echo "Started: $(date)"
h-router-gemini -t terminal,file -q "You are ACE Engineer advance scout. Working directory: /mnt/local-analysis/workspace-hub.
Execute ALL 5 tasks. Commit after each. Do NOT push. Close each issue.

TASK 1: Mount Drive Resource Audit (#1776)
- Read docs/document-intelligence/ for mount drive docs
- Search for legal scan results: search_files pattern='legal' output_mode=files_only
- Create: docs/document-intelligence/mount-drive-audit.md covering resources on local vs remote, gaps, legal scan status, bridging recommendations
- Commit: git add that file && git commit -m 'doc-intel: mount drive resource audit (#1776)'
- Close: gh issue close 1776 -c 'Mount drive audit completed. See docs/document-intelligence/mount-drive-audit.md'

TASK 2: Taxonomy All Domains (#1655)
- Read existing taxonomy in docs/ and data/
- Create: data/document-intelligence/taxonomy-all-domains-plan.md with taxonomy for: pipeline, structural, materials, process, geotechnical, reservoir, naval-arch. Category structure, keywords, classification criteria for each
- Commit: git add that file && git commit -m 'doc-intel: taxonomy classifier expanded to all domains (#1655)'
- Close: gh issue close 1655 -c 'All-domains taxonomy plan at data/document-intelligence/taxonomy-all-domains-plan.md'

TASK 3: Marine Subdomain Taxonomy (#1653)
- Create: data/document-intelligence/marine-subdomain-taxonomy.md with 9 sub-domains (hydrodynamics, mooring, risers, VIV, fatigue, installation, marine-ops, vessels, pipelines). For each: estimated count, keywords, criteria. Strategy to classify 33% unclassified of 32K marine docs
- Commit: git add that file && git commit -m 'doc-intel: marine subdomain taxonomy to reduce unclassified under 10% (#1653)'
- Close: gh issue close 1653 -c 'Marine subdomain taxonomy at data/document-intelligence/marine-subdomain-taxonomy.md'

TASK 4: Cross-Reference Improvement (#1658)
- Read document index structure
- Create: data/document-intelligence/cross-reference-improvement-plan.md with URL matching, org matching, doc_number matching strategies
- Commit: git add that file && git commit -m 'doc-intel: cross-reference improvement plan (#1658)'
- Close: gh issue close 1658 -c 'Cross-reference plan at data/document-intelligence/cross-reference-improvement-plan.md'

TASK 5: Standards Ledger Expansion (#1770)
- Search for standards ledger files
- Create: data/document-intelligence/standards-ledger-expansion-plan.md for SNAME, OnePetro, BSI, Norsok + 6 migrated orgs
- Commit: git add that file && git commit -m 'doc-intel: standards ledger expansion for 9 orgs (#1770)'
- Close: gh issue close 1770 -c 'Standards ledger plan at data/document-intelligence/standards-ledger-expansion-plan.md'

RULES: Commit after each task, do NOT push. Close each issue. All paths under /mnt/local-analysis/workspace-hub/"
echo "Batch 1 done: $(date)"

sleep 30

echo "=== BATCH 2 (5 issues: #1772 #1757 #1863 #1862 #1671) ==="
echo "Started: $(date)"
h-router-gemini -t terminal,file -q "You are ACE Engineer advance scout. Working directory: /mnt/local-analysis/workspace-hub.
Execute ALL 5 tasks. Commit after each. Do NOT push. Close each issue.

TASK 1: OCR/semantic index for 6 standards orgs (#1772)
- Search for standards file locations on disk
- Create: data/document-intelligence/ocr-index-standards-orgs.md covering: for each org (SNAME, OnePetro, BSI, NORSOK, API, ASTM) how many files, scan vs digital, OCR needs, estimated processing time, semantic index structure
- Commit: git add that file && git commit -m 'doc-intel: OCR and semantic index plan for 6 standards orgs (#1772)'
- Close: gh issue close 1772 -c 'OCR index plan at data/document-intelligence/ocr-index-standards-orgs.md'

TASK 2: Cross-drive dedup audit (#1757)
- Read any existing dedup reports: search_files pattern='dedup' output_mode=files_only
- Create: docs/document-intelligence/cross-drive-dedup-audit.md covering: what exists on /mnt/ace vs DDE, file count comparison, dedup strategy, tool recommendations
- Commit: git add that file && git commit -m 'doc-intel: cross-drive dedup audit (#1757)'
- Close: gh issue close 1757 -c 'Dedup audit at docs/document-intelligence/cross-drive-dedup-audit.md'

TASK 3: DDE remote literature migration plan (#1863)
- Create: docs/document-intelligence/dde-lit-migration-plan.md covering: 14.6 GB / 5,456 PDFs, storage requirements, bandwidth estimate, priority ordering by domain, indexing strategy post-migration
- Commit: git add that file && git commit -m 'doc-intel: DDE literature migration plan (#1863)'
- Close: gh issue close 1863 -c 'Migration plan at docs/document-intelligence/dde-lit-migration-plan.md'

TASK 4: Conference indexing plan (#1862)
- Create: docs/document-intelligence/conference-index-plan.md covering: 38,526 papers across 30 collections (OTC, OMAE, ISOPE, DOT, SPE), collection-by-collection breakdown, phased indexing strategy, metadata extraction priorities, time estimates
- Commit: git add that file && git commit -m 'doc-intel: conference indexing plan for 38K files (#1862)'
- Close: gh issue close 1862 -c 'Conference index plan at docs/document-intelligence/conference-index-plan.md'

TASK 5: GTM Job Market Scan strategy (#1671)
- Create: docs/business/gtm-job-market-scan-strategy.md covering: job board sources (LinkedIn, Indeed, Rigzone), keywords for offshore engineering, data fields to extract, mapping to ACE services, automation approach for recurring scans
- Commit: git add that file && git commit -m 'doc-intel: GTM job market scan strategy (#1671)'
- Close: gh issue close 1671 -c 'GTM scan strategy at docs/business/gtm-job-market-scan-strategy.md'

RULES: Commit after each task, do NOT push. Close each issue. All paths under /mnt/local-analysis/workspace-hub/"
echo "Batch 2 done: $(date)"

sleep 30

echo "=== BATCH 3 (5 issues: #1769 #1294 #1291 #1575 #1643) ==="
echo "Started: $(date)"
h-router-gemini -t terminal,file -q "You are ACE Engineer advance scout. Working directory: /mnt/local-analysis/workspace-hub.
Execute ALL 5 tasks. Commit after each. Do NOT push. Close each issue.

TASK 1: Phase B Summarization Plan (#1769)
- Read docs/document-intelligence/ for Phase B docs
- Create: docs/document-intelligence/phase-b-summarization-plan.md covering: current state 61.9%, 394K unsummarized docs by domain, batch strategy (100K per batch), estimated compute time, quality checks, path from 61.9% to 90%
- Commit: git add that file && git commit -m 'doc-intel: Phase B summarization plan for 394K documents (#1769)'
- Close: gh issue close 1769 -c 'Phase B plan at docs/document-intelligence/phase-b-summarization-plan.md'

TASK 2: TDD Fixtures from Worked Examples (#1294)
- Create: docs/document-intelligence/tdd-fixtures-plan.md covering: how to curate 3,683 extracted CSVs into clean test fixtures, organization by domain, integration with digitalmodel tests, priority fixtures for highest-value domains
- Commit: git add that file && git commit -m 'doc-intel: TDD fixture curation plan (#1294)'
- Close: gh issue close 1294 -c 'TDD fixtures plan at docs/document-intelligence/tdd-fixtures-plan.md'

TASK 3: SNAME Naval Architecture Knowledge Extraction (#1291)
- Create: docs/document-intelligence/sname-extraction-plan.md covering: SNAME collection scope, key topics (hull forms, resistance, propulsion, stability, structural), extraction pipeline design, integration with digitalmodel/naval_architecture
- Commit: git add that file && git commit -m 'doc-intel: SNAME knowledge extraction plan (#1291)'
- Close: gh issue close 1291 -c 'SNAME extraction plan at docs/document-intelligence/sname-extraction-plan.md'

TASK 4: Holistic Resource Intelligence (#1575)
- Create: docs/document-intelligence/holistic-resource-intelligence.md covering: unified tracking for all online resources, /mnt/ace backup monitoring, cross-domain leverage opportunities, unified resource dashboard architecture
- Commit: git add that file && git commit -m 'doc-intel: holistic resource intelligence plan (#1575)'
- Close: gh issue close 1575 -c 'Unified resource intelligence at docs/document-intelligence/holistic-resource-intelligence.md'

TASK 5: OCR Parser Registry (#1643)
- Create: docs/document-intelligence/ocr-parser-registry.md covering: OCR parser registration in doc-intel pipeline, supported types (scanned PDF, TIFF, PNG), tesseract integration, quality metrics, fallback strategies
- Commit: git add that file && git commit -m 'doc-intel: OCR parser registry design (#1643)'
- Close: gh issue close 1643 -c 'OCR parser registry at docs/document-intelligence/ocr-parser-registry.md'

RULES: Commit after each task, do NOT push. Close each issue. All paths under /mnt/local-analysis/workspace-hub/"
echo "Batch 3 done: $(date)"

sleep 30

echo "=== BATCH 4 (5 issues: #1676 #1771 #1816 #1817 #1825) ==="
echo "Started: $(date)"
h-router-gemini -t terminal,file -q "You are ACE Engineer advance scout. Working directory: /mnt/local-analysis/workspace-hub.
Execute ALL 5 tasks. Commit after each. Do NOT push. Close each issue.

TASK 1: Market-Driven Repo Roadmap (#1676)
- Read digitalmodel/ package structure
- Create: docs/engineering/repo-roadmap-market-aligned.md covering: current package maturity vs job market demand, alignment with in-demand skills (OrcaFlex, hydrodynamics, structural, pipeline, geotechnical), gaps, 6-month development priorities aligned with GTM strategy
- Commit: git add that file && git commit -m 'engineering: market-aligned repo roadmap (#1676)'
- Close: gh issue close 1676 -c 'Market-aligned roadmap at docs/engineering/repo-roadmap-market-aligned.md'

TASK 2: DDE Unique Project File Index (#1771)
- Create: docs/document-intelligence/dde-unique-file-index-plan.md covering: unique files on DDE not on /mnt/ace, estimated count, domains represented, indexing strategy, priority ordering
- Commit: git add that file && git commit -m 'doc-intel: DDE unique file index plan (#1771)'
- Close: gh issue close 1771 -c 'DDE unique file plan at docs/document-intelligence/dde-unique-file-index-plan.md'

TASK 3: Marine Excel Extraction (#1816)
- Create: docs/document-intelligence/marine-excel-extraction-plan.md covering: 419 marine Excel refs organized by sub-domain, extraction priority, template matching for recurring calcs, mapping to digitalmodel modules
- Commit: git add that file && git commit -m 'doc-intel: marine Excel extraction plan for 419 refs (#1816)'
- Close: gh issue close 1816 -c 'Marine Excel plan at docs/document-intelligence/marine-excel-extraction-plan.md'

TASK 4: Large Workbook Streaming (#1817)
- Create: docs/document-intelligence/large-workbook-streaming-plan.md covering: 4 skipped workbooks over 15MB, streaming mode approach, memory-efficient extraction, success criteria
- Commit: git add that file && git commit -m 'doc-intel: large workbook streaming plan (#1817)'
- Close: gh issue close 1817 -c 'Large workbook plan at docs/document-intelligence/large-workbook-streaming-plan.md'

TASK 5: Promotion Feedback Loop (#1825)
- Create: docs/document-intelligence/promotion-feedback-loop.md covering: extraction output to digitalmodel code promotion flow, automated ledger update, quality gates, tracking which extractions become production code
- Commit: git add that file && git commit -m 'doc-intel: promotion feedback loop design (#1825)'
- Close: gh issue close 1825 -c 'Promotion feedback loop at docs/document-intelligence/promotion-feedback-loop.md'

RULES: Commit after each task, do NOT push. Close each issue. All paths under /mnt/local-analysis/workspace-hub/"
echo "Batch 4 done: $(date)"

echo ""
echo "=== ALL 4 BATCHES COMPLETE ==="
echo "Finished: $(date)"
echo "Check results:"
echo "  gh issue list --label agent:gemini,priority:high"
echo "  git log --oneline -25"
