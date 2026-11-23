<!-- Generated 2026-06-15. Epic #3043 / sub-issue #3109. Out-of-sample companion to 2026-06-13-fable5-opus-parity-learning.md (#3056). -->
# Provenance

- **Corpus:** ~65 distinct **external** Fable-5 sessions from public Hugging Face datasets — independent of our operation. Raw transcripts stored off-repo at `/mnt/local-analysis/fable5-external-corpus/` (mixed/unspecified licenses + third-party content → never committed; only this PII-free derived analysis lands in the repo, per the public-repo rule and the #3056 precedent).
- **Sources:** `armand0e/claude-fable-5-claude-code` (63 native Claude Code `.jsonl`, 7,431 fable-5 turns, license unspecified); `victor/fable-5-boeing-747-trace` (1 session, MIT); `Glint-Research/Fable-5-traces` (70 MB merged chain-of-thought corpus, AGPL-3.0, 60 sessions / 4,665 turns).
- **Dedup truth:** Glint is an aggregator that had already ingested 59 of the 63 armand0e sessions. Union = **~65 distinct sessions** (64 with full transcripts; 59 also carry an extracted-COT representation). The honest public-pool ceiling today is ~65 distinct, **not** the ~100 originally targeted.
- **Method:** deterministic per-session digest (`digest.py`, no LLM) over the 64 full transcripts → metrics directly comparable to `analysis/parity-baseline.json`. Chain-of-thought stats from the Glint corpus. PII-free by construction (aggregate metrics only; no verbatim user content, repo names, or personal paths reproduced).

---

# External-Corpus Validation: does #3056 hold on other operators' Fable usage?

The internal corpus (#3056, 193 sessions, our two boxes) characterized what Fable did **for us**. Risk: our findings were workspace-hub-specific (triage/review-heavy ops). This report re-runs the same measurement on an **independent** public corpus to separate operator-specific habits from genuine model behavior.

## 1. Headline metric comparison

| Metric | Internal #3056 (193) | External HF (64) | Verdict |
|---|---|---|---|
| **fanout / session** | 0.715 | **0.703** | ✅ Confirmed — near-identical on independent data; Fable's fan-out orchestration (delta D6) is a model property, not our habit. |
| **askuser / session** | 0.104 | **0.031** | ✅ Confirmed + stronger — external operators drove it even more autonomously; one-prompt-per-agent (D2) is intrinsic. |
| **tokens/turn** | ~860 mean | 924 median (p10 208 / p90 2512) | ✅ Same order of magnitude; bimodal in both (5 terse-mode vs 59 synthesis-mode sessions). |
| **avg turns/session** | 91 | 124.8 (median 66, max 644) | ✅ Sustained long-horizon autonomy holds; external skews even longer. |
| **session duration** | 16–36 h longest | max 22.9 h, 14 sessions >4 h | ✅ Multi-hour autonomous runs are normal. |
| **tool mix** | Bash-dominant | Bash 1699 > Edit 1075 > Read 641 > Write 372 | ✅ Bash-first discovery, surgical edits — matches exactly. |

**Bottom line:** every load-bearing #3056 behavioral finding reproduces on an independent operator pool. The parity baseline is not an artifact of our usage.

## 2. New behaviors the external corpus surfaces (internal corpus had none)

- **Vision self-verification loop.** `mcp__Claude_Preview__preview_eval` (90 calls) + `preview_screenshot` (48) + `preview_console_logs` (6): Fable renders generative output (games, 3D, UI), screenshots its own result, evaluates against intent, and iterates — the Boeing-747 trace is the canonical example. Our internal corpus only had vision verification of *extracted tables*, not *generative builds*.
- **Async / scheduled autonomy.** `ScheduleWakeup` (17), `Monitor` (10), `TaskCreate`/`TaskUpdate`/`TaskStop` (58 combined) — self-pacing across wall-clock gaps without operator prompting.
- **Cross-platform.** `PowerShell` (141 calls) — substantial Windows Fable usage we have no internal sample of.
- **Reasoning density (from Glint COT).** Every turn carries chain-of-thought (median 2,365 chars, max 9,145) while **81% of turns are tool actions** (3,799 tool_use vs 866 text) — deep private reasoning, terse public output. This is the mechanism behind D1: Fable thinks a lot, says little.

## 3. Honest caveat — task-mix difference

Public Fable usage skews **creative/build** (games, 3D, web apps); our internal usage skews **ops/triage/review**. This shifts per-session token profiles (external terse-floor is higher because there's less pure metadata-triage). Therefore:

- Treat **cross-pool-stable** behaviors as the real engineering targets: ~0.7 fanout/session, ~0 clarification breaks, Bash-dominance, bimodal output, deep-reason/terse-output.
- Treat **task-specific** numbers (exact tokens/turn floor) as profile-dependent — calibrate per task class, not globally.

## 4. Impact on the parity workstream

- **#3056 deltas D2 (autonomy), D6 (fan-out), D1 (output shape):** upgraded from "observed in our corpus" to **confirmed on independent data** — raises confidence in the #3106 (de-prescription) and #3107 (fable-mode adapter) bets.
- **#3107 fable-mode adapter** should encode the **deep-reason / terse-output** pattern explicitly (summarized thinking + compressed surface output) and the **vision self-verification loop** as a reusable sub-pattern for generative/build tasks.
- **#3061 instrumentation / `parity-baseline.json`** should gain an `external_baseline` column so live-Opus regression checks compare against both pools.
- **No internal Opus sample for build/creative tasks** — a gap: our ecosystem rarely exercises the generative self-verification loop, so we can't yet measure Opus parity there. Flag for a targeted probe.

## Appendix — reproduction
- Corpus + manifest: `/mnt/local-analysis/fable5-external-corpus/manifest.csv` (124 rows incl. dual representations; ~65 distinct sessions).
- Digest tool: `/mnt/local-analysis/fable5-external-corpus/digest.py` (deterministic; promote into `scripts/ai/` alongside `parity_metrics.py` if this becomes recurring).
- Per-session metrics: `armand0e/digest.json`.
