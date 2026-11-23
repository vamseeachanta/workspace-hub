# Plan for #3250: Cross-provider skill-drift detector + alert — epic #3248

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-06-26
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3250
> **Client:** N/A
> **Lane:** lane:claude   <!-- harness/self-improvement; relabel the issue if scope class changed -->
> **Review artifacts:** scripts/review/results/2026-06-26-plan-3250-claude.md | ...-codex.md

---

## Resource Intelligence Summary

### Existing repo code
- Found: `scripts/curation/audit_skill_currency.py` — `audit(machine)` (lines 120-154) already computes the cross-provider family diff and emits FACTS to `.claude/state/skill-currency-<machine>.json`: `gemini_unexpected` / `gemini_expected` (COUNTS only), `index_dangling`, `canonical_count`, `gemini_present`, `schema_version: 1`. The family-diff itself (`_families()`, allowlist `_allowed()`, `_index_dangling()`) is the **authoritative drift computation — this plan must NOT duplicate it.** Gap: the audit emits only counts, not the *names* of the unexpected families, so a drift report cannot say *which* families drifted.
- Found: `scripts/operations/venue_absence_detector.py` — the **exact detector pattern to mirror**: a PURE `evaluate(...)` core (no IO/clock/subprocess, fully unit-testable, fails closed on malformed telemetry) + a thin CLI (`run_cli`) that gathers inputs, calls the core, and routes each alert through an **injectable `notify_fn`** (default `_default_notify` shells `bash scripts/notify.sh cron <job> fail <detail>`). Tests inject `notify_fn` to assert call counts without shelling out.
- Found: `scripts/notify.sh` — `bash scripts/notify.sh <source> <job> <status> [details]`; appends one JSONL event `{"source","job","status","ts","details"}` to `logs/notifications/YYYY-MM-DD.jsonl`; always exits 0; `status` is `pass|fail`. No jq dependency.
- Found: `scripts/monitoring/equivalence_state.py` — `publish(repo, role, content, *, ref=...)` writes a `<role>.json` blob into a dedicated git ref via plumbing + `--force-with-lease` (never touches `main`); `collect(repo, ref=...)` pulls every box's blob. `StoreUnavailable` on git failure.
- Found: `scripts/curation/curate_session_memory.py::publish_fingerprint` (lines 240-259) — the **bounded-publish precedent**: runs `equivalence_state.py publish` as a `subprocess.run(..., timeout=PUBLISH_TIMEOUT_S=90)` so a hung git push (observed stuck >1h) can never stall the cron; returns a fail-soft string (`publish-timeout`/`publish-error`/`publish-rc<n>`), never raises.
- Found: `scripts/readiness/build-equality-matrix.py::skill_currency_verdict` (lines 231-265) — maps the audit COUNTS → verdict (`SKILLS-DRIFTED`/`SKILLS-INDEX-STALE`/`EXPECTED-DIVERGENCE`/`SKILLS-CURRENT`). Reads `gemini_unexpected`/`index_dangling`/`audited_at`/`canonical_count` — **does NOT read family names**, so the additive names field this plan introduces is matrix-neutral.
- Found: `scripts/curation/curate-session-memory.sh` (lines 30-37) — already runs `audit_skill_currency.py` (soft-fail) every 6h before rebuilding the equality column. The detector wires in **immediately after** this block so it consumes freshly-written audit state.
- Found: `scripts/readiness/collect-equality.sh` (lines 164-182, 381-389) — reads the audit JSON's COUNTS into the equality YAML; ignores any extra fields, so adding `gemini_unexpected_families` to the audit output does not disturb it.

### Standards
Not applicable — harness/infrastructure issue, no engineering standard.

### LLM Wiki pages consulted
No relevant wiki pages — this is internal harness tooling, not domain knowledge.

### Documents consulted
- Issue #3250 body — "Detector that compares each provider's skill dirs against canonical and emits a drift report (reuse equivalence_state ref pattern for cross-machine). Alert via scripts/notify.sh on drift. Feeds the matrix line item. Closes gap #2."
- Sibling #3249 (MERGED) — established the audit + matrix verdict; this child layers detection/alerting on top, reusing #3249's FACTS.
- Existing test `tests/readiness/test_skill_currency.py` — unit-tests `skill_currency_verdict` in isolation; pattern (load module via `importlib.util.spec_from_file_location`, `_rep(**sc)` fixture builder) is reused for the detector's pure-core tests.

