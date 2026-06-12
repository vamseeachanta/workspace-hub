# Session Handoff — FDAS riser-buckling campaign + corpus-ingestion handover (2026-06-08)

Session id: 4c5cc728-466d-406e-99c3-9c24c2b3802d. Repo memory:
`.claude/memory/` → `project_fdas_wiki_population_loop.md` (the dispatch loop +
every gotcha) and `project_llm_ingestion_playbook_public_repo.md`.

## What this session did

Two distinct bodies of work:

### A. raw-to-knowledge-playbook (PUBLIC) — strengthened
- Filed epic #22 + strengthening issues #13–#21; ran an adversarially-verified
  multi-agent research workflow (6 researchers → 6 fact-checkers); posted verified
  findings on #14–#19.
- Merged: docs 14 (chunking/embedding), 15 (retrieval-eval), 16 (lifecycle), 17
  (cost-economics), 18 (security/PII), 19 (trust-boundary & private-mode);
  `skills/` (5 validated SKILL.md templates + authoring standard + validator +
  evals); `examples/minimal-ingest/` (runnable, CI-green); `QUICKSTART.md`;
  pre-commit + CI verify-gate. All on `main`.

### B. llm-wiki-fdas (PRIVATE, Frontier Deepwater client) — riser-buckling assessment
Per-issue host-side sweep dispatched to ace-linux-2, verified by Claude + an
independent Codex recompute each batch. **Screening program #2–#7 COMPLETE:**

| Issue | PR | Finding |
|---|---|---|
| #2 basis | #9 merged | 810-ft unrestrained fails Euler |
| #3 | #10→#11 merged | bay bowing can't absorb set-down (~320–554 ksi) |
| #4 | #12 merged | survival pushdown FAILS on stress (~102–138 ksi) |
| #5 | #13 merged | Chuck's chatbot drag total is strakes-only, undercarries ~6.4%; VIV lock-in OPEN |
| #6 synthesis | #14 merged | honest article tying it together |
| #7 | #15 merged | tendon tension FAILS (~9,900 kip / 120 ksi) |

**Campaign verdict:** the free-standing riser FAILS every conservative screen;
the verdict pivots on two inputs the screens can't make.

