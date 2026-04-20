# aceengineer-website Dependabot Orphan-Path Verification

**Date:** 2026-04-20
**Issue:** vamseeachanta/aceengineer-website#2407
**Investigator:** Claude (triage subagent, Wave 4)
**Hypothesis:** All 29 open dependabot vulnerability alerts on `aceengineer-website` target `ref/py_react_sql/client/yarn.lock` — a path deleted from `main` in commit `06f38714` ("refactor: transform to static site with PostHTML partials"). If true, all 29 are dismissible as "vulnerable code path removed".

## Result: HYPOTHESIS VERIFIED (29 of 29 alerts)

## Evidence

### 1. Deletion commit confirmed

- **SHA:** `06f38714977cd3404414a6c6e2ea5ae9cedb8212`
- **Date:** 2026-01-26
- **Message:** `refactor: transform to static site with PostHTML partials`
- **Scope (from commit body):** Removed legacy Flask app (`digitaltwinfeed/`), reference projects (`ref/`), inherited agent infrastructure, obsolete config; ~25 MB deleted.
- The GitHub REST commit API truncates the `.files` array to 300 entries, so the full deletion isn't enumerable in one call. However:
  - `GET /repos/.../commits?path=ref/py_react_sql/client/yarn.lock` returns exactly 2 commits: `06f38714` (the deletion) and `bff9969b` (2025-07-29 — an earlier touch). No further history. This confirms `06f38714` is the commit that removed the path from `main`.
  - `GET /contents/ref/py_react_sql/client/yarn.lock` → HTTP 404
  - `GET /contents/ref/py_react_sql` → HTTP 404

### 2. Live tree has zero `ref/` directory

Scanned `git/trees/main?recursive=1`:
- All `package.json` / `package-lock.json` / `yarn.lock` entries in live main: **exactly 2** — `package.json` and `package-lock.json` at repo root.
- Paths containing `ref/py_react_sql`: **0**
- Paths containing `ref/`: **0**

### 3. Root manifest analysis (LIVE)

Live `package.json` (root) devDependencies:
```
clean-css ^5.3.3
jest ^30.2.0
jest-environment-jsdom ^30.2.0
posthtml ^0.16.6
posthtml-expressions ^1.11.3
posthtml-include ^2.0.1
purgecss ^8.0.0
```
Zero direct intersection with the 29 vulnerable packages.

### 4. Alert enumeration — 29 open alerts, ALL orphan

Grouped by manifest_path via `GET /dependabot/alerts?state=open`:

| Manifest path | Count |
|---|---|
| `ref/py_react_sql/client/yarn.lock` | **29** |
| (any live path) | **0** |

Full alert table:

| # | Severity | Package | GHSA | Manifest | In live tree? | Dismissible? |
|---|---|---|---|---|---|---|
| 46 | medium | follow-redirects | GHSA-r4q5-vmmm-2653 | ref/py_react_sql/client/yarn.lock | No | Yes |
| 45 | medium | picomatch | GHSA-3v7f-55p6-f55p | ref/py_react_sql/client/yarn.lock | No | Yes |
| 44 | high | picomatch | GHSA-c2c7-rcm5-vvqj | ref/py_react_sql/client/yarn.lock | No | Yes |
| 43 | medium | lodash | GHSA-f23m-r3pf-42rh | ref/py_react_sql/client/yarn.lock | No | Yes |
| 42 | high | lodash | GHSA-r5fr-rjxr-66jc | ref/py_react_sql/client/yarn.lock | No | Yes |
| 41 | high | lodash.template | GHSA-r5fr-rjxr-66jc | ref/py_react_sql/client/yarn.lock | No | Yes |
| 40 | high | path-to-regexp | GHSA-37ch-88jc-xwx2 | ref/py_react_sql/client/yarn.lock | No | Yes |
| 39 | medium | serialize-javascript | GHSA-qj8w-gfj5-8c6v | ref/py_react_sql/client/yarn.lock | No | Yes |
| 38 | high | node-forge | GHSA-2328-f5f3-gj25 | ref/py_react_sql/client/yarn.lock | No | Yes |
| 37 | high | node-forge | GHSA-5m6q-g25r-mvwx | ref/py_react_sql/client/yarn.lock | No | Yes |
| 36 | high | node-forge | GHSA-q67f-28xg-22rw | ref/py_react_sql/client/yarn.lock | No | Yes |
| 35 | high | node-forge | GHSA-ppp5-5v6c-4jwp | ref/py_react_sql/client/yarn.lock | No | Yes |
| 34 | medium | yaml | GHSA-48c2-rrv3-qjmp | ref/py_react_sql/client/yarn.lock | No | Yes |
| 33 | high | flatted | GHSA-rf6f-7fwh-wjgh | ref/py_react_sql/client/yarn.lock | No | Yes |
| 32 | high | flatted | GHSA-25h7-pfq9-p65f | ref/py_react_sql/client/yarn.lock | No | Yes |
| 31 | high | minimatch | GHSA-7r86-cg39-jmmj | ref/py_react_sql/client/yarn.lock | No | Yes |
| 30 | high | minimatch | GHSA-23c5-xmqv-rm74 | ref/py_react_sql/client/yarn.lock | No | Yes |
| 29 | high | serialize-javascript | GHSA-5c6j-r48x-rmvq | ref/py_react_sql/client/yarn.lock | No | Yes |
| 28 | high | minimatch | GHSA-3ppc-4f35-3m26 | ref/py_react_sql/client/yarn.lock | No | Yes |
| 27 | medium | bn.js | GHSA-378v-28hj-76wf | ref/py_react_sql/client/yarn.lock | No | Yes |
| 26 | medium | bn.js | GHSA-378v-28hj-76wf | ref/py_react_sql/client/yarn.lock | No | Yes |
| 24 | medium | ajv | GHSA-2g4f-4pwh-qvx6 | ref/py_react_sql/client/yarn.lock | No | Yes |
| 22 | medium | url-parse | GHSA-rqff-837h-mm52 | ref/py_react_sql/client/yarn.lock | No | Yes |
| 21 | medium | url-parse | GHSA-8v38-pw62-9cw2 | ref/py_react_sql/client/yarn.lock | No | Yes |
| 19 | **critical** | **pbkdf2** | **GHSA-v62p-rq8g-8h59** | ref/py_react_sql/client/yarn.lock | **No** | **Yes** |
| 18 | low | qs | GHSA-w7fw-mjwx-w883 | ref/py_react_sql/client/yarn.lock | No | Yes |
| 17 | high | semver | GHSA-c2qf-rxjj-qqgw | ref/py_react_sql/client/yarn.lock | No | Yes |
| 16 | medium | url-parse | GHSA-hh27-ffr2-f2jc | ref/py_react_sql/client/yarn.lock | No | Yes |
| 15 | medium | url-parse | GHSA-jf5r-8hm2-f872 | ref/py_react_sql/client/yarn.lock | No | Yes |