### Gaps identified
- No standalone drift **detector** exists — the audit writes facts and the matrix renders them, but nothing emits a dedicated drift report or fires an alert when drift appears.
- No alert path on skill drift — `notify.sh` is wired for venue-absence/cron jobs but never for skill drift.
- No spam-suppression / last-seen state — re-running the audit every 6h would re-alert on the *same* standing drift forever without a dedup mechanism.
- The audit emits unexpected-family **counts** but not **names**, so a report can't enumerate what drifted.
- No cross-machine drift visibility — the equivalence-state ref pattern exists but no `skill-drift-state` ref is published.

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-26 via `gh issue view`):
- `#3250` — OPEN — "Self-improvement: cross-provider skill-drift detector + alert — epic #3248"; labels `cat:skills-improvement`, `domain:ai-orchestration`.

**File existence** (`ls -la` 2026-06-26):
- EXISTS: `scripts/curation/audit_skill_currency.py`
- EXISTS: `scripts/operations/venue_absence_detector.py`
- EXISTS: `scripts/notify.sh`
- EXISTS: `scripts/monitoring/equivalence_state.py`
- EXISTS: `scripts/curation/curate_session_memory.py` (publish_fingerprint timeout precedent)
- EXISTS: `tests/readiness/test_skill_currency.py`
- MISSING (new — this plan creates): `scripts/curation/detect_skill_drift.py`
- MISSING (new — this plan creates): `tests/curation/test_detect_skill_drift.py`

**Line excerpts** (`audit_skill_currency.py` return dict — what facts already exist):
```
142:    return {
143:        "machine": machine,
144:        "audited_at": _now(),
145:        "canonical_count": (len(canonical) if canonical is not None else None),
146:        "gemini_present": gemini_present,
147:        "gemini_unexpected": gemini_unexpected,
148:        "gemini_expected": gemini_expected,
...
151:        "index_dangling": (dangling if dangling is not None else None),
153:        "schema_version": 1,
```

**Line excerpts** (`venue_absence_detector.py` — injectable-notify pattern to mirror):
```
197: def run_cli(args, notify_fn: Callable[[dict], None] = _default_notify) -> int:
207:     alerts = evaluate(**inputs)
208:     for alert in alerts:
209:         notify_fn(alert)
```

**Gap proofs**:
- `ls scripts/curation/detect_skill_drift.py 2>&1` → "No such file or directory" → confirms detector does not exist.
- `grep -rln "skill-drift\|skill_drift" scripts/ 2>/dev/null` → empty → confirms no drift-alert path today.
- The audit `audit()` dict (lines 142-154) has no `*_families` key → confirms names are not emitted.

**Reproduction proofs:** N/A — this is a net-new feature (no alleged runtime failure to reproduce). The audit it builds on is verified live: `python3 scripts/curation/audit_skill_currency.py --stdout` emits the facts dict the detector will consume.

<!-- Source count: issue body + audit_skill_currency.py + venue_absence_detector.py + notify.sh + equivalence_state.py + curate_session_memory.py + build-equality-matrix.py + test_skill_currency.py = 8 sources -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | docs/plans/2026-06-26-3250-skill-drift-detector-alert.md |
| Implementation | `scripts/curation/detect_skill_drift.py` |
| Tests | `tests/curation/test_detect_skill_drift.py` |
| Audit names-field tests | `tests/readiness/test_skill_currency.py` (extend) |
| Modify (additive) | `scripts/curation/audit_skill_currency.py` |
| Cron wiring | `scripts/curation/curate-session-memory.sh` |
| Plan review — Claude | scripts/review/results/2026-06-26-plan-3250-claude.md |
| Plan review — Codex | scripts/review/results/2026-06-26-plan-3250-codex.md |

---

## Deliverable

A standalone `scripts/curation/detect_skill_drift.py` that reads the existing `audit_skill_currency.py` state, writes a drift report, and fires a `scripts/notify.sh` alert **only when NEW (not previously-seen) unexpected cross-provider skill drift appears** — with optional bounded publishing of the drift fingerprint to a dedicated `skill-drift-state` git ref for cross-machine visibility. The audit gains a small additive `gemini_unexpected_families` field so the report can name *which* families drifted; no family-diff logic is duplicated.

