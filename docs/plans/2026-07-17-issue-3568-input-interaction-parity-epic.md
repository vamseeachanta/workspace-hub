# Plan for [#3568](https://github.com/vamseeachanta/workspace-hub/issues/3568): Cross-Machine Input Interaction Parity

> **Status:** plan-review — user decision required
> **Complexity:** T3
> **Date:** 2026-07-17
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3568
> **Client:** N/A
> **Project:**
> **Lane:** lane:claude
> **Review artifacts:** `scripts/review/results/2026-07-17-plan-3568-claude.md` | `scripts/review/results/2026-07-17-plan-3568-codex.md` | `scripts/review/results/2026-07-17-plan-3568-gemini.md`

---

## Resource Intelligence Summary

### Existing repo code

- `scripts/agents/install-voice-dictation.sh:56-79,142-160` supplies the Linux
  dictation installer and defaults to `<Super><Shift>v`. It checks only whether the
  custom-keybinding list is writable; it has no GNOME minimize-collision journal,
  two-phase migration, uninstall, or guarded rollback.
- `tools/voice-dictation/codex-dictate.sh` supplies the offline/local Linux audio and
  focused-text-injection path. Its private state directory and transient-audio cleanup
  form a privacy boundary that the shortcut child will preserve.
- `scripts/readiness/collect-equality.sh:419-472` emits the current equality dimensions.
  It has no `interaction_ux` evidence family, and its `behavior` dimension remains the
  fixed b1-b5 deterministic harness contract.
- `scripts/readiness/build-equality-matrix.py:392-416,481-521,536-564` supplies value
  extraction, verdict precedence, display rows, and HTML groups. It compares uniform
  values across fresh peers and has no per-machine semantic interaction contract,
  interaction-evidence freshness rule, or remediation link metadata.
- `scripts/readiness/check-ux-consistency.sh` prints four unrelated UX checks and exits
  zero unless `--strict`. It is not structured interaction evidence and does not record
  desktop/session, terminal, Codex version, probe version, or evidence age.
- `config/workstations/registry.yaml:1-4` is the single source of truth for machine
  identity and capability data. It currently lists seven machine identities but defines
  no explicit active/unreachable status semantics:
  `dev-primary`, `dev-secondary`, `ace-win-1`, `ace-win-2`, `gpu-claw`,
  `macbook-portable`, and `gali-linux-compute-1`. It has no predicate-level
  interaction-UX applicability field.
- `scripts/readiness/harness-config.yaml:45-126` is the current equality/readiness
  projection. It lists five active machines, marks `home-win` and `macbook-portable`
  unreachable, and omits `gali-linux-compute-1`. That drift from the authoritative
  registry is a fail-closed gap, not a roster decision this plan may hide. #3567 will
  introduce explicit registry status semantics, add historical deferred member
  `home-win` with unreachable status, reconcile `macbook-portable` against live state, add
  `gali-linux-compute-1` to the projection, and reject any remaining set difference.
- `tests/readiness/test_collect_equality.py`,
  `tests/readiness/test_collect_equality_ps1_schema.py`, and
  `tests/readiness/test_build_equality_matrix.py` are the future #3567 regression
  surfaces. The parent epic will not modify them.

### Standards

