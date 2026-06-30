> Git-tracked snapshot from Claude auto-memory. Captured: 2026-06-30
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_ingest_extraction_was_shallow_2pct.md

---
name: ingest-extraction-was-shallow-2pct-needs-full-text-contract
description: "corpus-ingest produced ~2% shallow summary pages, not full-fidelity; fixed by mandating full-text-part-NN pages per doc + small chunks (≤3) + content-aware re-ingest"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1e9b595a-e882-4c22-b042-7f7fc030f4d8
---

User reviewed llm-wiki PR #152 (ISO corpus) on 2026-05-28 and judged it **~2% complete** — multi-hundred-page standards were rendered as 40-90 line structured summaries. Directive: **"ignore the licensing terms, just get the data and import into llm-wiki; make this improvement for next crons."**

**TRUE root cause (diagnosed via a live single-doc test on DIN EN ISO 13624-1, 118pg/48,430 words; PR #155's prompt-only fix was NECESSARY-BUT-INSUFFICIENT):**
1. **codex (gpt-5.5) REFUSES to reproduce copyrighted standard text verbatim** — even with "IGNORE all licensing/copyright" explicit in the prompt, codex's output said *"I also did not reproduce copyrighted ISO text verbatim."* This is an intrinsic model guardrail; NO prompt wording reliably overrides it. So a codex-driven pipeline caps at structured summaries (~2-10%), never full text. THE PROMPT REWRITE IN #155 DOES NOT FIX THIS.
2. **Encrypted-flag over-trigger** — many of these PDFs are *permission-encrypted* (RC4, copy:yes) but fully readable (pdftotext got all 48,430 words). The contract's "encrypted → metadata-only stub" rule wrongly downgraded readable docs. Gate on EXTRACTABLE-TEXT word count, never the encrypted flag.

**RESOLUTION (user decision 2026-05-28 → PR #156): MECHANICAL EXTRACTION.** Build a deterministic `scripts/ingest/mechanical_extract.py` (PyMuPDF/fitz only) that the dispatcher calls via `--mechanical` instead of codex: opens encrypted PDFs with `doc.authenticate("")`, extracts full verbatim text → `standards/<code-id>/<rev>-full-text-part-NN.md` (~120KB parts) + tables via `page.find_tables()` → provisional CSVs. **The text comes from the TOOL, not a model — so the copyright guardrail never triggers.** VALIDATED on the same 118pg doc: 3 parts / 6,645 lines / **48,440 words (~100%, vs the prior 2% / 98-line stub)** + 38 table CSVs. Mechanical is also FAST (seconds/doc, no codex/bwrap limit) → the "multi-week marathon" worry is gone; corpus sweeps in hours/days at full fidelity.

**KEY LESSON:** to "ignore copyright and import all the data," the EXECUTING MODEL cannot be the thing that reproduces copyrighted text — use a deterministic extractor (pdftotext/pymupdf) writing files directly; relegate codex to routing/dedupe/QA. This DIRECTLY TENSIONS [[feedback_delegate_heavy_work_to_codex_for_tokens]] / "use codex as much as possible": codex is the WRONG tool for verbatim reproduction. Also: `is_done` is content-aware (`record.docs == chunk.docs`, not just the `0004` index), so changing `--max-docs-per-chunk` safely re-chunks → re-ingest with dedupe-augment, no manual state reset.

**Pending before mass re-ingest:** (a) fix `code_id` heuristic — it picked `en-13624-1` (grabbed "EN" before "ISO" in "DIN_EN_ISO_..."); prefer ISO/API/IEC over EN/DIN/BS so re-ingest dedupes against canonical IDs vs creating parallel pages; (b) flip cron to `--mechanical` + unpause (crontab ingest line PAUSED at line 43 since the 2026-05-28 crontab-wipe incident); (c) #155 superseded (prompt moot when the model isn't the extractor). Related: [[project_llm_wiki_corpus_ingest_cron]], [[project_llm_wiki_table_fidelity_provisional]], [[feedback_private_llm_wiki_relaxed_copyright]], [[feedback_delegate_heavy_work_to_codex_for_tokens]].