Also landed: index auto-generation (PR #23 merged — edit page frontmatter +
`uv run scripts/gen_index.py`, never hand-edit the README index tables);
global-model child issues #16–#22; global-model scaffold in **digitalmodel**
(PR #687 merged, `model_library/frps_ssr_global_riser/`, input YAML only, no run).

## Open items (carry forward — DO NOT lose)

1. **⚑ Roy demand-definition question** (posted llm-wiki-fdas #4): does his
   "5–10 ft pushdown" already net the slip-joint stroke? Decides #4/#7 pass/fail
   and the global-model demand variant. If answered → re-run #4/#7 screens + set
   the digitalmodel `demand.setdown_definition` variant.
2. **verify-gate guard NOT applied.** Labels (`needs-verify`/`verified`) exist;
   the branch-protection command must be run BY THE HUMAN (auto-mode classifier
   blocks an agent setting enforce_admins on a client repo). Command is in the
   session transcript.
3. **Global model** (#16–#22): needs OrcaFlex + an analyst (not automatable);
   scaffold ready in digitalmodel PR #687 (merged); section basis (#3) and Roy
   demand (#4/#7) are the two open inputs, carried as variants.
4. **CORPUS LARGELY UN-INGESTED — the big remaining work.** llm-wiki-fdas was
   populated ONLY from the riser-buckling email thread (2 email extracts). The
   raw corpus `/mnt/ace/frontierdeepwater` (483 MB; ace-linux-2 sees it at
   `/mnt/remote/ace-linux-1/ace/frontierdeepwater`) has ~110 doc files NOT
   ingested: 50 pptx, 25 msg (Outlook binary), 17 xlsx, 14 docx, 1 pdf, 7 txt.
   ⚠️ that path is the frontierdeepwater COMPANY REPO → content-triage + value-
   filter required (much is code/config/venv/marketing). ~2% populated. Full
   ingestion = a separate corpus-driven campaign → see the prompt below.

## Dispatch + verify loop (reuse for the corpus ingestion)

- Launch on ace-linux-2: `ssh vamsee@ace-linux-2 'bash -ls'` (LOGIN shell or PATH
  misses → 65-byte dead log), inside: `nohup "$(command -v claude)"
  --dangerously-skip-permissions -p "$(cat prompt)" < /dev/null > log 2>&1 &`
  (absolute binary; `< /dev/null` or it hangs). Classifier blocks the
  skip-permissions launch until the HUMAN types "use dangerously skip
  permissions" in-session.
- Verify each PR: grep the diff yourself (never trust the producer's self-cert),
  then independent Codex: `codex exec -s workspace-write --skip-git-repo-check
  "<prompt>" < /dev/null > review.md 2>&1` (write to a FILE; stdout buffer-lossy;
  run from write-root). Apply `verified` only after Codex confirms.
- Codex repeatedly caught what structural/single-reviewer verification missed:
  omitted governing cases, demand-undercounting, wrong MATCH calls. Always use
  the independent second model on engineering content.

---

## HANDOVER PROMPT — populate llm-wiki-fdas from the full corpus (paste into a fresh session)

```text
# HANDOVER — Populate llm-wiki-fdas from the full Frontier Deepwater corpus

## Mission
The PRIVATE wiki vamseeachanta/llm-wiki-fdas is ~2% populated: it holds one
engineering assessment (riser buckling #2–#7) from 2 email extracts. The raw
Frontier Deepwater corpus has ~110 more documents NOT ingested. Ingest the rest
using the house method — content-triaged, provenance-clean, provisional-by-default.

## Read FIRST (authoritative)
- gh issue view 8 -R vamseeachanta/llm-wiki-fdas  (exact vocabulary + engineering-
  screen method; every batch reads this first).
- raw-to-knowledge-playbook (PUBLIC, /mnt/local-analysis/raw-to-knowledge-playbook)
  docs 01–19 — the per-format lanes (09 office, 10 structured, 11 imagery, 07/18/19
  governance + private-mode posture).
- Repo memory project_fdas_wiki_population_loop.md (dispatch loop + gotchas).

## Corpus (inventory it yourself first)
/mnt/ace/frontierdeepwater on ace-linux-1; ace-linux-2 reaches it read-only at
/mnt/remote/ace-linux-1/ace/frontierdeepwater. ~110 docs: 50 pptx, 25 msg (Outlook
binary — convert with extract_msg/msgconvert), 17 xlsx, 14 docx, 2 ppt, 1 pdf, 7 txt.
⚠️ It is the frontierdeepwater COMPANY REPO, not a clean doc set — also code/config/
venv/Mktg. So: (1) TRIAGE BY CONTENT not extension; (2) VALUE-FILTER (skip code/
config/venv/agents/low-content marketing); (3) route each real doc to its lane
(pptx→reporting-concepts+content; xlsx→calc-logic vs data, tier by formula density;
docx→reports via mammoth→semantic-md; msg→email extracts under sources/email/ like
the 2 existing; pdf/txt→standard).

## Two invariants (NEVER violate — doc 19)
1. Raw file NEVER enters any repo — commit DERIVED data + a sources: sha256 pointer
   only (extract binaries to text/CSV, never git add the binary).
2. PRIVATE never crosses to public; visibility: private on every page.
Plus: provenance on every value; INDEPENDENT publish-time grep (producer never
self-certifies); deterministic extraction; provisional-by-default.

## Dispatch (ace-linux-2 host-side sweep)
ssh vamsee@ace-linux-2 'bash -ls'  → inside, nohup "$(command -v claude)"
--dangerously-skip-permissions -p "$(cat promptfile)" < /dev/null > log 2>&1 &
(login shell + absolute binary + </dev/null). Classifier blocks the
skip-permissions launch until the human types explicit authorization in-session.
Per batch: one logical grouping → one PR off main → leave UNMERGED, apply
needs-verify → comment on its issue. llm-wiki-fdas index is AUTO-GENERATED
(scripts/gen_index.py): edit a page's frontmatter + run it; never hand-edit
pages/README.md or reports/README.md.

## Verify loop
Per PR: grep the diff yourself for invariants/vocab/leaks; then INDEPENDENT Codex:
codex exec -s workspace-write --skip-git-repo-check "<prompt>" < /dev/null >
review.md 2>&1 (write to a FILE; run from write-root). Apply verified only after
Codex confirms; fix-up round if needed. PII-sensitive docs sent to a hosted VLM →
apply doc-18 fail-closed egress gate.

## Plan
1. TRIAGE pass: classify all ~110 docs (technical / marketing / noise), value-rank,
   write the inventory to a tracking issue.
2. Create CORPUS-INGESTION issues (distinct from analysis #2–#7), one per lane
   (emails, technical decks, calc/data Excel, Word reports).
3. Dispatch → verify → Codex → merge, smallest-value-clear first. Each doc → a
   sources/ extract + a wiki page, provenance, provisional.

## Don't lose (separate analysis-side track)
- ⚑ Roy demand question on #4 (gates #4/#7 + global-model demand).
- verify-gate guard (human must run the branch-protection command).
- Global model: digitalmodel PR #687 merged (scaffold); child issues #16–#22;
  needs OrcaFlex + analyst.

## Acceptance
Each doc: sources/ extract (no raw binary committed) + a well-formed wiki page,
provenance on every value, provisional-by-default, issue-#8 exact tokens,
independent grep clean, one unmerged PR per batch. Report coverage %.
```