| Standard | Status | Source |
|---|---|---|
| Issue lifecycle and owner approval | binding | `AGENTS.md`, `docs/plans/README.md` |
| Control-plane ownership and discovery | applicable | `docs/standards/CONTROL_PLANE_CONTRACT.md` |
| Durable versus transient knowledge | applicable | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` |
| Machine identity/capability authority | binding | `config/workstations/registry.yaml` |
| Equality roster projection | applicable, currently drifted | `scripts/readiness/harness-config.yaml`, `tests/readiness/test_registry_sso_completeness.py` |
| Legal/security scan | binding | `scripts/legal/legal-sanity-scan.sh`, `.legal-deny-list.yaml` |
| Completeness before epic closure | binding through `gate:completeness` | issue labels and completeness workflow |

No engineering calculation standard or calculation citation sidecar applies to this
harness/interaction-governance issue.

### LLM Wiki pages consulted

- `docs/document-intelligence/README.md` identifies the durable architecture and
  intelligence entry points. No domain wiki owns workstation input gestures.
- `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` assigns the
  approved parity contract to durable repository documentation while issue comments,
  HITL observations, and review artifacts remain lifecycle evidence.

### Documents consulted

- [#3568](https://github.com/vamseeachanta/workspace-hub/issues/3568) fixes the semantic
  parity definition, child boundaries, pet-peeve intake contract, privacy requirement,
  and independently gated initial child set.
- Parent [#2887](https://github.com/vamseeachanta/workspace-hub/issues/2887) and closed
  baseline [#2801](https://github.com/vamseeachanta/workspace-hub/issues/2801) establish
  the fleet-equivalence program and measurement substrate. Their historical roster count
  will not override the live registry.
- [#3565](https://github.com/vamseeachanta/workspace-hub/issues/3565) owns the Ubuntu
  `Super+H` migration, collision handling, idempotence, uninstall, rollback, and live
  desktop verification. It will not replace the transcription engine or configure
  Windows speech.
- [#3566](https://github.com/vamseeachanta/workspace-hub/issues/3566) owns the
  keyboard/context-menu paste diagnosis and smallest remediation. Its first gate will
  confirm whether the user's intended chord is literally `Ctrl+Insert` or conventional
  `Shift+Insert` before any remapping. Its body was corrected at
  `2026-07-17T10:54:39Z` to compare input and canonical-draft digests separately, require
  pinned empirical canonicalization, and expose normalization loss.
- [#3567](https://github.com/vamseeachanta/workspace-hub/issues/3567) owns the future
  equality schema, structured evidence ingestion, freshness, matrix grading, HTML
  rendering, and remediation links. It will not mutate desktop, terminal, or dictation
  behavior.
- Plan-approved [#3403](https://github.com/vamseeachanta/workspace-hub/issues/3403) and
  `docs/plans/2026-07-09-issue-3403-voice-dictation-vnc-contract.md` establish the landed
  repo-native Linux dictation baseline. The issue remains open, so #3565 will consume
  the code on `main` rather than infer closure from issue state.
- Upstream Codex issue <https://github.com/openai/codex/issues/17103> documents the
  terminal paste-event versus raw key-event split. Upstream source inspection indicates
  that current Codex normalizes CR/CRLF to LF before composer insertion. #3566 will
  empirically re-verify that behavior against the pinned installed CLI before choosing a
  canonicalization version; the parent contract will not treat an unpinned upstream
  observation as permanent fact.
- The official Codex CLI slash-command catalog contains no stable `/voice` command, and
  upstream `RealtimeConversation` remains under development and disabled by default.
  Neither surface will replace the repo-native dictation baseline in this epic.
- The drive-index query `input interaction UX keyboard shortcut paste dictation machine
  equivalence` ran with caller `plan-resource-intel`. It returned no relevant drive
  documents; hits concerned unrelated legacy engineering keyboard shortcuts. Several
  indexes reported stale-age warnings, so no fleet claim will rely on those results.

### Gaps identified

- No durable, machine-validated contract defines the semantic predicates, bounded
  evidence envelope, lifecycle statuses, privacy exclusions, freshness behavior,
  applicability rules, child ownership, or dependency DAG.
- No predicate-level `capabilities.interaction_ux` rule in the authoritative workstation
  registry distinguishes applicable from intentionally inapplicable interactions.
  Inferring applicability from a hostname or applying one machine-wide headless verdict
  would be unsafe.
- No contract separates semantic shortcut parity from privacy parity. Windows `Win+H`
  uses an OS-managed speech boundary while Linux dictation remains repo-native/local.
- No contract defines canonical post-normalization paste equality, exact-once insertion,
  no-auto-submit behavior, CLIPBOARD-versus-PRIMARY selection, or trailing-newline cases.
- No interaction-evidence freshness policy reconciles evidence timestamps with the
  `scripts/readiness/publish-equality.sh` `generated_at` gate. A refreshed HITL observation must advance
  the generated report and publish while its timestamp remains outside the semantic
  value compared across machines.
- No parent-level test prevents a child from inheriting approval, crossing remediation
  and measurement ownership, leaking real clipboard/transcript content, or claiming
  fleet parity from partial/stale evidence.

### Evidence (embedded verification)

**Issue statuses** (verified `2026-07-17T10:39:29Z` via `gh issue view` and native
sub-issue GraphQL):

| Issue | State | Labels / relationship |
|---|---|---|
| [#2887](https://github.com/vamseeachanta/workspace-hub/issues/2887) | OPEN | native parent program |
| [#3568](https://github.com/vamseeachanta/workspace-hub/issues/3568) | OPEN | `status:needs-plan`, `lane:claude`, `gate:completeness`, epic |
| [#3565](https://github.com/vamseeachanta/workspace-hub/issues/3565) | OPEN | native child, `status:needs-plan`, `machine:multi` |
| [#3566](https://github.com/vamseeachanta/workspace-hub/issues/3566) | OPEN | native child, `status:needs-plan`, `machine:multi` |
| [#3567](https://github.com/vamseeachanta/workspace-hub/issues/3567) | OPEN | native child, `status:needs-plan`, `machine:multi` |
| [#3403](https://github.com/vamseeachanta/workspace-hub/issues/3403) | OPEN | `status:plan-approved`; baseline implementation is present on `main` |

**File existence and roster** (verified against
`origin/main@4225ab3c88dd199e6ce9d7e3c3672a2c790c8109`):

```text
EXISTS scripts/agents/install-voice-dictation.sh
EXISTS tools/voice-dictation/codex-dictate.sh
EXISTS scripts/readiness/{collect-equality.sh,collect-equality.ps1,build-equality-matrix.py}
EXISTS scripts/readiness/check-ux-consistency.sh
EXISTS config/workstations/registry.yaml
EXISTS scripts/readiness/harness-config.yaml (drifted projection)
EXISTS tests/readiness/{test_collect_equality.py,test_collect_equality_ps1_schema.py,test_build_equality_matrix.py}
MISSING docs/architecture/interaction-ux-parity-contract.yaml (planned)
MISSING docs/governance/2026-07-17-input-interaction-parity-decision-manual.html (planned)
MISSING tests/architecture/test_interaction_ux_parity_contract.py (planned)
REGISTRY IDENTITIES dev-primary, dev-secondary, ace-win-1, ace-win-2, gpu-claw,
                    macbook-portable, gali-linux-compute-1 (no status field)
