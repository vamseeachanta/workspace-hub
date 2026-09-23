# Verification log — plan #3709 v3 (author, NOT a review)

Raw evidence behind every RED/GREEN claim in
`docs/plans/2026-07-30-issue-3709-managed-block-classification-v3.md`. This is **not** an adversarial
review; an independent r2 review is still required.

- Host: `ace-linux-1` (`dev-primary`), repo `/mnt/local-analysis/workspace-hub`, HEAD **`3fe934da9`**
  = `origin/main`, git 2.43.0. Mac checkout `/Users/krishna/Developer/ws/workspace-hub` also at
  `3fe934da9`. (v2 measured against ace1 at `5690613c4`; ace1 has since fast-forwarded, so v3 and the
  Mac are on the identical commit and no cross-host hash comparison is needed.)
- Scope: read-only. `crontab -l` on ace1 and ace2 only; no `crontab` write, no `setup-cron.sh`, no
  `cron_apply.py --apply`, no `daily-cleanup.sh`, no `reconcile-ecosystem.sh --apply`. Probe scripts
  ran from `/tmp/v3probe` and were never written into the repo.
- v3 answers `scripts/review/results/2026-07-30-plan-3709-v2-codex-r2.md` (verdict MAJOR, 2 findings).

---

## 0. Baseline gates on today's `main` — all GREEN

```
$ [ace1] git rev-parse --short HEAD                                            3fe934da9
$ [ace1] uv run python scripts/enforcement/check-scheduler-mutation-surfaces.py
CHECKER_EXIT=0
$ [ace1] ... --check-html docs/reports/2026-07-11-issue-3470-scheduler-mutation-safety.html
HTML_EXIT=0
$ [ace1] uv run --with pyyaml python scripts/cron/build-cron-identity-inventory.py --check
INVENTORY_CHECK_EXIT=0
```

Module sizes (re-measured):

```
scheduler_mutation_attestations.py  317      scheduler_mutation_contract.py     400  (ceiling)
scheduler_mutation_delegation.py    123      scheduler_mutation_discovery.py     93
scheduler_mutation_python_flow.py   180      scheduler_mutation_report.py        91
scheduler_mutation_wrapper_attestations.py 196
cron_transaction.py 257   cron-audit.py 379   cron_identity.py 256   cron_line_model.py 177
```

---

## 1. FIX 1 — the attestation

### 1.1 r2's finding reproduced

v2's published predicate spec (plan lines 432-458) implemented literally, run against v2's own honest
shape and against r2's counter-example:

```
v2 spec on HONEST implementation  : {'order': True, 'all_locations': True, 'retention': True, 'shape': True}
v2 spec on COUNTEREXAMPLE         : {'order': True, 'all_locations': True, 'retention': True, 'shape': True}
```

Identical to the probe output r2 reported. The finding stands.

### 1.2 First v3 candidate (hand-rolled dead-branch elimination)

```
HONEST       : {'plan_cutover_order': True, 'plan_cutover_result_flow': True,
                'render_block_called_once': True, 'classify_populates_records': True,
                'fallback_records_populated': True, 'rebuild_retention': True,
                'intent_derives_blocking': True}                      => shape True
COUNTEREXAMPLE: {'plan_cutover_order': True, 'plan_cutover_result_flow': False,
                'render_block_called_once': True, 'classify_populates_records': False,
                'fallback_records_populated': False, 'rebuild_retention': False,
                'intent_derives_blocking': False}                     => shape False
```

Discarded in favour of 1.3: it reimplemented reachability that the repo already has.

### 1.3 Final v3 candidate — built on `scheduler_mutation_python_flow._walk_block`

First run **failed on the honest baseline** (`v3 accepts baseline: False`). Diagnosis:

```
--- plan_cutover: 5 live paths ---   (the trailing-newline `if` splits the success path)
```

`_terminal_returns` was counting the same `Return` node once per path, so `len(results) != 1`
rejected a correct implementation. Fixed by deduplicating terminal returns by node identity and
asserting "every live path ends in a Return" as a separate predicate. This false negative is recorded
because it is the kind of defect that would otherwise surface only after the implementer wrote
correct code and could not get it past the gate.

