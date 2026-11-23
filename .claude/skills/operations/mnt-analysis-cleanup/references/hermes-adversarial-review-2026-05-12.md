ADVERSARIAL CROSS-REVIEW

I inspected the live skill, the referenced Hermes skill path, `.gitignore`, and current Hermes CLI behavior. This is not safe enough for real disk-pressure cleanup without fixes.

1. Hermes coordination correctness

Severity: MAJOR

Evidence:
- Skill says: “Hermes creates a fresh dated dir per run — it does NOT poll old dated dirs.”
- Skill says: “Old `codex-burn-YYYYMMDD/` dirs are therefore post-run vestigial.”
- Referenced orchestration file says: `git worktree add -b codex/burn-YYYYMMDD-issue-NNNN /mnt/local-analysis/codex-burn-YYYYMMDD/issue-NNNN origin/main`
- Live referenced file at `/home/vamsee/.hermes/skills/autonomous-ai-agents/agent-cli-delegation-operations/references/codex-background-burn-orchestration.md` begins with: “Archived Skill: `codex-background-burn-orchestration`” and “Archived into: `/home/vamsee/.hermes/skills/.archive/...`”
- Case study itself says: “#2666 ... assetutilities + worldenergydata branches still unmerged”

Defect:
The skill overstates “old dirs are vestigial.” A dated codex-burn dir can still matter even if Hermes will not poll it again:
- live or recently active sessions may still reference the exact worktree path;
- GitHub issue comments may reference the worktree path as evidence;
- branch may be pushed but unmerged, open, or not represented in canonical nested repo;
- `git worktree list` in the canonical repo may still have metadata for the worktree;
- shared clone/worktree object dependencies may matter if delete order is wrong;
- logs/prompts/monitoring evidence may be the only audit trail for follow-up issues;
- a current burn can start after the initial `pgrep` check.

Also, the referenced Hermes path is not a stable operational contract. It points to an archived skill wrapper on this machine. The active skill content may also exist elsewhere, but this cleanup skill hardcodes one fragile path as if canonical.

Fix:
Replace the blanket “old dirs are therefore post-run vestigial” with:

“Old dated dirs are candidates only. They are deletable only after all of these are true:
1. no running process has cwd or open files under the dir: `lsof +D <dir>` or cheaper targeted `fuser -vm <dir>` plus `pgrep -af 'codex|hermes|tui_gateway|slash_worker'`;
2. no Hermes cron/job/session/goal references the dir: search goals, cron definitions, sessions, logs;
3. no canonical repo still lists it in `git worktree list --porcelain`;
4. all branches named by the bundles exist on origin and have been compared;
5. any GitHub issues referenced by prompts/logs are closed or explicitly documented as deferred;
6. archive is verified before deletion.”

Add recovery/audit cases:
- “If issue comments reference this path and issue is open, Tier 3 leave/defer unless archive includes the full evidence bundle and issue gets a comment with archive path.”
- “If `git worktree list` still references the path, use `git worktree remove/prune` from the owning repo; do not raw-delete first.”
- “If branch is unmerged or issue still open, do not call it vestigial; classify as evidence-preserving archive/defer.”

2. Iron Law completeness

Severity: MAJOR

Evidence:
- Skill says filter derived artifacts: `__pycache__`, `.venv`, `node_modules`, `egg-info`, `.benchmarks`, `test_output`, `results/Data`, `results/Plot`, `logs/`, `.hypothesis`, `.ruff_cache`.
- Skill says: “Archive non-derived unique content — any item flagged unique-to-bundle that's NOT a derived artifact...”
- Case study says archived: `results/*`, `test_output/*`, `marine_safety.db`.

Defect A — missing derived patterns:
The filter is too short for real repo cleanup. It will either produce noisy false positives or tempt agents to broaden filters manually without review.

Missing common derived/cache patterns:
- Python: `.pytest_cache/`, `.mypy_cache/`, `.pyre/`, `.nox/`, `.tox/`, `.coverage`, `coverage.xml`, `htmlcov/`, `build/`, `dist/`, `*.egg-info/`, `.eggs/`, `.uv-cache/`, `.ipynb_checkpoints/`
- JS/web: `.next/`, `.nuxt/`, `.turbo/`, `.vite/`, `.parcel-cache/`, `coverage/`, `playwright-report/`, `test-results/`, `dist/`, `build/`
- General: `*.log`, `*.tmp`, `tmp/`, `temp/`, `junit.xml`, `*.pyc`, `*.pyo`, `.DS_Store`
- Rust/Go/etc if applicable: `target/`, `bin/`, compiled artifacts

