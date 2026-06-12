---
name: project-llm-ingestion-playbook-public-repo
description: "Public methodology playbook distilled from llm-wiki sessions — staged locally, publish decision pending"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9ccbd8e4-685b-45c7-ad23-652ad04a35c1
---

VA asked (2026-06-04) for a peer-shareable PUBLIC repo distilling the llm-wiki
ingestion methodology across Claude/Codex/Hermes sessions. Drafted at
`/mnt/local-analysis/llm-ingestion-playbook/` (not yet git init / not published):

- README + CONTRIBUTING + 8 docs: 01 document taxonomy (doc types × extraction
  levels L0–L5 × storage × single-shot-vs-iterative), 02 pipeline architecture,
  03 verification playbook, 04 failure modes (16, A/B/C classes), 05 good
  practices **GP-01…GP-26 append-only numbering (next: GP-27)**, 06 multi-agent
  orchestration, 07 data governance, 08 skills catalog.
- Sanitized + grep-verified against client names/mounts/hostnames (one Hermes
  reference rewritten as "internal monitoring agent"). Publisher names kept
  (public bodies). Keep CONTRIBUTING rule: evidence-backed, one GP per PR,
  never renumber.
- Sources: 4 parallel Explore agents over llm-wiki repo+issues, Claude memory/
  handoffs/skills, Codex (~80 sessions) + Hermes traces. See
  [[project_llm_wiki_corpus_ingest_cron]] for the underlying campaign.

**2026-06-06 exit handoff doc**: workspace-hub
`docs/session-handoffs/2026-06-06-raw-to-knowledge-playbook-exit.md` committed
`e7ca128fb` — NOTE: landed on pre-existing branch
`fix/track-fleet-skills-2925-portable` (repo wasn't on main; push deferred per
known check-all sibling-layout pre-push blocker) → cherry-pick onto a fresh
origin/main branch when pushing, per [[feedback_recover_stale_branch_for_pr]].
Also cleared a stale 2-day-old `.git/index.lock` (no live git procs, verified
before removal). Signal message final form = objective + "can any of you
help" + repo link + briefs #2–#12 pointer (drafted, VA to send).

**2026-06-06 HANDED TO EXTERNAL AI EXPERTS for deep research** (session exit):
repo at 5b0dc12, clean, local==origin; README now has a "research program"
entry-point section (epic #1, briefs #2–#12, ground rules, order #2→#12→#5).
Expect inbound expert findings as PRs/issue comments on the playbook —
review against the doc-12 trust rubric + CONTRIBUTING evidence bar before
merging; GPs still require pilot evidence.

**2026-06-06 ultra-research program filed** (VA directive): playbook EPIC #1 +
children #2–#11 (one per raw format: PDF, scanned, photo, calc-Excel,
data-Excel/CSV, Word, PPT, solver-deck, solver-output, web) + #12
(knowledge-store data formats, generic) — each a deep-research brief w/
baseline refs, 5-6 research questions, deliverables = lane-doc/flowchart/
doc-12 updates + candidate GPs (minted only after pilot evidence). PRIVATE
pair: llm-wiki#420 storage-architecture epic (queues→SQLite assessment vs
B1–B7 hazards incl. 3 coexisting queue schemas, 18k CSV git-scale, frontmatter
schema CI, migration triggers BEFORE pain, pilot-one-domain rule). Suggested
order: #2 → #12 → #5. Research NOT yet run — issues are briefs.

**2026-06-05 tooling research + flowcharts** (commit 7d35ad8): doc-12 vetted OSS
landscape (3 web-research agents, license-VERIFIED) — KEY FINDING: **PyMuPDF is
AGPL-3.0** (fine internal-only; exit path pdfplumber/Docling MIT); adopt list:
Docling, gmft, Camelot v2, PaddleOCR, CleverCSV, frictionless-py, pandera,
python-calamine, ImageHash, openpyxl, python-docx/pptx, mammoth, oletools (no
GPLv3 pcodedmp extra); NO permissive maintained Excel formula evaluator —
pattern = openpyxl graph + `formulas`(EUPL, arm's-length oracle) or
xlcalculator(MIT); avoid marker/pycel/koala2/Nougat/MegaParse/LangChain-wrappers.
Doc-13 = 11 Mermaid lane flowcharts (master router + 10 lanes), all
render-validated via mermaid-cli + system Chrome (PUPPETEER_EXECUTABLE_PATH;
note: `\n` in labels renders literally — use `<br>`; no colons in edge text).
Integration tracked: llm-wiki#414 (gmft/Camelot pilots vs find_tables, AGPL
register, CleverCSV/frictionless, Docling chunker) + digitalmodel#686
(Excel→code oracle pattern, calamine, pandera/frictionless) — VA approved
filing after auto-mode classifier denial.

**2026-06-05 RENAMED → raw-to-knowledge-playbook** (VA choice; old llm-ingestion-playbook
URL redirects): repo = https://github.com/vamseeachanta/raw-to-knowledge-playbook,
local = /mnt/local-analysis/raw-to-knowledge-playbook. Commit 0046475 adds
docs/11 imagery lane — photos DESCRIBED not extracted (description records:
falsifiable observations / verbatim legible text / capture metadata / dated
series; verify w/ independent 2nd description), scans = `ocr-interpreted`
labeled interpretation, Excel split data-vs-calculation-vs-canvas routed by
scanned structure not filename; GP-38/39 (next GP-40); README retitled.

**2026-06-05 structured-data lane** (commit e01bbbf): docs/10 adds CSV/delimited
+ solver-deck/output-listing lane — dialect probing, content-parity (not
row-count) validation, units/sign convention sidecars, deck→YAML-config
round-trip (per [[feedback_externalize_all_config_to_yaml]]), a/b/c
output-driven contract + assumption ledger (per
[[project_analysis_domain_objective]]), dual native/pipeline export
auto-detection; GP-32…37 (next GP-38) + failure class E (7 entries). Solver
vendor names genericized in public text.

**2026-06-05 Office-format extension** (commit bc4f4c6): docs/09-office-formats.md
adds D1-content/D2-logic/D3-format extraction *dimensions* (4th taxonomy axis);
Excel lane grounded in crossprovider hermes/codex memories (4,125-workbook
inventory, tier P0–P2×1–6, formula→loop compression 2.5–44×, cached_ok cell
classification, 656K-formula stub-pileup lesson, dark-intelligence
strip-context-keep-methodology); GP-27…31 added (next GP-32) + failure class D
(5 entries). Repo NAME KEPT — already format-agnostic; rename would break
published peer links. Sanitized: wrote "three analysis domains" not domain
names, no client/mount/host identifiers (grep-verified).

**PUBLISHED 2026-06-04** (VA approved): public repo
https://github.com/vamseeachanta/llm-ingestion-playbook (root commit 88e771b,
11 files incl. dual LICENSE CC-BY-4.0/MIT). Future practices append as GP-NN
via the CONTRIBUTING format (one evidence-backed practice per PR, never
renumber).
