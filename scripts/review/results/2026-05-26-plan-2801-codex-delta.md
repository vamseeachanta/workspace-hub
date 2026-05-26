# Plan Review — #2801 — Codex (delta on D1/D2/D3, adversarial)

**Provider:** Codex CLI 0.133.0 via `env -u CLAUDECODE`. Sandbox blocked skill load (bwrap loopback); inline-text review.
**Verdict:** MAJOR (5 MAJOR + 4 MINOR/nits). Reviewed delta only.

## MAJOR
- **DC1 — b1 side-effect-freedom not enforceable.** No proof plan-approval-gate.sh supports no-write/no-log mode; readonly test only snapshots fixture root → misses writes to state dirs, logs, locks, shell history. Fix: run b1 in isolated temp repo with HOME/XDG/cache/log redirected, OR add+test an explicit `--dry-run --no-log` hook contract.
- **DC2 — b5 hash determinism under-specified.** Key-sort doesn't canonicalize array order, dup entries, slash direction, drive-letter case, symlink-expanded/$HOME-equivalent paths. Same policy → different hash; or different policies normalized-equal. Fix: canonical permission schema (sort non-semantic arrays, per-field path normalization, reject abs HOME paths); test Win-vs-Linux equivalent policy beyond CRLF.
- **DC3 — compute_floor has no typed schema.** Could compare only cores → CONFORMS while RAM/disk/GPU below floor. Fix: typed per-field floor (cores_min, ram_gib_min, disk_free_gb_min, gpu_required); GiB-vs-GB rule; unknown-GPU/partial-floor handling; below-floor tests per field.
- **DC4 — commit-on-change hash excludes only generated_at.** Other volatile fields (memory mtime, disk-free jitter) cause churn OR suppress real drift if exclusions broadened ad hoc. Fix: define exact canonical hash payload by field path (allowlist), not single-timestamp exclusion; tests for mtime, disk jitter, map/list ordering, probe order.
- **DC5 — per-machine weekly wiring under-specified.** No existing Linux installer named (only weekly-hermes-parity-review.sh attested); setup-scheduler-tasks.ps1 not attested; no AC inspecting installed cron/task defs or verifying both invoke same command/repo/branch/commit-on-change/push. Fix: name exact files, generate scheduled commands from ONE shared template/config, add dry-run render checks for both OSes.

## MINOR / Nits
- MC1: `sibling:/mnt/local-analysis/<repo>` leaks machine layout despite "no paths" deliverable — prefer `sibling`+repo-name label, not full path.
- MC2: baseline subset check needs key normalization vs tier1_repos (nested/sibling/alias/case/rename).
- MC3: behavior results mix enum (b1-b4) + hash (b5) — split types so serialization/rendering tests don't assume one scalar.
- Nit: artifact map lists Gemini delta before result exists (mark pending); `deny`/ok ambiguous — pin exact serialized value.

## Author questions
- Publish machine checkout roots (`sibling:/mnt/...`) or only repo labels + access mode?
- b5: exact byte-equivalent after canonicalization, or semantic permission equivalence?
