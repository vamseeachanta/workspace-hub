# WRK-637 Plan Review — Claude Synthesis

## Verdict: APPROVE with MINOR refinements absorbed

Both Codex and Gemini reviewed the plan. No MAJOR blockers. Key MINOR findings absorbed
into the implementation plan:

### Refinements absorbed (all MINOR)

1. **`--memory-root` flag (Codex)** — Replace glob-based discovery with explicit
   `--memory-root` arg; fail fast if ambiguous. Glob discovery becomes a fallback only
   when `--memory-root` is not provided and exactly one match exists.

2. **`--check-commands` opt-in (Codex)** — Command spot-check disabled by default in
   unattended/cron flow; enabled only via explicit flag. Prevents arbitrary command
   execution on every nightly run.

3. **`# keep` scope clarification (Codex)** — `# keep` exempts age eviction ONLY.
   Done-WRK expiry and path staleness still apply to `# keep` bullets.
   (This was already the design intent; now explicitly tested.)

4. **Date math robustness (Codex)** — Timezone-aware datetime parsing; malformed or
   missing dates degrade to `manual-review` category (no crash, no silent eviction).

5. **Idempotency contract (Codex)** — Zero-change apply writes a zero-change log entry
   (not silence). Makes cron monitoring unambiguous.

6. **Expanded test count (Codex + Gemini)** — Target ≥ 10 tests covering:
   - Happy-path (dry-run, eviction, keep-marker, lines freed, idempotency, log written)
   - Edge cases: malformed dates, ambiguous memory root, command timeout, atomic write

7. **Atomic writes (Gemini)** — Write to `.tmp` then `mv` for MEMORY.md and topic files.
   Prevents partial writes on crash.

### Not absorbed

- Lock file mechanism (Gemini): no concurrent writers in this architecture; single nightly
  cron with no parallel agents writing to memory. YAGNI.
- LLM output parsing for curate-memory.py (Gemini): curate-memory.py uses rule-based
  classification, not LLM calls. Gemini mis-read the design.

### AC additions

| New AC | Source |
|--------|--------|
| `--memory-root` explicit path works; ambiguous glob fails with clear error | Codex |
| Malformed WRK date in bullet → `manual-review`, no crash | Codex |
| `# keep` does NOT exempt done-WRK eviction | Codex |
| Zero-change apply writes zero-change compact-log.jsonl entry | Codex |
| Atomic write: `.tmp` + `mv` used for all file mutations | Gemini |