HARNESS ACTIVE dev-primary, dev-secondary, gpu-claw, ace-win-1, ace-win-2
HARNESS UNREACHABLE home-win, macbook-portable; OMITTED gali-linux-compute-1
```

**Relevant source excerpts:**

```text
install-voice-dictation.sh:60  hotkey="${DICTATE_HOTKEY:-<Super><Shift>v}"
collect-equality.sh:438-440   behavior.enums b1-b4; behavior.hashes b5
build-equality-matrix.py:536-540 BASE_DISPLAY_DIMS has no interaction_ux
check-ux-consistency.sh:5     returns 0 always; --strict returns 1 on FAIL
```

**Read-only runtime reproduction** (`2026-07-17T10:39:29Z`):

```text
$ env | rg '^(DISPLAY|WAYLAND_DISPLAY|DBUS_SESSION_BUS_ADDRESS)='
<no output>
$ gsettings get org.gnome.desktop.wm.keybindings minimize
['<Super>h']
$ gsettings get org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/codex-dictate/ binding
'<Super><Shift>v'
$ gnome-terminal --version
GNOME Terminal 3.52.0 using VTE 0.76.0
$ codex --version
codex-cli 0.144.5
```

The distinct current bindings prove that the proposed migration target `<Super>h` is
already owned by GNOME minimize; they do not constitute a current collision. Live
activation, focused insertion, and exact rollback cannot be tested from this headless
shell and will remain explicit #3565 HITL
gates. Paste behavior also remains a #3566 HITL gate because the intended Insert chord
has not been confirmed; no remapping will occur from this parent.

Distinct sources: epic/parent/three children and baseline issue; six repo implementation
and test surfaces; two prior plans; document-intelligence entry points; upstream Codex
issue/source; official Codex command catalog; live roster; drive-index probe (more than
the required three sources).

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-07-17-issue-3568-input-interaction-parity-epic.md` |
| Human decision manual | `docs/governance/2026-07-17-input-interaction-parity-decision-manual.html` |
| Machine-readable parent contract | `docs/architecture/interaction-ux-parity-contract.yaml` |
| Contract tests | `tests/architecture/test_interaction_ux_parity_contract.py` |
| Documentation entry point | `docs/README.md` |
| Plan review — Claude | `scripts/review/results/2026-07-17-plan-3568-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-07-17-plan-3568-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-07-17-plan-3568-gemini.md` |
| Disagreement report | `scripts/review/results/2026-07-17-plan-3568-disagreement.md` |
| Completeness report | `docs/reports/<completion-date>-3568-completeness.html` |

