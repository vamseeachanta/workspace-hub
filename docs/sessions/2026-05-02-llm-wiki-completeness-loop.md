# LLM-wiki completeness audit loop — session log

**Started:** 2026-05-02
**Hard deadline:** +8 hours from start
**Mode:** /loop dynamic (self-paced)
**Goal:** open GH issues at `status:plan-review` for each gap area, leaving user-approval gate intact
**Protocol:** Issue → Resource Intel → Plan → Adversarial Review → `status:plan-review` → STOP

## Constraints (load-bearing)

- **Stop at `status:plan-review`** — never self-approve (memory `feedback_never_offer_to_self_label_plan_approved.md`)
- **Per #2540 epic**: raw data stays in `/mnt/ace`; wiki/git receive only summaries + metadata after separate approval per gap
- **Codex blocked** since 2026-04-23 (CLI 0.124 stdin-hang upstream regression #2479); reviewers = Gemini + Claude-internal
- **Future tense only** in plan files (memory `feedback_plan_past_tense_artifact_claims.md`)
- **No overlap** with existing in-flight work: #2540 (Elements epic), #2541 SESA, #2542 Doris University, #2543 Doris codes, #2544 Woodfibre LNG, #2559 OCIMF Tandem

## Gap-priority queue (rotating, gap-prioritized)

| Priority | Wiki area | Gap signal | Wave |
|---|---|---|---|
| P1 | engineering-standards / API | 9 wiki files vs 43 GB raw at /mnt/ace/O&G-Standards/API | W1 |
| P1 | engineering-standards / DNV | 9 wiki files; DNV is dense raw | W2 |
| P1 | engineering-standards / ASME | 9 wiki files; ASME pressure-vessel spans | W2 |
| P1 | engineering-standards / ABS | 9 wiki files; offshore unit rules | W3 |
| P2 | asset-management completeness | 4 wiki files; thin domain | W1 |
| P2 | naval-architecture topical | 62 wiki files; check missing core topics | W1 |
| P2 | maritime-law topical | 22 wiki files; verify coverage | W3 |
| P2 | engineering wiki gap audit | 521 raw vs 105 wiki — uncovered subdirs | W1 |
| P3 | engineering / pipeline-installation deeper | subset audit | W4 |
| P3 | engineering / mooring deeper | subset audit | W4 |
| P3 | engineering / riser deeper | subset audit | W4 |
| P3 | online-resource registry refresh | latest standards revisions | W5 |
| P4 | personal wiki content audit | 5 files; verify scope intent | later |
| P4 | health-reports wiki scope | 0 raw / 0 wiki — what is this? | later |
| P4 | acma-projects beyond Elements wave | non-Elements raw | later |

## Cycle log

| Cycle | Started | Areas | Plans drafted | Issues opened | Reviews | Status |
|---|---|---|---|---|---|---|
| 1 | 2026-05-02 | TBD | 0 | 0 | — | dispatching |
