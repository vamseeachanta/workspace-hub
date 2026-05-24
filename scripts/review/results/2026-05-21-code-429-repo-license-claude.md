# Code review — worldenergydata-wiki repo scaffold + license posture

**Reviewer**: Claude (adversarial, code-stage)
**Date**: 2026-05-21
**Scope**: vamseeachanta/worldenergydata#429 implementation — new public sibling wiki repo `vamseeachanta/worldenergydata-wiki`
**Companion reviewer focus**: governance + cross-wiki linking (separate report)
**This review**: repo-scaffold quality, license posture, leak audit

---

VERDICT: MAJOR

---

## FINDINGS

### [MAJOR] LICENSE file does not parse as CC-BY-4.0; GitHub shows "Other / NOASSERTION"

**Evidence**:
- `gh repo view vamseeachanta/worldenergydata-wiki --json licenseInfo` → `{"key":"other","name":"Other","nickname":""}`
- `gh api repos/vamseeachanta/worldenergydata-wiki --jq '.license'` → `{"key":"other","name":"Other","spdx_id":"NOASSERTION",...}`
- `/mnt/local-analysis/worldenergydata-wiki/LICENSE:1-33` — file contains a **paraphrased summary** of CC-BY-4.0 ("You are free to: Share — copy and redistribute...") followed by a note on underlying data; it is NOT the canonical CC-BY-4.0 legal text.

**Why this matters**: GitHub's license detector (Licensee gem) does fuzzy hash matching against the canonical CC-BY-4.0 text from `https://api.github.com/licenses/cc-by-4.0`. A paraphrase fails the hash check, GitHub renders the repo as "Other (NOASSERTION)", the green license badge does not appear, and the repo will NOT show in CC-BY-4.0 filtered searches. For a wiki whose entire reason to exist is "make this content discoverable and redistributable", invisible-license posture defeats the goal.

**The CC-BY-4.0 README footer prose in the LICENSE file** has additional legal risk: paraphrasing a Creative Commons license without using the canonical text means the *paraphrase* (not the actual CC-BY-4.0) is what binds downstream users. Creative Commons explicitly warns against this — see their FAQ on "I want to use a CC license — can I rewrite it?".

**Fix**: replace `LICENSE` with the canonical CC-BY-4.0 legalcode body returned by `gh api /licenses/cc-by-4.0 --jq .body` (or downloaded from `https://creativecommons.org/licenses/by/4.0/legalcode.txt`). Keep the "Note on underlying data" preamble as a separate `NOTICE` file or move it to `README.md`. Re-verify `gh api repos/... --jq '.license.spdx_id'` returns `CC-BY-4.0`. The LICENSE-CODE (MIT) file at `:1-25` is canonical-text-correct and parses fine if isolated, but GitHub only detects the *root* LICENSE, so MIT will be invisible regardless — see next finding.

---

### [MAJOR] Dual-license layout is unrecognized by GitHub; MIT is invisible

**Evidence**:
- Repo root has `LICENSE` (CC-BY-4.0 paraphrase) and `LICENSE-CODE` (MIT canonical).
- GitHub license detector reads ONE root-level `LICENSE*` file — it does not aggregate dual-license layouts.
- README.md:7-10 declares dual licensing in prose only.

**Why this matters**: even if the CC-BY-4.0 LICENSE is fixed (above finding), the MIT scope for `scripts/`, `ci/`, tooling is communicated to humans only — not to license-aware tools, dependency scanners, SBOM generators, or organizational compliance bots. A downstream consumer running `licensee detect` on this repo will see only the (eventually-fixed) CC-BY-4.0 and will assume it covers everything including future scripts.

**Fix options** (rank-ordered):
1. **Recommended**: ship CC-BY-4.0 in root `LICENSE`, and add SPDX headers (`SPDX-License-Identifier: MIT`) to the top of every script/CI file once they exist. The dual-license posture is then file-resolved, not repo-resolved. Add a `REUSE.toml` or `.reuse/dep5` file for fully-automated detection per the REUSE 3.0 spec.
2. **Acceptable**: move all code to a subdirectory (`scripts/` or `tooling/`) and put `LICENSE` (MIT canonical) inside it; root `LICENSE` stays CC-BY-4.0. GitHub still only detects root, but downstream tools that walk the tree will resolve correctly.
3. **Not acceptable**: status quo — silent license-scope ambiguity.

---

### [MAJOR] `hasWikiEnabled: true` contradicts the plan; will confuse contributors

**Evidence**:
- `gh repo view ... --json hasWikiEnabled` → `true`.
- Plan and decision doc state explicitly: "regular repo with `wiki/` directory NOT GitHub Wiki feature".
- README.md:22-29 lists wiki domain pages as `wiki/bsee/index.md` (filesystem paths), confirming the design intent.