The Markdown plan will remain the lifecycle artifact required by the planning harness.
The HTML manual will be the rich human-facing durable view. Review-round snapshots, if
needed, will use `-<provider>-rN.md` and name the exact reviewed revision.

---

## Deliverable

A machine-validated YAML contract and matching HTML decision manual will define semantic
input parity, evidence/privacy/freshness rules, role applicability, the pet-peeve intake
contract, and an independently approved child DAG for dictation, paste, and matrix
integration.

Parent approval will authorize only the future parent contract, manual, tests, and
coordination updates listed here. It will not authorize implementation of #3565, #3566,
or #3567, desktop mutation, live keypresses, or external speech configuration.

---

## Pseudocode

```text
function validate_parent_contract(contract):
    require contract version and exactly these predicates:
        dictation_activation, clipboard_text_paste,
        focused_text_injection, terminal_input_contract
    require a closed evidence envelope with additional properties forbidden recursively
    require semantic outcomes independent of literal cross-OS chord equality
    require each predicate to name one remediation owner and one measurement owner
    allow only bounded enums, booleans, versions, timestamps, SHA-256 fixture digests,
        and repository issue URLs; reject unknown keys, aliases, and nested free text
    require explicit owner approval on every child; reject inherited approval edges
    require rollback for every child that can mutate desktop or terminal configuration
    require a versioned synthetic fixture and bounded HITL protocol for non-automatable evidence
    return valid contract or a fail-closed list of violations

function grade_interaction_evidence(machine, predicate, registry, evidence, now):
    resolve identity and predicate applicability from
        config/workstations/registry.yaml capabilities.interaction_ux
    never infer applicability from hostname, broad role, or another predicate
    if current reachability is explicitly unavailable: return UNREACHABLE
    if predicate applicability is not_applicable:
        return EXPECTED-DIVERGENCE(reason=declared_role_constraint)
    if evidence is absent, malformed, or expired: return MISSING-EVIDENCE
    project evidence to semantic outcome without observed_at or literal chord
    if outcome violates the platform/role contract: return DIVERGES(remediation_issue)
    semantic_verdict = EQUAL
    attach processing_boundary annotation separately:
        repo_local or os_managed, with privacy_comparison EXPECTED-DIVERGENCE when different
    return semantic_verdict plus annotations

function validate_paste_fixture(evidence):
    require fixture_id, canonicalization_version, CLIPBOARD selection, and two event routes
    require an empirical pinned-CLI observation of CR/CRLF behavior before selecting normalization
    require keyboard and context-menu canonical draft digests to match
    record input digest and canonical-draft digest separately to expose normalization loss
    require insertion_count equals one and auto_submit equals false for both routes
    require Unicode, tab, multiline, and trailing-newline cases
    reject PRIMARY selection and any serialized raw fixture or user clipboard content
    return pass or a remediation-linked failure

function validate_freshness_and_publication(evidence, report):
    require observed_at, probe_version, environment identity, and maximum age policy
    require a refreshed observation to advance report generated_at and pass
        scripts/readiness/publish-equality.sh
    exclude observed_at from the semantic value compared across machines
    fail missing or expired applicable evidence as MISSING-EVIDENCE
    preserve precedence UNREACHABLE -> predicate applicability -> evidence freshness -> outcome
    return reproducible freshness and semantic projections

child dependency graph:
    #3565 evidence-contract output -> #3567 schema/ingestion plan
    #3566 HITL chord decision + evidence-contract output -> #3567 schema/ingestion plan
    #3565 and #3566 have no dependency edge between them
    #3565 live evidence + #3566 live evidence + #3567 published matrix -> #3568 closeout
    every issue retains its own plan-review, user approval, implementation, and code review
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Create | `docs/architecture/interaction-ux-parity-contract.yaml` | machine-readable terminology, predicates, evidence envelope, statuses, privacy/freshness rules, ownership, and child DAG |
| Create | `docs/governance/2026-07-17-input-interaction-parity-decision-manual.html` | rich human-facing explanation, cross-platform gesture table, dependency flow, HITL gates, privacy, and rollback rules |
| Create | `tests/architecture/test_interaction_ux_parity_contract.py` | RED-first validation of the YAML contract and HTML parity using stdlib `html.parser` plus existing PyYAML |
| Update | `docs/README.md` | expose the approved durable architecture and manual |
| Update | `docs/plans/README.md` | add and maintain the plan index row |
| Create at closeout | `docs/reports/<completion-date>-3568-completeness.html` | roll up child lifecycle state and exact live machine coverage for `gate:completeness` |

The parent implementation will not modify dictation scripts, GNOME settings, terminal
configuration, Codex source, equality collectors/renderers, machine evidence files, or
any child plan. Those surfaces will remain owned by separately approved child issues.

Future child-owned surfaces are contractual dependencies, not parent-authorized changes:

| Owner | Future surface | Required obligation |
|---|---|---|
| #3565 | dictation installer/tests/docs | emit the versioned `dictation_activation` and `focused_text_injection` fixture contract; migrate and roll back Linux bindings only after its own approval |
| #3566 | terminal/Codex reproduction and smallest remediation | resolve the Insert chord through HITL; emit the versioned `clipboard_text_paste` and `terminal_input_contract` fixture contract |
| #3567 | `config/workstations/registry.yaml`, `scripts/readiness/harness-config.yaml`, equality collectors/renderers/tests | add predicate-level `capabilities.interaction_ux` to the authoritative registry, reconcile the equality projection, ingest/grade evidence, and preserve b1-b5 |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_contract_has_required_predicates_and_terms` | `dictation_activation`, `clipboard_text_paste`, `focused_text_injection`, and `terminal_input_contract` plus canonical terms are complete | contract YAML | exact required set, no ambiguous aliases |
| `test_semantic_parity_does_not_require_literal_chord_identity` | Windows `Win+H` and Linux `Super+H` can share an outcome while privacy metadata differs | platform contracts | semantic parity plus declared expected divergence |
| `test_paste_contract_uses_canonical_composer_text` | empirically pinned CR/CRLF handling, separate input/draft digests, exact-once, no-submit, Unicode/tab/multiline/trailing-newline cases | paste fixture rules | deterministic canonical equality policy with visible normalization loss |
| `test_ctrl_insert_decision_remains_hitl_gated` | no parent or child default silently treats `Ctrl+Insert` as paste | decision table | explicit unresolved HITL gate before remap |
| `test_roster_semantics_are_explicit_and_fail_closed` | active GUI, active headless, missing GUI evidence, and unreachable roles grade distinctly | roster/evidence cases | EQUAL/DIVERGES, EXPECTED-DIVERGENCE, MISSING-EVIDENCE, UNREACHABLE as applicable |
| `test_applicability_is_not_inferred_from_hostname` | machine role comes from an explicit authority | invalid hostname-only case | validation failure |
| `test_predicate_applicability_is_independent` | one inapplicable GUI predicate cannot suppress applicable terminal predicates on the same machine | mixed-applicability fixture | per-predicate verdicts, no machine-wide shortcut |
| `test_freshness_refreshes_report_without_changing_semantic_value` | observation time advances `generated_at` publication but is excluded from semantic comparison | two timestamped equivalent records | newer report publishes, equal semantic projection |
| `test_evidence_schema_is_closed_recursively` | unknown keys, aliases such as `payload_text`, nested free text, raw clipboard/transcript/audio, screenshots, raw commands, secrets, client identifiers, private POSIX/Windows paths, and wrong types cannot enter evidence | one adversarial fixture per forbidden category plus nested/aliased variants | validation failure for every mutation |
| `test_child_dag_is_complete_acyclic_and_independently_gated` | exact edges `3565-contract→3567`, `3566-decision+contract→3567`, and all three children→3568-close have exact URLs and owner-only approval | child graph | complete DAG, no 3565↔3566 edge, no approval inheritance |
| `test_measurement_and_remediation_ownership_do_not_cross` | #3567 cannot fix behavior and remediation children cannot grade the fleet | ownership matrix | no crossing edge |
| `test_every_failure_has_a_remediation_issue` | actionable DIVERGES cells route to a focused child | predicate table | exact issue URL per failure |
| `test_html_manual_matches_yaml_contract` | HTML terms, gestures, predicates, gates, links, and contract version match YAML | YAML plus HTML | structural and semantic parity |
| `test_closed_schema_rejects_synthetic_denied_values` | durable regression coverage rejects synthetic legal/privacy/path aliases without depending on a working-tree diff | synthetic denied strings and path shapes | validation failure with no raw value echoed |