Defect B — dangerous items already in the “derived” filter:
- `logs/` is not always disposable. In this workflow, logs are audit evidence and sometimes the only record of process output.
- `test_output` may contain reproduction artifacts, failure captures, generated fixtures, screenshots, downloaded samples, or acceptance evidence.
- `results/Data` and `results/Plot` may be generated, but in engineering/data repos they can contain valuable derived evidence, validation outputs, or manually curated result snapshots.
- `.venv` is usually derived, but can contain editable installs, generated scripts, local package snapshots, or accidental user-created notebooks/files. It should be excluded from code diff, not blindly ignored for archival if deletion is high risk.

Fix:
Separate three categories instead of one blunt filter:

A. Always disposable after diff:
`__pycache__/`, `*.pyc`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.hypothesis/`, `.tox/`, `.nox/`, `.coverage`, `htmlcov/`, `.DS_Store`, `node_modules/`, `.next/cache/`, `.turbo/`, `.vite/`, `.parcel-cache/`.

B. Derived but evidence-bearing — summarize and archive manifest, not blindly discard:
`logs/`, `test_output/`, `test-results/`, `playwright-report/`, `results/`, `coverage.xml`, `junit.xml`, `*.db`, `*.sqlite*`.

C. Never filter without size/type inspection:
`data/`, `results/Data/`, `downloads/`, `cache/`, `*.db`, `*.sqlite`, `*.parquet`, `*.csv`, `*.xlsx`, notebooks.

Add executable file classification:
`find <residue> -maxdepth 3 -type f -printf '%p|%s|%TY-%Tm-%Td %TH:%TM\n'`
and for DBs:
`file <db>; sqlite3 <db> '.tables'` when available.

3. Failure modes not covered

Severity: MAJOR

Evidence:
- Execute order says: “Archive”, “Verify archive integrity (`tar tzf <archive> | wc -l`)”, “Delete sources”.
- Hermes coordination says: “Always check `pgrep -af hermes` before deletion...”
- Disk-pressure trigger says: `df -h /mnt/local-analysis | awk '/sdc1|local-analysis/ ...'`

Defects:
- Disk-full mid-archive not handled. A truncated `.tar.gz` can still exist. `tar tzf | wc -l` only proves listability, not completeness against an expected manifest.
- No expected manifest is produced before archive, so archive verification is weak.
- No atomic archive path. Writing directly to final archive path means partial archives look official if interrupted.
- No checksum. No byte/file count comparison against pre-archive manifest.
- No partial-delete rollback or deletion log.
- No race guard. `pgrep` at proposal time does not protect against a burn launched between approval and delete.
- No open-file/cwd check. A process may not have “hermes” in argv but still use the directory.
- `du -sh` with timeout can under-report or silently skip permission/io failures.
- `df -h ... awk '/sdc1|local-analysis/'` is brittle: device names change; human-readable `df -h` parsing is worse than `df -P`.

Fix:
Add mandatory two-phase execution:

Pre-delete lock:
- create lock dir: `/mnt/local-analysis/.cleanup-lock`
- if exists, stop and inspect owner file.
- write PID, date, hostname, target dirs.

Pre-archive manifest:
`find <target> -xdev -printf '%y\t%s\t%T@\t%p\n' | sort > <archive>.manifest.tsv`

Archive atomically:
- write to `archives/.tmp/<name>.tar.gz.partial`
- require free space estimate before archive: source selected bytes + 10% overhead
- after tar: `tar tzf`, compare entry count to manifest where applicable, write `sha256sum`
- move partial to final only after verification.

Race check immediately before delete:
- repeat `pgrep`, `hermes cron list`, goal/session/path search;
- run `lsof +D <target>` or at minimum `fuser -vm <target>`;
- run `git worktree list --porcelain` from owning repos;
- abort if any new reference appears.

Delete safely:
- prefer `mv <target> /mnt/local-analysis/.cleanup-trash/<timestamp>/` first;
- verify post-move system behavior and disk state;
- only then `rm -rf` the trash, or keep for one cycle if space allows.
Under severe disk pressure, document that trash-stage may be skipped only after verified archive.

Use `df -P /mnt/local-analysis` not `df -h` for machine parsing.

4. Verifiability of safeguards

Severity: MAJOR

Safeguard A: “Confirm content is on origin”
Evidence:
- “fetch the relevant branch and `diff -rq` the working tree against the branch tip.”

Assessment:
Partly executable, but underspecified. “Relevant branch” is trust-the-agent unless branch derivation is explicit. Also `diff -rq` against `git archive FETCH_HEAD` misses untracked-vs-ignored nuance and submodules/symlinks/mode changes.

Fix:
Require:
- identify current branch: `git -C <bundle> branch --show-current` or parse `.git`/worktree metadata;
- verify upstream: `git -C <canonical> ls-remote --heads origin <branch>`;
- compare tracked files: `git -C <bundle> status --porcelain=v1 --untracked-files=all`;
- compare archive to worktree with manifest;
- explicitly list ignored files: `git -C <bundle> status --ignored --short`.

Safeguard B: “Archive non-derived unique content”
Evidence:
- “any item flagged unique-to-bundle that's NOT a derived artifact ... goes into the cleanup tarball”

Assessment:
Trust-the-agent. No command defines how unique content is selected, where manifest lives, or how archive inclusion is proven.

Fix:
Generate residue list:
`diff -rq <branch-tree> <bundle> | tee <residue>.txt`
Then create an explicit include file for archive:
`archive-includes.txt`
Then verify:
`tar tzf <archive> | sort > archive-list.txt`
and compare expected includes to archive list.

Safeguard C: “No rm -rf until diff clean OR residue captured”
Evidence:
- “No `rm -rf` until the diff is clean OR the diff residue is captured in the archive.”

Assessment:
Good policy, weak enforcement. The skill does not require an actual pass/fail gate artifact.

Fix:
Require a `cleanup-verification.json` with:
- target path
- branch compared
- diff command
- residue count
- archive path
- archive sha256
- delete_allowed boolean
- approver/timestamp

Safeguard D: “Cross-check Hermes active state”
Evidence:
- “`pgrep -af hermes`, `hermes cron list`, `~/.hermes/goals/*.json` for recent goals naming the dated dir”

Assessment:
Partly executable, incomplete. `pgrep -af hermes` is noisy and misses `codex`, `tmux`, `slash_worker`, `tui_gateway`, shells, or non-Hermes processes with cwd/open files under the dir. “recent goals” is ambiguous. `hermes sessions list` only lists titles/previews, not full path references.

Fix:
Use concrete checks:
- `pgrep -af 'hermes|codex|tui_gateway|slash_worker|tmux'`
- `grep -R --fixed-strings "$target" ~/.hermes/goals ~/.hermes/sessions ~/.hermes/logs 2>/dev/null`
- `hermes cron list --all`
- `lsof +D "$target"` or `fuser -vm "$target"`

Safeguard E: “Present to user via AskUserQuestion”
Evidence:
- “Present to user via `AskUserQuestion`”
- “One question per tier... Never auto-execute without per-tier approval.”

Assessment:
Tooling mismatch. In this Hermes environment the user-question tool is `clarify`, not `AskUserQuestion`. This is not just cosmetic: future agents may quote the skill and fail to perform the intended approval gate.

Fix:
Replace with:
“Use the available user-interaction mechanism (`clarify` in Hermes CLI, or explicit terminal response prompt in non-interactive mode). If no user-interaction tool is available, stop after writing the proposal; do not delete.”

5. Naming traps and `.gitignore` traps

Severity: MAJOR

Evidence:
- Skill name: `mnt-analysis-cleanup`
- Description only says `/mnt/local-analysis/`
- Related skill entry: `coordination/issue-planning-mode (when cleanup surfaces issues for #2666-style follow-up)`
- Live `skill_view` parsed that related skill as truncated: `coordination/issue-planning-mode (when cleanup surfaces issues for`
- Skill says: “Archive target: `workspace-hub/docs/sessions/archives/YYYY-MM-DD-<topic>.tar.gz`.”
- Skill says: “docs/sessions/archives/ is currently not gitignored”
- `.gitignore` in workspace-hub contains `*.tar.gz` at lines 330-332. That means the archive is globally ignored regardless of directory unless force-added.

Defects:
- Name is too narrow and awkward. Future agents may search “local-analysis cleanup”, “disk pressure”, “orphan worktree cleanup”, “codex burn cleanup”, “mnt cleanup”, “workspace sibling cleanup”. `mnt-analysis-cleanup` may be missed.
- YAML `related_skills` has an unquoted `#2666`; YAML treats `#` as comment. The live parsed skill confirms truncation. That is a real frontmatter defect.
- Archive commit instruction is wrong. `*.tar.gz` is ignored in repo root `.gitignore`, so “docs/sessions/archives/ is currently not gitignored” is misleading. Directory may not be explicitly ignored, but archive files are.
- `related_skills` points to `operations/devops/remote-desktop-headless-ubuntu`, which was not in the available skill list I saw. Broken/unknown related skill reduces discoverability and trust.
- `AskUserQuestion` naming is probably inherited from another agent ecosystem, not Hermes.

Fix:
- Rename or add aliases/frontmatter tags:
  - name maybe `local-analysis-disk-cleanup`
  - tags: `disk-cleanup`, `local-analysis`, `codex-burn`, `orphan-worktrees`, `outer-clones`, `agent-logs`
  - when_to_use should include “disk pressure”, “orphan worktree”, “codex-burn”, “/mnt/local-analysis”, “cleanup sibling repos”.
- Quote related skill entries or remove comments:
  `- "coordination/issue-planning-mode"`
- Replace broken related skill with existing concrete skills:
  `workspace-hub/repo-sync`, `workspace-hub/worktree-branch-sync-hygiene`, `development/artifact-commit-verification`, `coordination/issue-planning-mode`.
- Fix archive commit section:
  “Archives match global `*.tar.gz` ignore. Do not assume they are tracked. Either `git add -f docs/sessions/archives/<file>.tar.gz` after size/security review, or store only manifest/checksum in git and leave archive local.”
- Add secret scan before committing archives:
  `git secrets`, `gitleaks`, or at minimum `grep -R` for token/key patterns and `tar tzf` manifest review.

6. Case-study honesty

Severity: MINOR, bordering MAJOR if used as justification for risky behavior

Evidence:
- Case study says: “Iron Law verification claim: saved 1.1 MB.”
- Case study says: “Total archive cost: 1.1 MB. Total bytes-at-risk-of-loss if Iron Law were skipped: 1.1 MB. Cost-benefit of the law is overwhelming.”
- Case study also says: `marine_safety.db` “could be runtime cache”
- Case study says: `results/` and `test_output/` were “test-run outputs; small, archived to be safe.”

Defect:
“Saved 1.1 MB” is rhetorically stronger than the evidence supports. The actual finding appears to be “1.1 MB of unique-to-worktree residue was preserved,” not “1.1 MB of useful work was saved.” If `marine_safety.db`, `results/`, and `test_output/` are regenerable runtime/test artifacts, the skill is using a vanity metric as proof of safety.

That said, the case study is still useful: it proves the diff/archive step catches residue. It does not prove the residue was valuable.

Fix:
Rewrite:
- “Iron Law preserved 1.1 MB of unique residue pending classification.”
- “This may have been regenerable, but preserving it was the correct default because the cleanup pass could not prove that before deletion.”
- Avoid “bytes-at-risk-of-loss” unless you mean “bytes not present on origin and not covered by derived filters.”
- Add a table:
  - path
  - size
  - classification
  - why archived
  - later disposition if known
  - confidence useful/regenerable/unknown

Additional high-risk defects outside the six buckets

Severity: MAJOR

Evidence:
- “Commit the handoff. If an archive was created, also commit it...”
- Archive includes logs/prompts/monitoring evidence.

Defect:
Committing raw archives of prompts/logs can leak:
- secrets accidentally printed in logs,
- private prospect/client names,
- full process snapshots,
- local paths,
- provider/account metadata,
- downloaded data with unknown licensing.

Fix:
Before any archive commit:
- create manifest and size report;
- run secret scan against extracted archive contents;
- manually classify privacy/licensing;
- default to committing manifest/checksum only, not archive, unless archive is small and reviewed.
Given `.gitignore` ignores `*.tar.gz`, this skill should not casually recommend `git add -f`.

Severity: MINOR

Evidence:
- “What NOT to clean: `.pnpm-store/`, `.cache/`, `.cargo/`...”
- Classification says “system | dotfile, pnpm/.cargo/.npm cache...”

Defect:
“dotfile == system” is too broad. Dotdirs can include `.worktrees`, `.agent-state`, `.codex`, `.claude`, `.venv`, `.local`, `.config`, or manually created hidden dirs. Some are safe, some are not.

Fix:
Change signal from “dotfile” to explicit allowlist:
`.pnpm-store/`, `.Trash-*`, maybe package-manager caches after owner/process check. Unknown dotdirs are Tier 3 until classified.

Severity: MINOR

Evidence:
- “empty coordination meta-dir” safe if `find <dir> -maxdepth 2 -mindepth 1 | head -1` returns nothing.

Defect:
`maxdepth 2` is not “empty”; it can miss deeper content if parent has only deeper mount/bind/symlink weirdness. Also `head` can hide permission errors.

Fix:
Use:
`find "$dir" -xdev -mindepth 1 -print -quit`
and fail closed on permission errors.

Required patch set before approval

1. Remove/soften “old dirs are therefore vestigial.”
2. Add race-safe pre-delete checks: lock, lsof/fuser, repeated Hermes/session/goal/path search, git worktree metadata check.
3. Replace `AskUserQuestion` with Hermes-valid `clarify` / explicit stop-if-no-interaction.
4. Fix YAML `related_skills` quoting; remove unquoted `#2666`.
5. Fix archive tracking claim: `*.tar.gz` is ignored; require `git add -f` only after secret/privacy review or commit manifest only.
6. Split derived filters into disposable vs evidence-bearing vs inspect-first.
7. Add archive manifest/checksum/atomic partial-file workflow.
8. Rewrite case-study “saved 1.1 MB” to “preserved 1.1 MB of unique residue pending classification.”

VERDICT: REJECT