Final result:

```
mutation                                                 v2     v3
------------------------------------------------------------------
(baseline honest implementation)                       True   True
------------------------------------------------------------------
M1  all-locations loop drops 'managed'                False  False
M2  delete uncataloged abort guard                    False  False
M3  hoist render_block above classification           False  False
M3b decoy render_block hoisted (v2's admitted hole)    True  False
M4  before-retention emptied                          False  False
M5  after section dropped from composition            False  False
M6  delete intent-blocking guard                      False  False
M7  delete parse-error guard                          False  False
M8  dead all-locations loop, records=[] (reviewer)     True  False
M9  dead retention return, live `return block` (rev.)  True  False
M10 vacuous intent builder (reviewer)                  True  False
M11 parse-error fallback returns no records            True  False
M12 success return emits only the managed block        True  False
M13 record append made conditional (skips lines)       True  False
M14 rebuild called with no records                    False  False
MX  full reviewer counter-example                      True  False
------------------------------------------------------------------
v3 accepts baseline: True
v3 mutations NOT rejected: none — all rejected
v2 mutations NOT rejected: M3b, M8, M9, M10, M11, M12, M13, MX   (8 of 16)
```

### 1.4 The v3 set is RED on today's source, and the refactor breaks today's attestation

```
v3 predicate set on TODAY's cron_transaction.py : False
  per-predicate: {'plan-cutover-order': False, 'plan-cutover-result-flow': False,
                  'render-block-called-once': True, 'classify-populates-records': False,
                  'fallback-records-populated': False, 'rebuild-retention': False,
                  'intent-derives-blocking': False}
SHIPPED _preservation_shape on TODAY's source   : True
SHIPPED _preservation_shape on the NEW shape    : False
```

Both directions measured, so commit 4 must fuse the transaction refactor with the attestation.

### 1.5 Residue the attestation cannot cover — measured, not asserted

Three semantically wrong implementations the v3 predicate set still accepts:

```
R1 (classifier declares every line cataloged) : v3 attestation = True
R2 (_abort returns abort_reason=None)         : v3 attestation = True
R3 (parse_crontab mis-partitions all lines)   : v3 attestation = True
```

R1 deletes every live line with all seven predicates green. This is why the plan declines to claim
the attestation carries `scheduler-mutation-safety.md`'s fail-closed clause alone.

### 1.6 Module placement constraints

```
candidate module lines            : 293      (ceiling 400)
functions over 50 lines           : none     (largest 26)
attestations.py today             : 317      -> ~302 after removing _preservation_shape (17)
folding 293 into attestations.py  : ~593     -> BREAKS the ceiling; new module required
```

Size test (`tests/enforcement/test_scheduler_mutation_task3.py:274-288`) globs
`scripts/enforcement/scheduler_mutation*.py`, so a new sibling is covered automatically; its
`required` set is only `{report.py, delegation.py}` and is unaffected by an addition.

Surface-discovery scan (`PRIMITIVE_PATTERNS` per non-comment line, plus alias and known-call checks):

```
v3 predicate module (candidate)    : direct_primitives=[]  alias=False  known_call=None
existing attestations.py (control) : direct_primitives=['windows-task-set',
                                     'windows-task-unregister-register']  (7 matching lines)
PRIMITIVE_PATTERNS keys: ['crontab-replace','systemd-user-enable-disable',
                          'systemd-user-unit-write','windows-task-set',
                          'windows-task-unregister-register']
FORENSIC = {CHECKER, TEST, HARDENING_TEST, ATTESTATIONS, DISCOVERY_HELPER, WRAPPER_ATTESTATIONS}
sentinel comments on attestations.py:229-236 : 7
```

The control confirms the mechanism: `attestations.py` matches two primitives and is exempt only
through `FORENSIC` membership plus `# scheduler-mutation-forensic` sentinels. The candidate matches
none, so no `FORENSIC` and no `mutation-surfaces.yaml` change is needed.

---

## 2. FIX 2 — the inventory host dependency