---

## Acceptance Criteria

- [ ] Parent contract tests will be written first and observed failing before the YAML
      contract and HTML manual are implemented.
- [ ] The YAML contract will define versioned canonical terms and exactly
      `dictation_activation`, `clipboard_text_paste`, `focused_text_injection`, and
      `terminal_input_contract`, plus evidence fields, statuses, per-predicate
      applicability, freshness, a recursively closed evidence schema, rollback
      obligations, issue ownership, and the exact dependency DAG.
- [ ] The HTML manual will explain the same contract with a Windows/Linux gesture table,
      event-flow diagrams, HITL checkpoints, pet-peeve intake template, and rollback path.
- [ ] Parent approval will not authorize child implementation; every child will retain
      its own resource intel, plan, adversarial review, user approval, TDD, code/artifact
      review, issue comment, and closeout gate.
- [ ] #3566 planning will precede any paste remap and will stop for the user's literal
      `Ctrl+Insert` versus `Shift+Insert` decision after plain-Bash and Codex reproduction
      are specified.
- [ ] #3565 will own only Linux shortcut migration/rollback and documentation. It will
      preserve the local dictation privacy boundary, leave Windows configuration alone,
      preserve unrelated GNOME bindings, fail closed on unknown ownership, and restore
      prior GVariant values only when tool ownership still matches.
