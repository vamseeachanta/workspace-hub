# Repo/Data Location Contract Planning

Use this reference when planning issues that define where repos, raw data, private/client corpora, extracted artifacts, and generated reports should live across `/mnt/local-analysis`, `/mnt/ace`, and compatibility aliases.

## Core planning boundary

- Treat repo placement decisions as governance/contract work until a reviewed child plan explicitly authorizes movement.
- Do not move, delete, rename, rsync, or reclassify files during the planning issue itself.
- Separate these concerns explicitly:
  - active git checkout placement
  - bulk/raw/source-data placement
  - readable raw or extracted staging
  - private/client wiki placement
  - public `llm-wiki` promotion rules
  - generated report/deliverable residency

## Adjacent sibling checkout model

When `/mnt/local-analysis/workspace-hub` is the control-plane repo, prefer and plan around sibling checkouts:

- `/mnt/local-analysis/workspace-hub` — orchestration/control-plane repo: plans, governance docs, skills, scripts, cross-repo issue routing, review artifacts, and reports.
- `/mnt/local-analysis/<tier-1-repo>` — active implementation repo checkout when present on that machine.
- `workspace-hub/<repo>` nested checkouts — non-canonical unless a plan explicitly authorizes a temporary migration/shim.

A plan must not assume every tier-1 repo is checked out on the current machine. It should enumerate the live sibling checkout set and phrase coverage as observed, not universal.

## Required live evidence before drafting

Capture compact, empirical evidence in the Resource Intelligence Summary:

```bash
printf '/mnt/local-analysis first-level directories:\n'
find /mnt/local-analysis -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort

printf '\nGit repos detected at maxdepth 2:\n'
find /mnt/local-analysis -maxdepth 2 -name .git -type d -printf '%h\n' | sort

printf '\nAlias state:\n'
realpath -m ../../ace-data
ls -ld /mnt/ace-data /mnt/ace 2>/dev/null || true
```

If the issue cites exact paths, verify each named path exists/missing and classify each one as `canonical`, `alias`, `deprecated`, `planned`, or `defer`.

## Plan acceptance criteria to include

- Every named path has an explicit classification: stay, move, alias, archive, planned, or defer.
- `/mnt/local-analysis` active sibling checkouts are distinguished from `/mnt/ace` raw/source/bulk data.
- `/mnt/ace-data` alias handling is decided as supported compatibility wording or retired wording.
- Nested `workspace-hub/<repo>` checkout references are inventoried and corrected or marked legacy.
- Private/client source data cannot route directly to public `llm-wiki`; promotion requires a sanitization/publication gate.
- Immediate move candidates are represented as reviewable transactions with manifest/checksum/rollback gates; no movement occurs inline.
- Tests/checkers are planned before implementation to prevent future drift in path classification.

## Common pitfalls

- Do not turn a cleanup observation such as “only `workspace-hub` remains” or “only three sibling repos are currently present” into a universal placement claim. Cleanup changes live inventory, not the durable repo-location contract. The plan should define expected placement rules while accurately reporting the current machine’s partial checkout coverage.
- Treat user-reported cleanup state as an assertion to verify, not as permission to mutate the filesystem. If a live probe contradicts the reported state (for example sibling checkouts still exist under `/mnt/local-analysis`), record the discrepancy in the plan or closeout, keep the plan future-tense, and do **not** delete/move the remaining directories unless a reviewed/approved transaction plan explicitly authorizes that action.
- Preserve tier-1 sibling checkouts as potentially legitimate working copies until role/remote/dirty state is classified. Repo-location plans should decide the contract and any future manifest/checksum/rollback transaction; they should not opportunistically “finish cleanup” during planning.