Severity breakdown: 1 critical (pbkdf2), 16 high, 11 medium, 1 low.

### 5. Nuance: transitive overlap in LIVE package-lock.json

The LIVE root `package-lock.json` does contain transitive references to `semver`, `picomatch`, and `minimatch` (via jest, posthtml, purgecss). However:
- **Dependabot did not flag any of them** — all 29 alerts are scoped exclusively to the deleted orphan manifest path.
- The live transitive versions are presumably on safe (non-vulnerable) ranges; otherwise, dependabot would have raised separate alerts with `manifest_path = "package-lock.json"`.
- If dismissal proceeds and dependabot later re-raises against the live path, those would be genuine new alerts requiring their own fix (npm update / audit fix / manifest bump).

### 6. Build-system dependency check

`build.js` contains no references to `ref/` or `py_react_sql`. The PostHTML build walks `src/` only. The deleted reference project is not reachable from any live build, runtime, or test path.

## Classification summary

| Bucket | Count |
|---|---|
| Orphan-path, dismissible | 29 |
| Live-path, needs-fix | 0 |
| **Total open alerts** | **29** |

## Recommendation

Dismiss all 29 alerts with rationale `"Vulnerable code path removed from main in commit 06f38714 (2026-01-26). The manifest 'ref/py_react_sql/client/yarn.lock' does not exist on the default branch. No live runtime, build, or test path depends on any of these packages."` (GitHub dismissal reason: `not_used`.)

Do NOT auto-dismiss. User decision.

## Follow-up watch items

1. Confirm dependabot stops re-flagging the deleted path within 7 days of dismissal (GitHub sometimes re-scans branch tips).
2. If any new alert appears with `manifest_path = "package-lock.json"` (root), treat as genuine — run `npm audit fix` / bump direct devDeps.
3. Confirm no stale branches / PRs still reference `ref/py_react_sql/` — those could keep the alerts alive on non-default branches (dependabot tracks default branch by default, so likely moot, but worth a spot check).

## Commands executed (for reproducibility)

```bash
gh api repos/vamseeachanta/aceengineer-website/commits/06f38714 --jq '.commit.message'
gh api repos/vamseeachanta/aceengineer-website/contents/ref/py_react_sql/client/yarn.lock  # 404
gh api repos/vamseeachanta/aceengineer-website/contents/ref/py_react_sql                     # 404
gh api "repos/vamseeachanta/aceengineer-website/commits?path=ref/py_react_sql/client/yarn.lock"
gh api "repos/vamseeachanta/aceengineer-website/dependabot/alerts?state=open&per_page=100" --paginate \
  --jq '[.[] | {number, severity: .security_advisory.severity, package: .dependency.package.name, ghsa: .security_advisory.ghsa_id, manifest: .dependency.manifest_path}]'
gh api "repos/vamseeachanta/aceengineer-website/git/trees/main?recursive=1" \
  --jq '[.tree[] | select(.path | test("package\\.json$|package-lock\\.json$|yarn\\.lock$")) | .path]'
gh api repos/vamseeachanta/aceengineer-website/contents/package.json \
  --jq '.content | @base64d | fromjson | {dependencies, devDependencies}'
```

No `gh api` errors during investigation.