Root cause is `cron_render.workspace_hub_path` (`cron_render.py:87`,
`Path(override).expanduser().resolve()`), fed each Linux machine's declared `workspace_root` by
`build-cron-identity-inventory.py:96-100`.

```
[ace1] ace-win-1        os=windows  declared=D:\workspace-hub                        faithful=False
[ace1] ace-win-2        os=windows  declared=D:\workspace-hub                        faithful=False
[ace1] dev-primary      os=linux    declared=/mnt/local-analysis/workspace-hub       faithful=True
[ace1] dev-secondary    os=linux    declared=/mnt/local-analysis/workspace-hub       faithful=True
[ace1] gali-linux-compute-1 linux   NO_ROOT
[ace1] gpu-claw         os=linux    declared=/home/undi/ws/workspace-hub             faithful=True
[ace1] macbook-portable os=macos    declared=/Users/krishna/Developer/ws/workspace-hub faithful=True

[mac]  gpu-claw         os=linux    declared=/home/undi/ws/workspace-hub
                                    resolved=/System/Volumes/Data/home/undi/ws/workspace-hub
                                    faithful=False
[mac]  dev-primary / dev-secondary / macbook-portable                                 faithful=True
```

`build()` iterates only `os == "linux"` machines, so the Windows rows are irrelevant and `gpu-claw`
is the single poisoned row on macOS — exactly #3711's reported near-miss. The one-comparison guard
predicate is therefore validated, which is what makes #3711 cheap enough to sequence first.

Checker-side confirmation of the silent-failure claim: `_validate_inventory_digest`
(`scheduler_mutation_delegation.py:112-123`) hashes only the eight configured source files and
compares `inventory["input_digest"]`; it never compares `inventory["identities"]` against a fresh
generator run. `_validate_inventory_bytes` (`:104-110`) only checks canonical JSON formatting.

---

## 3. FIX 3 — the crontab fixtures

### 3.1 No fixture exists on `main`

```
$ [ace1] ls tests/cron/fixtures            ls: cannot access 'tests/cron/fixtures': No such file or directory
$ [ace1] git ls-files | grep -i crontab
config/agents/claude/memory-snapshots/crossprovider_codex_cron-yaml-source-drifts-from-installed-crontab-a_98da4b8b.md
config/agents/claude/memory-snapshots/crossprovider_codex_source-schedule-and-installed-crontab-drift-auto_6d6e3904.md
config/agents/claude/memory-snapshots/crossprovider_hermes_crontab-path-setup-critical-for-user-local-tools_ab83b4d6.md
docs/reports/2026-04-15-issue-2292-installed-crontab-probe.md
scripts/coordination/productivity/crontab.example
scripts/cron/crontab-template.sh
```

None is an ace crontab capture.

### 3.2 Capture and deny-scan

```
ace1 exit=0 bytes=15603 lines=73
ace2 exit=0 bytes=6856  lines=40

=== ace1: 73 lines, 15593 bytes ===
  deny-scan total matches: 0
  trailing newline: True
=== ace2: 40 lines, 6850 bytes ===
  HIT literal /home/<user>: 4 -> ['/home/linuxbrew', '/home/vamsee']
  deny-scan total matches: 4
  trailing newline: True
```

Deny-scan patterns: `MAILTO=`, `[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|APIKEY|API_KEY|ACCESS_KEY)=`,
`Bearer <token>`, `ghp_|gho_|ghu_|ghs_|ghr_|github_pat_`, `sk-|sk-ant-`, `AKIA[0-9A-Z]{16}`,
`AIza[…]{35}`, `xox[abprs]-`, PEM private-key header, e-mail address, `/home/<user>`,
`/Users/<user>`, IPv4 literal, `ssh|scp|rsync user@`.

ace2's four hits: `/home/linuxbrew` ×1 (system account, exempt by rule) and `/home/vamsee` ×3
(crontab lines 2, 35, 37).

### 3.3 Redaction and class-preservation