- [ ] #3567 planning will consume versioned evidence-interface sections from approved
      #3565/#3566 plans. Its implementation may land before live remediation only if
      missing evidence remains explicit and no parity claim is made.
- [ ] #3567 will add a separate `interaction_ux` family without changing `behavior` b1-b5,
      will grade each machine against a platform/role contract before fleet rollup, and
      will link failures to remediation issues.
- [ ] #3567 will add predicate-level `capabilities.interaction_ux` applicability to
      `config/workstations/registry.yaml`, the declared machine capability authority;
      introduce explicit active/unreachable status semantics in that registry schema;
      update `scripts/readiness/harness-config.yaml` only as a derived equality projection;
      add historical deferred member `home-win` to the registry with explicit unreachable
      status; reconcile `macbook-portable` against live state; add
      `gali-linux-compute-1` to the projection; and extend set-equality tests so no
      registry-only or projection-only machine can disappear through stale assumptions.
- [ ] Roster coverage will be enumerated from `config/workstations/registry.yaml` at
      execution time and reconciled with the harness projection. Applicable predicates
      without fresh evidence will report `MISSING-EVIDENCE`; currently unreachable
      applicable machines will report `UNREACHABLE`; only an explicitly inapplicable
      machine-and-predicate pair on a reachable machine will report bounded
      `EXPECTED-DIVERGENCE`. `interaction_ux` will explicitly preserve the existing
      matrix precedence `UNREACHABLE` before applicability, then freshness, then outcome.
- [ ] Interaction evidence will use a recursively closed schema that rejects unknown
      keys and nested free text. It will allow only bounded enums, versions, booleans,
      timestamps, repository issue URLs, and SHA-256 synthetic fixture digests; it will
      reject aliases and values carrying real clipboard text, dictated content/audio,
      screenshots, raw commands, secrets, client identifiers, or private absolute paths.
- [ ] #3566 will preserve its amended contract: paste parity will compare route input
      digests and canonical composer-draft digests separately, will
      empirically pin the installed CLI's CR/CRLF behavior before selecting a
      canonicalization version, and will expose any normalization loss while requiring
      exact-once insertion, no auto-submit, `CLIPBOARD` selection, Unicode/tab/multiline,
      and trailing-newline cases.
