# Disagreement report — plan #2746 (2026-05-20)

## Verdicts

| Provider | Verdict |
|---|---|
| claude | MINOR |
| codex | MAJOR |

## Findings unique to each provider

A finding is 'unique to X' if its text appears in X's artifact but not
verbatim in any other provider's artifact.

### claude

- **TDD tests 3, 4, 8 — RED-condition construction not specified, risks live-state pollution or test-only-passes-on-network-fail.**
- Test 3 ("GH repo for `bootstrapped` entry doesn't exist") requires the registry to point at a missing repo. If the test uses the live registry, no fail can be produced without breaking the live data. If it uses a fixture registry, the plan does not say where the fixture lives or how the runner selects it. The pseudocode in §Pseudocode `check-client-wiki-registry.sh` does not parameterize the registry path beyond `${REPO_ROOT}/config/client-wikis.yml`. Fix: add a `REGISTRY_PATH` env override (`REGISTRY_PATH="${REGISTRY_PATH:-${REPO_ROOT}/config/client-wikis.yml}"`) and have tests construct per-test fixtures under `tests/enforcement/fixtures/`.
- Test 4 same issue (visibility mismatch — can't reproduce against live PRIVATE without poking GH).
- Test 8 (firewall guard: `client-private` `raw_roots` contains public llm-wiki path) requires a polluted-registry fixture; same fix applies.
- **Factory-skill step 9 ("Update `config/client-wikis.yml`") spans two repos without commit semantics.** Steps 4 (`git clone`) and 8 (initial commit + push) operate inside the NEW client wiki repo. Step 9 modifies workspace-hub `config/client-wikis.yml`, which is a different repo. The skill does not specify: (a) `cd $WORKSPACE_HUB`, (b) `git commit -m "..." -- config/client-wikis.yml` (pathspec form per `feedback_multi_agent_commit_serialization`), (c) `git push` for workspace-hub. Implementer who copy-pastes literally will edit the file without committing it, leaving inconsistent state. Fix: split step 9 into two sub-steps (edit + commit) and make the repo context explicit.
- **T8 sync check is incomplete.** The plan says: "Verify `/mnt/local-analysis/llm-wiki-acma/` is fully synced with origin: `cd /mnt/local-analysis/llm-wiki-acma && git status && git fetch && git diff origin/main..main --quiet`". This catches *tracked-commit* divergence between local main and origin/main. It does NOT catch (a) uncommitted changes (`git status` is run but its exit code not consulted), (b) untracked files that exist in NTFS clone but not ext4, (c) unpushed commits to non-main branches. Since the next step is `rm -rf /mnt/ace/llm-wiki-acma/`, this is data-loss territory if any of those conditions hold. Fix: explicit checks:
-    ```bash
-    cd /mnt/ace/llm-wiki-acma
-    [[ -z "$(git status --porcelain)" ]] || { echo "NTFS clone has uncommitted/untracked changes; ABORT"; exit 1; }
-    git fetch origin --quiet
-    [[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] || { echo "NTFS clone diverges from origin; ABORT"; exit 1; }
-    for branch in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
-      git diff "$branch" "origin/$branch" --quiet 2>/dev/null || { echo "NTFS clone branch $branch unpushed; ABORT"; exit 1; }
-    done
-    ```
-    Run these checks on the NTFS clone (the one being deleted), not on the ext4 clone.
- **Acceptance criterion for `LICENSE` OSS-keyword check is grep-fragile.** Plan says: "`grep -i 'MIT\|Apache\|BSD\|CC-BY' LICENSE` returns 0 hits". Two corner cases: (a) the word "license" in any proprietary-license boilerplate is fine, but if the boilerplate accidentally mentions "this is NOT an MIT license" or "see Apache 2.0 for what we are NOT", the grep flags false-positives. (b) a properly-proprietary LICENSE could include phrases like "based on MIT-style language" in a comment. Fix: tighten the regex to match common OSS-license boilerplate headers (e.g., `'Licensed under the MIT'`, `'Apache License, Version 2.0'`, `'BSD 3-Clause'`, `'Creative Commons'`) rather than bare acronyms. Or invert: grep for proprietary markers (`'All rights reserved'`, `'Proprietary'`, `'Confidential'`) must be PRESENT.
- **Schema field `client` is in the existing acma ledger example but missing from the proposed `config/client-wikis.yml` shape.** The ledger has `client: acma` at the top level (per live inspection). The registry uses `short_name: acma` instead. Both refer to the same concept. Pick one and use it consistently: either rename ledger's `client:` to `short_name:` (preferable, since the registry name is more precise), OR add `client:` as a field in the registry. Plan should note the consolidation as a follow-on or include it now.
- **`tests/enforcement/test_client_wiki_registry.sh` shell-test design ergonomics question.** Several similar repo tests use Python (see `scripts/legal/legal-sanity-scan.sh` is shell, but `tests/` tree has mixed Python and shell). The pseudocode test runner uses `declare -F` enumeration which works only on bash, not POSIX sh. Plan should pin `#!/usr/bin/env bash` and document this (or accept that test 1's "no stderr" assertion is hard to verify in pure shell-redirect).
- **Resource Intelligence Evidence section timestamps are session-bound, not implementation-time.** The plan says "verified 2026-05-20T18:30Z via `gh issue view`" and "ls -la /mnt/local-analysis/llm-wiki-acma/ 2026-05-20T12:50Z". By the time implementation runs (post-approval), these timestamps will be stale. Per `feedback_attestation_enables_contradiction_detection`, this is forward-looking and OK as a snapshot, but the implementer should re-verify at implementation start (and the plan does not say so explicitly).
- **The plan does not name a fallback for `yq` absence.** Pseudocode `command -v yq` is implied by usage but not pre-checked. If implementer runs on a machine without yq, the checker errors mid-loop with a misleading message. Fix: add `command -v yq >/dev/null || { echo "FAIL: yq v4+ required (https://github.com/mikefarah/yq)"; exit 1; }` at the script head.
- **T1 single commit for ~250 LOC across 11 files is reviewer-hostile.** The example T1 commit message ("feat(client-wiki-factory): template tree for per-client private wikis") doesn't help adversarial review surface which file has which content. Suggest splitting into 2 commits at minimum: (a) docs files (READMEs, DATA-CYCLE, REDACTION-POSTURE), (b) machinery (LICENSE, .gitignore, .claude/CLAUDE.md). Mild defect; pure ergonomics.
- **Acceptance criterion "Adversarial review (T2: Claude + Codex) produces APPROVE on both code and plan stages" — operationally undefined for the Codex side in this session.** Per the brainstorming-session decision, Codex review is DEFERRED to batch agents or a separate session. The plan should explicitly say "Codex review may be deferred and surfaced as a separate review artifact at `scripts/review/results/2026-05-20-plan-2746-codex.md`; if UNAVAILABLE at plan-review time, plan-review gating cites both providers' status."

### codex

- Plan factory step 5 uses `cp -r workspace-hub/templates/client-llm-wiki/* /mnt/local-analysis/llm-wiki-<short_name>/`. The `*` glob will not copy dotfiles/directories, so `templates/client-llm-wiki/.gitignore` and `templates/client-llm-wiki/.claude/CLAUDE.md` are omitted from new repos. Those files are explicitly listed as firewall artifacts in the plan’s Artifact Map, making this a privacy-firewall failure.
- Plan §Files to Change T1 says `templates/client-llm-wiki/DATA-CYCLE.md` will be copied “verbatim” from `/mnt/local-analysis/llm-wiki-acma/DATA-CYCLE.md` and the Artifact Map calls it “Client-agnostic.” The fetched `vamseeachanta/llm-wiki-acma@main:DATA-CYCLE.md` is not client-agnostic: it says “This repository is the private ACMA LLM-wiki target” and names `vamseeachanta/acma-llm-wiki`. Copying it verbatim would bake ACMA and the stale old repo name into every future template instance.
- Plan §Artifact Map says existing `llm-wiki-acma` files are “kept as-is,” and T6 only adds four firewall files. The fetched `vamseeachanta/llm-wiki-acma@main:README.md` still has title `# acma-llm-wiki`, says “Recommended repo name … `acma-llm-wiki`,” and `DATA-CYCLE.md` still names `vamseeachanta/acma-llm-wiki`. The plan does not update these stale references after the D4’ rename to `llm-wiki-acma`, so the final repo will contradict the target repo name and the registry.
- Plan §TDD Test List says all tests are implemented in `tests/enforcement/test_client_wiki_registry.sh`, but test #9 is explicitly “n/a (template-instantiation test, not registry test)” and runs on `/mnt/local-analysis/llm-wiki-acma/LICENSE` after T6. That cannot be part of the T3 RED suite that must run before T4, because the target file is only created in T6. The acceptance criterion “All 9 TDD tests in `tests/enforcement/test_client_wiki_registry.sh` pass” is therefore internally inconsistent.
- Governance spec §4.3 requires the checker to validate `isArchived=false` for non-retired entries and that `local_working_clone` remote matches `repo`. The plan’s checker pseudocode only queries `gh repo view "$REPO" --json visibility`, and the local clone check only tests `[[ -d "$CLONE/.git" ]]`. This omits two correctness-critical validations from the cited source contract.
- Plan §Pseudocode comment says “Parse with yq (require yq v4+); fall back to python if needed,” but the pseudocode implements no Python fallback. This is a false implementation note and will mislead execution/review if `yq` is absent.
- Plan §Risks says the macOS `sed -i` risk is mitigated because the “Factory skill uses `find -exec sed -i.bak` and removes `.bak` files explicitly.” The actual Factory skill pseudocode step 6 uses `sed -i "s/<CLIENT_SHORT_NAME>/<short_name>/g"` and T5 says to use that pseudocode. The stated mitigation is not present.
- `scripts/review/results/2026-05-20-plan-2746-codex.md` exists, but its content is “DEFERRED — Codex cross-review not run” and says T2 adversarial review is incomplete. The plan’s “Review artifacts” header presents `...-codex.md` as an artifact path, but the artifact is not a review. This must not be treated as satisfying the T2 review gate.