```
ace2 substitutions: 3          (/home/(?!linuxbrew/)[A-Za-z0-9._-]+  ->  $HOME)
residual /home hits: ['/home/linuxbrew']
lines raw/red: 40 40
ace1 identical to raw: True    (zero redactions)
```

```
===== ace1 (dev-primary) =====
  ace1-crontab-2026-07-30.txt: lines=73 parse before=11 managed=51 after=9 err=None roles=control-plane
     by class      : {'cataloged': 11, 'ignore': 12, 'preserved_external': 1, 'uncataloged': 47}
     by (loc,class): {('after','cataloged'): 7, ('after','ignore'): 2, ('before','ignore'): 10,
                      ('before','preserved_external'): 1, ('managed','cataloged'): 4,
                      ('managed','uncataloged'): 47}
===== ace2 (dev-secondary) =====
  ace2-crontab.txt (raw):       lines=40 parse before=14 managed=14 after=10 err=None
                                roles=comms-dispatch+sim-worker
     by class      : {'cataloged': 3, 'ignore': 15, 'preserved_external': 9, 'uncataloged': 11}
     by (loc,class): {('after','ignore'): 5, ('after','preserved_external'): 5,
                      ('before','ignore'): 10, ('before','preserved_external'): 4,
                      ('managed','cataloged'): 3, ('managed','uncataloged'): 11}
  ace2-crontab.sanitised.txt:   identical parse and identical class counts
  SANITISATION CLASS-PRESERVING: True
```

ace1 reproduces v2's M1 exactly. ace2 confirms the breakdown v2's M9 explicitly declined to verify
(40 lines, role `comms-dispatch+sim-worker`, 9 `preserved_external`, 3 of 14 managed cataloged).

The ace1 `ignore` count is 12 here versus `cron-audit`'s 15 in v2's M1: `audit_crontab` iterates
`crontab_text.split("\n")` and counts the two markers and the trailing blank, which have no location.
That is the audit defect D1 removes, not a measurement discrepancy.

### 3.4 Rows 1, 8, 12, 14 re-measured from the fixture, no `crontab -l`

```
=== ROW 1 (fixture-based) ===
  abort_reason: None  uncataloged: 0  new_text lines: 72
  true uncataloged records: 47  all managed: True
=== ROW 12/14 (fixture-based) ===
  absent occurrences: 51  by class: {'uncataloged': 47, 'cataloged': 4}
  added occurrences: 52
  absent cataloged (loc,idx): [('after', 0), ('after', 4), ('after', 7), ('after', 8)]
  duplicate live non-ignore lines:
   x2 at [('managed', 31), ('after', 7)] : 30 4 * * * cd /mnt/local-analysis/workspace-hub && find logs/notifications/ …
   x2 at [('after', 1), ('after', 8)]    : 0 5 * * 0 PATH=$HOME/.local/bin:$PATH; mkdir -p /mnt/local-analysis/… catalog_delta.py …
=== ROW 8 (fixture-based parity: blanket vs third-party-first) ===
  blanket preservation-first  : same=69/71 diffs=2
     cataloged -> preserved_external : 0 5 * * 0 … catalog_delta.py …
     cataloged -> preserved_external : 0 5 * * 0 … catalog_delta.py …
  third-party-first (D2)      : same=71/71 diffs=0
```

r2's three "NOT RERUN" rows (1, 12, 14) and the two parity counts it could not verify (69/71 and
71/71) are all now reproducible offline by any reviewer on any Linux host.

---

## 4. Claims this log does NOT support

- No claim that the attestation makes unsafe reconstruction impossible. §1.5 measures three shapes it
  accepts.
- No claim that #3711's fix is verified. Only its root cause and the cheapness of its guard predicate
  are measured; the fix itself is not written.
- No claim that the enforcement checker validates identity-row **content**. §2 measures the opposite;
  the plan records it as an unclosed follow-on.
- No re-verification of v2's M2/M3/M4/M5/M6 probes. Those were reproduced independently by the Codex
  r2 reviewer (rows 3-7, 9-11, 13) and are carried forward on that basis, not re-run here.
- The fixtures are point-in-time captures taken 2026-07-30 and will drift from live state.