- [ ] Dictation parity will treat Windows `Win+H` and Ubuntu `Super+H` as the same semantic
      activation intent with semantic verdict `EQUAL`; a separate processing-boundary
      annotation will record OS-managed versus repo-local privacy as
      `EXPECTED-DIVERGENCE`, never overwrite the semantic verdict, and never claim false
      privacy equivalence.
- [ ] A refreshed `observed_at` will cause a later report `generated_at` value that passes
      the existing `scripts/readiness/publish-equality.sh` newer-than gate, while semantic cross-machine
      comparison will exclude observation time and literal chord.
- [ ] `uv run pytest tests/architecture/test_interaction_ux_parity_contract.py -v` will pass.
- [ ] Focused child test suites and the full readiness/architecture regression set will
      pass in each separately approved implementation issue.
- [ ] New files will be added with intent-to-add or staged before
      `scripts/legal/legal-sanity-scan.sh --diff-only`. The operator will first record the
      non-empty output of `git diff --name-only HEAD -- <exact parent paths>` as the scan
      target proxy, then record scanner exit 0. `scripts/enforcement/check-no-abs-paths.sh` will
      cover tracked Python/shell paths; the closed-schema tests and legal scan will cover
      YAML/HTML because the absolute-path checker does not target those extensions.
- [ ] The HTML manual will pass desktop/mobile visual inspection, and its parity test will
      verify unique anchors, balanced structural tags, contract version, required links,
      predicates, statuses, and gates.
- [ ] Before epic closure, all three children will be complete, the authoritative roster
      and its equality projection will be reconciled, every named registry machine will
      have fresh predicate evidence or explicit non-parity status, and stale/dirty
      checkout evidence will not support a parity claim.
- [ ] Closeout will call `classify(...)` from `scripts/workflow/completeness_score.py`
      against the actual changed paths and available package mapping rather than choose a
      class in advance; compute the corresponding issue-3568-bound score; render
      `docs/reports/<completion-date>-3568-completeness.html`, stamp the exact JSON into
      kanban metadata via `hermes kanban complete --metadata`, stamp the same JSON into
      the issue body's fenced `completeness` block, meet the server-configured derived-class
      threshold, and then stop for an authorized owner to apply
      `status:completeness-verified`. Any later body edit will invalidate verification
      and require the owner label to be reapplied before closure.
- [ ] No desktop mutation, terminal remap, live keypress, clipboard capture, speech-service
      change, matrix code change, or child implementation will occur under this parent issue.

---

## Adversarial Review Summary

| Round | Revision | Claude | Codex | Gemini | Result |
|---|---|---|---|---|---|
| r1 | working tree on `origin/main@4225ab3c8` | **MAJOR** — capability authority, publish mechanism, template/source/scanner precision | **MAJOR** — authority, privacy/verdict separation, predicate applicability, exact DAG, completeness, closed schema, legal target, paste contract | **UNAVAILABLE** — no noninteractive credentials | Blocked; all concrete findings were corrected before r2. |
| r2 | revised working tree | **MINOR** — projection-only `home-win`, scan-target evidence, durable legal test, Project value, Gemini state | **MAJOR** — temporary artifact state, preselected completeness class, explicit privacy/path fixtures | **UNAVAILABLE** — no noninteractive credentials | Blocked on Codex findings; all concrete r2 findings were corrected before r3. |
| r3 | final working tree | **MINOR** — explicit registry status schema, BC3 precedence, kanban persistence, artifact packaging, loop-break disclosure | **MAJOR** — canonical artifacts were transiently empty while providers were still running | **UNAVAILABLE** — no noninteractive credentials | Review cap reached. Canonical Claude/Codex artifacts and disagreement report are now non-empty, resolving Codex's sole concrete r3 finding; no fourth verdict will be manufactured. |

**Overall result:** USER DECISION REQUIRED. Claude reached MINOR; Codex returned MAJOR
for a third round, but its only r3 finding described the temporary zero-byte output files
that existed while the parallel wave was still running. The canonical Claude and Codex
files now contain substantive reviews, Gemini contains a truthful UNAVAILABLE record,
and the disagreement report is non-empty. Under the sustained-MAJOR loop-break policy,
the plan will not manufacture r4. The HITL approval must explicitly accept both the
Claude/Codex verdict split and the T3-to-T2 provider-depth reduction.

Revisions made after r1:

- Moved machine capability authority to `config/workstations/registry.yaml`, exposed its
  drift from the equality projection, assigned predicate-level applicability and
  reconciliation to #3567, and removed machine-wide headless grading.
- Separated semantic dictation verdicts from privacy-boundary annotations and froze the
  four predicate names plus exact child dependency edges.
- Replaced the nonexistent report-fingerprint premise with the actual
  `scripts/readiness/publish-equality.sh` `generated_at` gate.
- Added the issue-bound completeness JSON/body/owner-label freshness transaction.
- Replaced field-name denylisting with a recursively closed allowlist schema and
  adversarial unknown-key/value tests.
- Required intent-to-add/staging plus non-empty legal-scan targets for new artifacts and
  documented the absolute-path checker's Python/shell-only scope.
- Corrected #3566's issue contract to separate input and canonical-draft digests, pin
  normalization empirically, and expose loss without weakening exact route equivalence.
- Corrected proposed-target collision wording and added the blank template `Project` field.

Revisions made after r2:

- Assigned `home-win` registry restoration, `macbook-portable` live reconciliation,
  `gali-linux-compute-1` projection, and strict registry/projection set equality to #3567.
- Replaced an impossible scanner-emitted target list with separately recorded exact-path
  `git diff --name-only` evidence and moved durable legal/privacy proof to synthetic
  closed-schema fixtures.
- Removed the preselected completeness class; closeout will call `classify(...)` against
  actual paths and package mapping, then use the derived class.
- Enumerated adversarial fixtures for raw clipboard/transcript/audio, screenshots, raw
  commands, secrets, client identifiers, private POSIX/Windows paths, aliases, nesting,
  unknown keys, and wrong types.
- Recorded Gemini's second noninteractive-auth failure and retained the T3-to-T2
  degradation disclosure for the user gate.

Final packaging after r3:

- Introduced explicit registry status semantics, restored `UNREACHABLE`-first BC3
  precedence, and added required kanban completeness persistence.
- Populated the canonical Claude/Codex/Gemini artifacts and generated the disagreement
  report; all four canonical files are non-empty.
- Stopped after the third Codex MAJOR as required. Its sole r3 finding is resolved by the
  final artifact state but remains visible as a minority verdict for user disposition.

---

## Risks and Open Questions

- **HITL chord ambiguity:** the user reported `Ctrl+Insert`, while conventional paste is
  `Shift+Insert` and current GNOME Terminal uses `Ctrl+Shift+V`. #3566 will reproduce and
  ask the user before any remap; this parent will not guess.
- **Desktop collision risk:** live configuration assigns `<Super>h` to minimize and
  `<Super><Shift>v` to dictation. #3565 will require a two-phase transaction, exact-state
  journal, idempotence, ownership-aware uninstall, and live desktop rollback proof.
- **Passive hotkey risk:** a listener can receive `Super+H` while GNOME also acts on it.
  The shortcut child will treat collision removal and no-minimize verification as
  load-bearing, not cosmetic.
- **Terminal ownership risk:** right-click behavior can differ under mouse reporting,
  remote sessions, and terminal emulators. #3566 will reproduce first in plain Bash and
  then Codex before assigning the defect to terminal configuration or Codex.
- **Registry/projection drift risk:** the authoritative workstation registry and equality
  projection disagree on membership/status and neither has predicate applicability.
  #3567 will add `capabilities.interaction_ux` to the registry, reconcile the projection,
  and grade each predicate independently without hostname or broad-role inference.
- **Freshness/churn risk:** manual evidence must refresh the published report without
  becoming the semantic comparison value. The contract and #3567 tests will pin the two
  projections separately.
- **Stale-fleet risk:** current equality artifacts do not cover `gpu-claw`, and available
  reports include stale/dirty checkouts. Epic closeout will use a newly enumerated roster
  and will not promote current partial evidence into a parity claim.
- **Provider-feature drift:** Codex realtime voice is experimental and can change. It will
  remain a rejected implementation dependency unless a future separately planned issue
  replaces the stable repo-native workflow.

---

## Complexity: T3

**T3** — the epic spans Linux/Windows interaction semantics, desktop and terminal
ownership, privacy/rollback, a versioned evidence contract, machine-role applicability,
freshness, HTML reporting, and three independently gated implementation children.