**Why this matters**: GitHub will surface a "Wiki" tab on the repo, separate from the in-tree `wiki/` directory. Contributors landing on the repo see TWO surfaces named "wiki", click the GitHub Wiki tab, create pages there, and those pages land in a separate `.wiki.git` repo invisible to the routing/license/cross-link policy this repo was built to enforce. This is exactly the confusion the plan tried to prevent.

**Fix**: `gh api -X PATCH repos/vamseeachanta/worldenergydata-wiki -f has_wiki=false`. Verify via re-running the json query.

---

### [MAJOR] Client identifiers leaked into PUBLIC repo

**Evidence**: `MIGRATION_MANIFEST.md:46`:
> `| Client-project content (B1528, SIROCCO, acma-projects) | vamseeachanta/llm-wiki-acma or vamseeachanta/llm-wiki | Client confidentiality |`

**Why this matters**: the row exists to document what should NOT come here, but it lists three client identifiers verbatim — B1528, SIROCCO, acma-projects — in a public repo's manifest file, intended specifically as a routing reference for AI agents and humans. This violates `feedback_naive_secret_scan_false_positive_cascade`-adjacent posture and the legal-deny-list policy: client identifiers should not appear in public artifacts, even in deny-list contexts. An external reader now knows three of the user's client engagements exist, by name.

**Fix**: replace specific identifiers with generic phrasing, e.g.:
> `| Client-project content (any project codename, customer-confidential dataset) | private llm-wiki-* repos | Client confidentiality |`

The internal `.claude/rules/codes-standards-data-routing.md` and `.legal-deny-list.yaml` (private to workspace-hub) can carry the explicit identifier list. Cross-check via `grep -riE 'b1528|sirocco|acma' worldenergydata-wiki/` returning zero hits.

---

### [MINOR] `/mnt/ace/` private filesystem path exposed across 7 sites in PUBLIC repo

**Evidence**:
- `MIGRATION_MANIFEST.md:24,36`
- `README.md:49` (in the frontmatter example block)
- `wiki/bsee/index.md:44`
- `wiki/noaa/index.md:31,44`
- `wiki/usgs/index.md:42`

**Why this matters**: not a credential, but telegraphs internal storage organization on the user's workstation. An attacker who later compromises any single workstation account learns that `/mnt/ace/0_mrv/` and `/mnt/ace/data/` are high-value target paths. More practically: this path is workstation-specific (`/mnt/ace/` exists on `ace-linux-1`); a teammate on `ace-windows-2` or a contractor on a Mac has no analogous mount, so the frontmatter example `sources:\n  - /mnt/ace/...` is actively misleading as a contributor template. They'll either copy a path that doesn't exist on their machine, or fabricate an analog.

**Fix**: replace literal `/mnt/ace/...` references with abstract placeholder `<off-repo-canonical>` or `${WORKSPACE_DATA_ROOT}/...` per the same posture as `${HERMES_HOME}/.env` from `feedback_skill_content_scanner_docs_tension`. Document the mapping in a single private location (workspace-hub internal docs), not the public wiki. The README frontmatter example at line 49 is the worst offender because it's a template — new contributors will copy it literally.

---

### [MINOR] "(none yet — scaffolded 2026-05-20)" is technically true but misleading

**Evidence**:
- 4 domain index pages claim no derived pages: `wiki/bsee/index.md:39`, `wiki/noaa/index.md:39`, `wiki/usgs/index.md:38`, `wiki/mms/index.md:46`.
- But `/mnt/local-analysis/worldenergydata/reports/` contains MANY derived analyses that match the wiki domains:
  - `reports/bsee/buckskin_analysis.html`, `reports/bsee/lower_tertiary/`
  - `reports/marine_safety/{executive_summary,fatality_analysis,foundering_analysis,hatch_analysis}.html` (NOAA/MMS-adjacent)
  - `reports/metocean/test_wave_rose.html` (NOAA)
  - `reports/gtm/2026-05-04-bsee-field-analysis-comprehensive.html` (BSEE)
- MIGRATION_MANIFEST.md:26 acknowledges "GTM client reports | `worldenergydata/reports/gtm/` (6 reports) | Already public; clients cite library paths directly; no re-homing".

**Why this is a defect, not a non-issue**: the manifest decides "no re-homing", which is a defensible choice for the *files themselves*, but the domain index pages still falsely claim no derived material exists. A reader of `wiki/bsee/index.md` learns nothing about the existing buckskin / lower_tertiary / GTM corpus that they could cite. The right pattern is a "Related external derived material" section on each domain index, linking to `worldenergydata/reports/bsee/*` etc. with a one-line description each. This costs ~20 lines per index page and turns the scaffold from "future plans" into "current state inventory + future plans".

**Fix**: add to each domain index a `## Related external derived material` section that links to the existing `worldenergydata/reports/<domain>/` artifacts. Preserves the "no re-homing" decision while making the existing corpus discoverable from the wiki.

