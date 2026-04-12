# Claude agent-team prompt: #2225 implementation

Use this prompt as a single self-contained handoff to Claude Code for implementation.

---

We are in `/mnt/local-analysis/workspace-hub`.

You are Claude Code operating as an internal 4-role agent team in one run:
1. Planner
2. Data-Pipeline Implementer
3. Adversarial Reviewer
4. Integrator

Do not ask the user any questions.

Execution authorization:
- Issue `#2225` has been explicitly user-approved for execution.
- GitHub label `status:plan-approved` is present.
- Local marker exists: `.planning/plan-approved/2225.md`

Primary issue:
- `#2225` https://github.com/vamseeachanta/workspace-hub/issues/2225

Approved plan:
- `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md`

Review artifacts:
- `scripts/review/results/2026-04-11-plan-2225-claude.md`
- `scripts/review/results/2026-04-11-plan-2225-final.md`

Authoritative supporting docs to follow, not redefine:
- `docs/plans/2026-04-11-issue-2216-acma-codes-llm-wiki-repo-intelligence-integration.md`
- `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md`
- `docs/document-intelligence/standards-codes-provenance-reuse-contract.md`
- `data/document-index/mounted-source-registry.yaml`
- `scripts/data/document-index/config.yaml`
- `scripts/data/document-index/phase-a-index.py`
- `scripts/data/document-index/provenance.py`

Critical safety constraints:
- The repo has many unrelated dirty/untracked files.
- Do NOT touch unrelated files.
- Stage and commit ONLY the files explicitly owned by this issue.
- Never use `git add .` or broad globs.
- If you detect unavoidable conflict with unrelated dirty files, stop and report clearly.

Owned implementation paths for #2225 only:
- `data/document-index/mounted-source-registry.yaml`
- `scripts/data/document-index/config.yaml`

Optional owned path only if truly necessary and directly tied to deliverable evidence:
- a small generated report file under `docs/reports/` or `docs/document-intelligence/` is NOT owned by this issue unless absolutely necessary; prefer GitHub comment summary instead

Read-only context paths:
- `docs/plans/2026-04-11-issue-2225-acma-codes-source-registration-and-initial-indexing.md`
- `/mnt/ace/acma-codes/**`
- `data/document-index/index.jsonl`
- `data/document-index/standards-transfer-ledger.yaml`
- `scripts/review/results/2026-04-11-plan-2225-*.md`
- existing pipeline scripts under `scripts/data/document-index/`

Forbidden paths:
- `knowledge/**`
- `docs/plans/**` other than read-only context
- `tests/**`
- `.claude/**`
- `.codex/**`
- `config/**` outside owned file above
- any unrelated dirty/untracked file outside the owned paths above

Success condition:
Implement the approved #2225 plan fully and safely.

Required implementation outcomes:
1. Update `data/document-index/mounted-source-registry.yaml`
   - add source entry for `/mnt/ace/acma-codes`
   - include clear staging/dedup guidance consistent with the approved plan
2. Update `scripts/data/document-index/config.yaml`
   - add `acma_codes` source entry under `sources:`
   - add `acma_codes` to source priority appropriately
   - add/confirm exclusion patterns for obvious junk artifacts like `Thumbs.db` and `desktop.ini`
3. Perform a live inventory check of `/mnt/ace/acma-codes`
   - verify top-level families and note any material deviations from the plan
4. Run the appropriate Phase A indexing path for the new source if safe and feasible in this environment
   - if full indexing is too heavy for this run, do the smallest safe bounded run that still proves the source wiring is correct, and report exactly what was done
5. Produce an initial dedup assessment against existing corpus using current provenance/index mechanisms
   - identify likely duplicate API records vs net-new OCIMF/CSA records as far as the run allows
6. Post a GitHub implementation summary on #2225 with:
   - source registration result
   - live inventory result
   - indexing result
   - dedup result
   - any deviations or next blockers for #2226
7. Close #2225 only if the approved acceptance criteria are genuinely met

Implementation guidance:
- Prefer the smallest safe real implementation over a simulated one.
- Be honest about what was actually run versus what was only prepared.
- If full Phase A indexing is too expensive or risky, do not fake completion; report partial completion and leave the issue open.
- Keep scope tight: this issue is source registration + initial indexing/dedup only.
- Do not edit ledger entries, wiki pages, or accessibility docs in this issue.

Required verification before commit:
- confirm new mounted source entry exists
- confirm new config source entry exists
- confirm junk exclusion rules cover obvious system artifacts
- confirm live `/mnt/ace/acma-codes` inspection was performed and summarized
- confirm any indexing command actually executed is reported accurately
- confirm no forbidden paths were modified

Git discipline:
- Stage only the owned paths explicitly by path.
- Commit message:
  - `feat(acma-codes): register source and configure initial indexing for #2225`
- After commit, push to `origin main`.

GitHub closeout:
- Post a concise comment on #2225 summarizing:
  - files changed
  - live inventory findings
  - indexing/dedup outcome
  - whether issue is complete or what remains
- Close the issue only if it is fully complete and verified.

Final return format in the Claude session:
1. What changed
2. Verification performed
3. Exact files committed
4. GitHub comment URL
5. Whether issue was closed
6. Residual risks or blockers
