> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-10
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_verification_queue_mixed_line_endings.md

---
name: feedback_verification_queue_mixed_line_endings
description: llm-wiki verification-queue CSV has mixed LF/CRLF rows; edit it with binary I/O or text-mode strips 340 CRLF rows silently
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 69caff90-5cfe-48ea-b0d5-d43bcc161936
---

The llm-wiki `_verification-queue.csv` files have **mixed line endings**: 10-col-format rows (code_id,table_id,...,csv_path@7,structural@8,issues@9) use LF, but positional-format rows (parse_status@0, the `papers/sect-*` family) use CRLF (`\r\n`).

**Why:** Python's default text-mode `open()` applies universal-newline translation, silently rewriting every `\r\n`→`\n` on read. A 12-row verdict edit then produced a **352-line phantom diff** (12 real + 340 CRLF→LF rewrites of untouched rows). `csv.reader`/`csv.writer` round-trips hit the same trap plus extra requoting. The on-disk file looked correct; only `git diff --numstat` (expect 12/12, saw 352/352) exposed it. Cousin of [[feedback_sparse_worktree_commit_trap]] — committed bytes differ from what you think you wrote.

**Queue-edit invariants (vision batches):** `structural_status` (10-col f[8] / 6-col f[4]) must be `ok`|`flagged`|`no-csv` — NOT a copy of parse_status; batch 13 wrote `verified`/`rejected` there on all 12 rows (caught in review, fixed). When fixing a row in place, split QUOTE-AWARE (`csv.reader(io.StringIO(line))`, never `line.split(",")`) — notes contain commas, and a naive split shatters the quoted note then re-quotes to garbage. bs-7910 queue has MANY duplicate rows (same csv_path, different recorded page = multi-page/dedup artifact); convention is verify the correct-page row + reject the wrong-page dup. Spot-check a batch by EXACT csv_path (editions share table-IDs).

**How to apply:** Edit the queue with **binary I/O** — `data=open(QF,"rb").read(); lines=data.split(b"\n"); ... ; open(QF,"wb").write(b"\n".join(lines))`. Skip any line where `raw.endswith(b"\r")` when matching LF-format targets (your 10-col rows have no trailing `\r`). Always verify `git diff --numstat` equals 2×(rows you changed) before commit. Applies to vision-verify batches and any [[project_llm_wiki_corpus_ingest_cron]] tooling that rewrites the queue (verify_tables.py self-heal already writes via csv — audit it for this).