---

### [MINOR] No branch protection on `main` in a legal-posture public repo

**Evidence**: `gh api repos/vamseeachanta/worldenergydata-wiki/branches/main/protection` → `404 Branch not protected`.

**Why this matters**: this repo's entire reason to exist is enforcing a license/visibility posture. A force-push or direct-commit that lands a vendor-licensed standards excerpt or a client identifier directly to `main` cannot be caught by review. The companion `worldenergydata` repo presumably has protection — this sibling needs at minimum the same: require PR, require review, disallow force-push, disallow deletion. For a one-maintainer repo, even self-PR enforcement is a meaningful tripwire that catches the "fast typo commit that includes a vendor PDF" class.

**Fix**: enable branch protection via `gh api -X PUT repos/vamseeachanta/worldenergydata-wiki/branches/main/protection ...` with at minimum: `allow_force_pushes=false`, `allow_deletions=false`, `required_status_checks` (when CI lands), and `enforce_admins=true`. If "self-PR is too much friction", at the very least disable force-push + deletion.

---

### [MINOR] Attribution / SA-contamination guidance absent from README

**Evidence**: README.md:7-12 declares CC-BY-4.0 but does not tell:
- Downstream consumers HOW to attribute (suggested attribution string: "From vamseeachanta/worldenergydata-wiki, CC-BY-4.0").
- Contributors how to handle the case where a derived page incorporates a CC-BY-SA dataset from elsewhere (SA propagation would force the derivative page to ALSO be CC-BY-SA, conflicting with this repo's CC-BY-4.0).
- The interaction between the CC-BY-4.0 prose license and the 17 USC §105 public-domain underlying data (the LICENSE file footer covers it; README does not).

**Why this matters**: ambiguity about attribution mechanics is the single most common CC-BY violation, and the user already invested in a wiki whose purpose is professional citability. Contributors who merge a CC-BY-SA dataset into a page (e.g., a Natural Earth shapefile, which is CC-BY-SA-equivalent in places) without flagging it create unmarketable cross-licensed content. SA-contamination is the same hazard pattern as `feedback_silent_verdict_flip_defect_class` at the license layer.

**Fix**: add a "## Attribution" section to README.md with (a) the recommended attribution string, (b) an explicit "do not mix CC-BY-SA inputs without surfacing in PR review" rule, (c) the 17 USC §105 distinction promoted from LICENSE footer to README body.

---

### [MINOR] No CONTRIBUTING.md / DCO mechanism for a contributor-facing wiki

**Evidence**: no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`, no DCO/CLA bot configured. README.md:62-64 "Contributing" section is two sentences.

**Why this matters**: the `contribution_status: mixed_private_contributors` frontmatter field anticipates outside contributions, but there's no mechanism (DCO sign-off, CLA, or even a CONTRIBUTING.md) that grants this repo the right to relicense or sublicense contributions. A contributor who PRs a derived page hasn't necessarily granted CC-BY-4.0 to their contribution. For a one-maintainer repo today this is academic; the moment anyone external PRs, it becomes load-bearing.

**Fix**: minimum viable CONTRIBUTING.md stating "all contributions are submitted under CC-BY-4.0 (prose) / MIT (code); by submitting a PR you agree to license your contribution under these terms". DCO sign-off via `git commit -s` is the lightweight standard.

---

### [INFO] Initial commit is the root commit — no anomaly, just noting

**Evidence**: `git log --oneline --all` → single commit `8763eb4 Initial scaffold...`.

**Note**: as a NEW repo this is expected. The branch-protection finding above is the actionable item; the root commit itself is fine.

---

## SUMMARY

The scaffold's legal intent is sound, but the LICENSE file is a paraphrase that fails GitHub's CC-BY-4.0 detector (renders as "Other / NOASSERTION"), the dual-license layout is invisible to license-aware tools, GitHub Wiki feature is enabled in contradiction to the plan, and the MIGRATION_MANIFEST leaks three client identifiers (B1528 / SIROCCO / acma-projects) verbatim into a public repo — all four of which are MAJOR for a repo whose entire purpose is legal-posture enforcement. The `/mnt/ace/` exposure and empty-scaffold honesty are MINOR fixes but worth landing before any external contributors arrive. Branch protection and CONTRIBUTING.md / attribution guidance round out the gaps. Recommend not advertising or cross-linking this repo from the privacy-flipped llm-wiki until the four MAJORs are resolved.

**Top 3 blockers**:
1. LICENSE paraphrase → replace with canonical CC-BY-4.0 text so GitHub detects it.
2. `hasWikiEnabled: true` → disable GitHub Wiki tab via API.
3. Client identifiers (B1528, SIROCCO, acma-projects) in `MIGRATION_MANIFEST.md:46` → replace with generic phrasing; move specifics to private deny-list.