The drift-alert path is scoped to **cross-provider family drift only**. Index-staleness is **excluded by default** (`drift_signature`/`evaluate_drift` accept `include_index=False`): the `.claude/skills-index.yaml` is already known-rotted (202/224 dangling at plan time) and no generator currently regenerates it, so letting index-dangling into the family-drift signature would make the detector **false-fire on its very first run** against pre-existing rot. Index staleness stays surfaced by the matrix `SKILLS-INDEX-STALE` verdict (which #3249 already renders) and is only foldable into the drift signal behind an explicit `--include-index` opt-in. The detector derives its machine label by **reusing `audit_skill_currency.machine_label()`** — the exact function that wrote the state file it reads — so the report/last-seen/publish filenames can never key off a different label than the audit's `skill-currency-<machine>.json`.

---

## Design decisions (resolve the two questions in the issue scope)

1. **Separate script, not an extension of the audit.** The audit stays a pure *fact emitter* (single responsibility, already consumed by the matrix + collect-equality). The detector is a separate *decide/alert/persist* layer that READS the audit's state file. This mirrors the `audit → matrix` split already in place and the `evaluate` pure-core + thin-CLI split in `venue_absence_detector.py`. The only change to the audit is **additive**: emit the names of the unexpected families (the diff already computes them internally — we expose, not recompute), bumping `schema_version` 1→2.

2. **Spam suppression via last-seen drift signature.** The detector computes a stable **drift signature** from the current facts (sorted unexpected family names + an `UNREADABLE` sentinel when the audit couldn't read the tree). Index-dangling is **NOT in the default signature** — `drift_signature(facts, *, include_index=False)` only folds the dangling count when `include_index=True` (the `--include-index` opt-in), so the standing index rot (202/224 dangling) can never trip the family-drift alert on the first run. The signature is compared against a persisted `.claude/state/skill-drift-last-seen-<machine>.json`. An alert fires **only on a signature transition into/within drift** (new drift, or the drift *set changed*), never on an unchanged standing drift. A transition from drift → clean emits a single `pass` "recovery" event. This is the same one-shot-on-change posture as correction/absence detectors and avoids re-alerting every 6h on the same standing divergence.

3. **Machine label is borrowed from the audit, not reinvented.** The detector reads `skill-currency-<machine>.json` and writes `skill-drift-report-<machine>.json` / `skill-drift-last-seen-<machine>.json` keyed on the same `<machine>`. To guarantee they agree, the detector `import`s and calls `audit_skill_currency.machine_label()` (the function that produced the audit's filename) rather than reimplementing the host→label table or borrowing `curate_session_memory.machine_label()`'s independent copy. A single source of truth for the label removes the class of bug where the detector reads one box's facts but writes/publishes under a different label.

---

## Pseudocode

```
# ── audit_skill_currency.py (additive) ──────────────────────────────────
# inside audit(): the diff already builds the unexpected set; capture its names.
# CRITICAL: init unexpected_families BEFORE the canonical/gemini guard (mirrors the existing
# `gemini_unexpected = gemini_expected = 0` init on line 129) so the gemini-ABSENT path — where
# the `if canonical is not None and gemini is not None and gemini_present:` body never runs —
# does not hit a NameError when the return dict references the name.
gemini_unexpected = gemini_expected = 0
unexpected_families = []                            # NEW: init before the guard (no NameError when gemini absent)
if canonical is not None and gemini is not None and gemini_present:
    diff = canonical ^ gemini
    expected = {f for f in diff if _allowed(f)}
    gemini_expected = len(expected)
    unexpected_families = sorted(diff - expected)  # NEW: names, assigned INSIDE the guard
    gemini_unexpected = len(unexpected_families)
...
return {... existing facts ...,
        "gemini_unexpected": gemini_unexpected,               # unchanged count
        "gemini_unexpected_families": unexpected_families,    # NEW: [] on gemini-absent / no-drift
        "schema_version": 2}                                  # bumped 1→2


# ── detect_skill_drift.py ───────────────────────────────────────────────
from audit_skill_currency import machine_label   # REUSE the fn that wrote skill-currency-<machine>.json
PUBLISH_TIMEOUT_S = 90
DRIFT_REF = "skill-drift-state"

def drift_signature(facts, *, include_index=False) -> str:   # PURE; index OFF by default
    if facts unreadable (canonical_count not a positive int): return "UNREADABLE"
    parts = []
    fams = sorted(facts.get("gemini_unexpected_families") or [])
    if facts.gemini_present and fams: parts.append("fam:" + ",".join(fams))
    if include_index:                            # opt-in ONLY (--include-index); default path ignores rot
        dang = facts.get("index_dangling")
        if isinstance(dang, int) and not isinstance(dang, bool) and dang > 0:
            parts.append(f"idx:{dang}")
    return "CLEAN" if not parts else "|".join(parts)

def evaluate_drift(facts, last_seen, *, now_iso, include_index=False) -> dict:   # PURE — no IO/clock
    validate facts is a dict; sig = drift_signature(facts, include_index=include_index)
    drift_present = sig not in ("CLEAN",)            # UNREADABLE counts as a (fail-closed) alertable state
    last_sig = (last_seen or {}).get("signature")
    alerts = []
    new_drift  = drift_present and sig != last_sig
    recovered  = (not drift_present) and last_sig not in (None, "CLEAN")
    if new_drift:
        kind = "audit-unreadable" if sig == "UNREADABLE" else "skill-drift"
        alerts.append({kind, detail=human_summary(facts, sig),
                       severity="critical", status="fail"})
    if recovered:
        alerts.append({kind="skill-drift-cleared", detail=..., severity="info", status="pass"})
    new_state = {"signature": sig, "drift_present": drift_present, "updated_at": now_iso,
                 "first_seen": (last_seen.first_seen if sig == last_sig else now_iso)}
    return {"signature": sig, "drift_present": drift_present,
            "new_drift": new_drift, "recovered": recovered,
            "alerts": alerts, "report": {facts + sig + remediation}, "new_state": new_state}

def run_cli(args, notify_fn=_default_notify) -> int:
    machine = machine_label()                                  # REUSED from audit_skill_currency, not reimplemented
    facts = read_json(STATE / f"skill-currency-{machine}.json")   # audit output; MISSING → unreadable facts
    last  = read_json(STATE / f"skill-drift-last-seen-{machine}.json") or None
    result = evaluate_drift(facts, last, now_iso=_now(), include_index=args.include_index)
    write_json(STATE / f"skill-drift-report-{machine}.json", result["report"])   # (a) ALWAYS written
    for a in result["alerts"]: notify_fn(a)                                       # (b) gated by dedup
    write_json(STATE / f"skill-drift-last-seen-{machine}.json", result["new_state"])
    if args.publish: print(publish_drift(machine), file=sys.stderr)               # (c) bounded, fail-soft
    return 1 if result["new_drift"] else 0

def _default_notify(alert):                  # mirrors venue_absence _default_notify
    subprocess.run(["bash", notify_sh, "cron", "skill-drift",
                    alert["status"], f'{alert["kind"]}: {alert["detail"]}'], check=False)

def publish_drift(machine) -> str:           # mirrors publish_fingerprint exactly
    try: subprocess.run([py, equivalence_state.py, "publish", "--repo", REPO,
                         "--role", machine, "--file", report_file, "--ref", DRIFT_REF],
                        timeout=PUBLISH_TIMEOUT_S)
    except TimeoutExpired: return f"publish-timeout ({PUBLISH_TIMEOUT_S}s)"
    ...
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `scripts/curation/detect_skill_drift.py` | pure `evaluate_drift`/`drift_signature` core (`include_index=False` default) + thin CLI (imports `audit_skill_currency.machine_label`) + bounded publish |
| Create | `tests/curation/test_detect_skill_drift.py` | TDD suite for the detector |
| Modify | `scripts/curation/audit_skill_currency.py` | additively emit `gemini_unexpected_families`; bump `schema_version` 1→2 |
| Modify | `tests/readiness/test_skill_currency.py` | assert the new names field; assert matrix verdict unchanged by it |
| Modify | `scripts/curation/curate-session-memory.sh` | run the detector (soft-fail) right after the audit block |
| Update | docs/plans/README.md | index this plan |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_signature_clean | no drift → CLEAN | facts: unexpected=[], dangling=0, gemini_present | `drift_signature == "CLEAN"` |
| test_signature_names_sorted | signature is name-stable & order-independent | families `["b","a"]` vs `["a","b"]` | identical signature `"fam:a,b"` |
| test_signature_index_excluded_by_default | index rot does NOT enter the default signature | dangling=200, no fam drift, `include_index` unset | `drift_signature == "CLEAN"` (no `idx:` token) |
| test_signature_includes_index_optin | dangling enters only with the opt-in | dangling=3, `include_index=True` | signature contains `"idx:3"` |
| test_first_run_no_falsefire_on_index_rot | first run against standing index rot stays quiet | dangling=200, no fam drift, last_seen=None, default | `new_drift=False`, 0 alerts, rc 0 |
| test_signature_unreadable | canonical_count 0/None → UNREADABLE | canonical_count=0 | `"UNREADABLE"` |
| test_new_drift_alerts_once | first appearance fires one fail alert | facts drift, last_seen=None | `new_drift=True`, 1 alert status=fail |
| test_same_drift_suppressed | unchanged standing drift → no alert | facts drift, last_seen.signature==sig | `new_drift=False`, 0 alerts |
| test_changed_drift_realerts | drift SET changed → re-alert | last sig `fam:a`, now `fam:a,b` | `new_drift=True`, 1 alert |
| test_recovery_emits_pass | drift → clean transition | facts CLEAN, last_seen drift | `recovered=True`, 1 alert status=pass |
| test_clean_stays_quiet | clean and was clean → silent | facts CLEAN, last_seen CLEAN | 0 alerts, rc 0 |
| test_unreadable_alerts_failclosed | unreadable facts alert once, not green | canonical_count=None, last clean | 1 alert kind=audit-unreadable |
| test_gemini_absent_no_drift | stale count ignored when gemini absent | gemini_present=False, unexpected_families=["x"] | signature CLEAN, 0 alerts |
| test_run_cli_injected_notify | CLI fires injected notify_fn per alert, writes report+last-seen | tmp STATE with drift facts | notify called once; both state files written; rc 1 |
| test_run_cli_uses_audit_machine_label | CLI keys state files on `audit_skill_currency.machine_label()` | monkeypatch `audit_skill_currency.machine_label`→`"BOXLBL"`, tmp STATE | reads `skill-currency-BOXLBL.json`, writes `skill-drift-report-BOXLBL.json` |
| test_report_always_written | report file written even when no alert | clean facts | `skill-drift-report-*.json` exists; 0 notify calls |
| test_publish_bounded_timeout | publish wraps a timeout, fail-soft string | monkeypatch subprocess→TimeoutExpired | returns `publish-timeout (90s)`, no raise |
| test_evaluate_pure_no_io | evaluate_drift performs no file/subprocess IO | any facts | (assert via monkeypatched open/subprocess unused) |
| test_audit_emits_unexpected_families | audit output carries names list | (in test_skill_currency.py, fixture tree with drift) | `gemini_unexpected_families` is a sorted list matching `gemini_unexpected` count |
| test_audit_gemini_absent_no_nameerror | gemini-ABSENT path returns cleanly, no NameError | (in test_skill_currency.py) fixture tree with NO `.agents/skills` families (`gemini_present=False`) | `audit()` returns dict; `gemini_unexpected_families == []`, `gemini_unexpected == 0` (proves init-before-guard) |
| test_matrix_verdict_ignores_names | adding names field doesn't change verdict | `_rep(gemini_unexpected_families=["x"], gemini_unexpected=1)` | `SKILLS-DRIFTED` (unchanged) |

---

## Acceptance Criteria

- [ ] New tests pass: `uv run --no-project --with pyyaml pytest tests/curation/test_detect_skill_drift.py -v`
- [ ] Audit/matrix tests still pass: `uv run --no-project --with pyyaml pytest tests/readiness/test_skill_currency.py -v`
- [ ] `evaluate_drift` is PURE (no file/subprocess/clock IO; `now_iso` injected) — proven by a test that monkeypatches `open`/`subprocess` to raise.
- [ ] `drift_signature`/`evaluate_drift` accept `include_index=False` by default; index-dangling enters the signature **only** under `--include-index`. A first run against the standing index rot (no family drift, `last_seen=None`) fires **zero** alerts — no false-fire on the pre-rotted index (202/224 dangling).
- [ ] The detector derives `<machine>` by calling `audit_skill_currency.machine_label()` (imported, not reimplemented and not borrowed from `curate_session_memory`); a monkeypatch of that function redirects every state filename the detector reads/writes.
- [ ] The audit's gemini-ABSENT path returns without `NameError` and emits `gemini_unexpected_families == []` (init-before-guard verified by `test_audit_gemini_absent_no_nameerror`).
- [ ] Running the detector twice on the same standing drift fires exactly **one** `notify.sh` event (spam suppression verified).
- [ ] Drift report `.claude/state/skill-drift-report-<machine>.json` is written on **every** run regardless of alert.
- [ ] `notify.sh` event uses `source=cron`, `job=skill-drift`, `status=fail` on new drift / `pass` on recovery.
- [ ] Publish path is bounded by a 90s `subprocess` timeout and returns a fail-soft string (never raises, never blocks the cron) — mirrors `publish_fingerprint`.
- [ ] `scripts/legal/legal-sanity-scan.sh` passes; `scripts/enforcement/check-no-abs-paths.sh` passes (all paths via `Path(__file__).resolve().parents[...]`); no client identifiers.
- [ ] `curate-session-memory.sh` invokes the detector soft-fail after the audit (a detector failure never blocks curation).
- [ ] Review artifacts posted to scripts/review/results/ (T2 → 2 providers).

---

## Adversarial Review Summary

<!-- Filled after Step 4. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | — | — |
| Codex | — | — |

**Overall result:** —

---

## Risks and Open Questions

- **Risk — cross-machine publish hangs.** Context note confirms pushes to these state-refs currently HANG in non-interactive context. Mitigation: publish is OFF by default (`--publish` flag), bounded by a 90s subprocess timeout, fail-soft (precedent: `publish_fingerprint`). Cron may enable it; a hang degrades to a `publish-timeout` string, never stalls curation.
- **Risk — schema_version bump breaks a consumer.** `skill_currency_verdict` and `collect-equality.sh` read named fact keys, not `schema_version`, and ignore unknown keys; `test_matrix_verdict_ignores_names` guards this. The only `schema_version`-asserting test is `tests/skills/test_weekly_skills_audit_v2.py` against a *different* script, so unaffected.
- **Risk — first-run false-fire on the pre-rotted index (RESOLVED).** `.claude/skills-index.yaml` is known-rotted (202/224 dangling) and no generator currently regenerates it. If index-dangling entered the default signature, the detector's *very first* run would see a non-CLEAN signature with `last_seen=None`, compute `new_drift=True`, and fire a critical alert on standing rot that has nothing to do with cross-provider drift. **Decision (not just a recommendation):** `drift_signature`/`evaluate_drift` take `include_index=False` by default — index-dangling is folded into the signature **only** under the explicit `--include-index` opt-in. The detector's primary, high-signal alert is cross-provider family drift; index staleness remains surfaced by the matrix `SKILLS-INDEX-STALE` verdict (#3249). Guarded by `test_signature_index_excluded_by_default` + `test_first_run_no_falsefire_on_index_rot`. When `--include-index` is on, a changing dangling count (5→6) still changes the signature and re-alerts — accepted as opt-in behavior, not the default path.
- **Risk — detector reads one box's facts, writes under another label.** If the detector reimplemented its own host→label table (or borrowed `curate_session_memory.machine_label()`), label drift between the two functions would make it read `skill-currency-<A>.json` but write `skill-drift-report-<B>.json`. Mitigation: the detector imports and calls `audit_skill_currency.machine_label()` — the single source of truth that produced the audit filename — guarded by `test_run_cli_uses_audit_machine_label`.
- **Risk — audit additive raises NameError on the gemini-absent path.** `gemini_unexpected_families` is referenced unconditionally in the return dict, but the diff that populates it lives inside the `if canonical … and gemini_present:` guard. On any box where Gemini's `.agents/skills` is absent (guard false), an assign-only-inside-the-guard would `NameError`. Mitigation: initialize `unexpected_families = []` BEFORE the guard (mirrors the existing `gemini_unexpected = gemini_expected = 0` init) and assign the sorted names inside it; guarded by `test_audit_gemini_absent_no_nameerror`.
- **Risk — audit not yet run.** If `skill-currency-<machine>.json` is missing, the detector treats facts as UNREADABLE (fail-closed, alerts once). Cron ordering (detector after audit) makes this rare; the soft-fail wiring tolerates it.
- **Open:** re-alert cooldown — should an unchanged standing drift re-alert after N days as a reminder? Deferred; signature-only suppression ships first, a `--realert-after-h` cooldown is a clean follow-on.

---

## Complexity: T2

**T2** — new module + test file, one additive modification to an existing script (audit), one cron-script wiring change, and reuse of the equivalence-state ref. Multi-file but not cross-provider-systemic. Adversarial review at T2 scale = 2 providers (Claude + Codex).
