# Issue #2424 ecosystem CI health audit

Generated: `2026-04-27T22:30:00+00:00`

## Summary

| State | Count |
|---|---:|
| Green | 3 |
| Red | 4 |
| No signal | 0 |
| Unknown | 0 |

Open tracked issue evidence: `#2424` OPEN `enhancement,priority:medium,cat:infrastructure,status:working,agent:codex,maintenance,status:plan-approved`; `#2433` OPEN `priority:high,cat:infrastructure,status:working,agent:codex,status:plan-approved`; `#2459` OPEN `priority:medium,cat:infrastructure,status:working,agent:codex,status:plan-approved`; `#2490` OPEN `enhancement,priority:medium,cat:infrastructure,status:plan-review`

## Repo Evidence

| Repo | State | Tracker | Latest main-branch workflow evidence | Note |
|---|---|---|---|---|
| [`vamseeachanta/workspace-hub`](https://github.com/vamseeachanta/workspace-hub) | Green | #2437 | [Baseline Testing](https://github.com/vamseeachanta/workspace-hub/actions/runs/25020714455) `success` at `2026-04-27T21:33:02Z` | workspace-hub child closed; parent remains rollup |
| [`vamseeachanta/worldenergydata`](https://github.com/vamseeachanta/worldenergydata) | Red | #2433 | [CI](https://github.com/vamseeachanta/worldenergydata/actions/runs/24996694082) `failure` at `2026-04-27T13:04:34Z`<br>[.github/workflows/docs.yml](https://github.com/vamseeachanta/worldenergydata/actions/runs/24996693327) `failure` at `2026-04-27T13:04:33Z`<br>[Dependabot Updates](https://github.com/vamseeachanta/worldenergydata/actions/runs/24996650191) `success` at `2026-04-27T13:03:41Z`<br>[Nightly](https://github.com/vamseeachanta/worldenergydata/actions/runs/24974448044) `failure` at `2026-04-27T03:00:31Z` | main CI and Dependabot blocker lane |
| [`vamseeachanta/digitalmodel`](https://github.com/vamseeachanta/digitalmodel) | Red | #2441 / #2490 | [Dependency Graph](https://github.com/vamseeachanta/digitalmodel/actions/runs/24975627332) `failure` at `2026-04-27T03:49:26Z`<br>[Build API Docs](https://github.com/vamseeachanta/digitalmodel/actions/runs/24975626763) `success` at `2026-04-27T03:49:25Z`<br>[Quality Gates](https://github.com/vamseeachanta/digitalmodel/actions/runs/24975626765) `failure` at `2026-04-27T03:49:25Z` | pylife child closed; coverage-gate follow-up open |
| [`vamseeachanta/assethold`](https://github.com/vamseeachanta/assethold) | Red | #2442 / #2448 / #2459 | [Python Tests](https://github.com/vamseeachanta/assethold/actions/runs/24946909831) `failure` at `2026-04-26T03:06:28Z`<br>[.github/workflows/docs.yml](https://github.com/vamseeachanta/assethold/actions/runs/24792042937) `failure` at `2026-04-22T17:12:17Z` | startup/smoke children closed; hardening plan remains |
| [`vamseeachanta/achantas-data`](https://github.com/vamseeachanta/achantas-data) | Red | #2443 | [link-check](https://github.com/vamseeachanta/achantas-data/actions/runs/24998480318) `failure` at `2026-04-27T13:40:43Z`<br>[markdown-lint](https://github.com/vamseeachanta/achantas-data/actions/runs/24959525884) `success` at `2026-04-26T14:54:30Z`<br>[Python Tests](https://github.com/vamseeachanta/achantas-data/actions/runs/18252775917) `failure` at `2025-10-05T02:35:49Z` | CI restored; scheduled link-check must stay observable |
| [`vamseeachanta/aceengineer-admin`](https://github.com/vamseeachanta/aceengineer-admin) | Green | #2444 | [CI](https://github.com/vamseeachanta/aceengineer-admin/actions/runs/24961076938) `success` at `2026-04-26T16:09:41Z` | minimal CI bootstrap child closed |
| [`vamseeachanta/assetutilities`](https://github.com/vamseeachanta/assetutilities) | Green | reference | [Source Hygiene](https://github.com/vamseeachanta/assetutilities/actions/runs/25020866448) `success` at `2026-04-27T21:36:34Z`<br>[Tests](https://github.com/vamseeachanta/assetutilities/actions/runs/25020866457) `success` at `2026-04-27T21:36:34Z`<br>[Build API Docs](https://github.com/vamseeachanta/assetutilities/actions/runs/25020866480) `success` at `2026-04-27T21:36:34Z` | known green reference repo |

## Guard Contract

- The audit filters to `main` branch runs and CI-like events so Dependabot PR noise cannot mask red main evidence.
- One latest run per workflow is shown to avoid stale older failures overriding newer green runs.
- The seven-repo scoreboard is hard-coded because #2424 is a fixed ecosystem rollup, not a broad repo rewrite lane.
- This report is evidence only; child issue implementation and closure still follow their individual approved plans.

## Reproduce

```bash
uv run python scripts/ci_health/ecosystem_ci_audit.py --output docs/reports/2026-04-27-issue-2424-ecosystem-ci-health-audit.md --limit 30
```
