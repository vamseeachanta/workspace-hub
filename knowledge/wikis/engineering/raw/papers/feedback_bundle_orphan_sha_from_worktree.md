> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-02
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_bundle_orphan_sha_from_worktree.md

---
name: Bundle orphan SHAs from inside the worktree, not the parent repo
description: `git bundle create` from the parent repo fails for unreachable orphan SHAs; bundle from inside the worktree where HEAD points at the SHA, then optionally tag+push for cross-machine durability
type: feedback
originSessionId: 73cbf578-6fb3-4436-9a95-06ed471cd8b1
---
To preserve an orphan SHA (one not reachable from any branch or tag in the parent repo), `git -C <parent> bundle create <bundle> <SHA>` fails with "Refusing to create empty bundle" — bundle's reachability traversal sees nothing.

**Workaround:** bundle from INSIDE the worktree where HEAD references that SHA: `git -C <worktree> bundle create <bundle> HEAD~5..HEAD` (or just `HEAD` with a tighter ancestor restriction). The worktree's perspective makes HEAD reachable as a ref, so traversal walks back the requested range.

Verified on 2026-05-01: `issue-2408-staging` had detached HEAD `9c1d4e67c` not on any branch in workspace-hub. Bundle from `/mnt/local-analysis/workspace-hub` failed; bundle from `/mnt/local-analysis/workspace-hub/.planning/quick/issue-2408-staging` succeeded (77KB, verified OK).

**Belt-and-suspenders durability:** also `git tag preserved/<descriptive-name> <SHA>` in the parent repo, then `git push --no-verify origin refs/tags/preserved/<descriptive-name>`. The tag pins the SHA against gc, the origin push makes it durable across machines, and the bundle becomes a redundant local backup (deletable).

**How to apply:** when surfacing or removing an orphan-SHA worktree, default to the tag-on-origin pattern unless the SHA is known load-bearing (in which case keep the bundle too). Prefix preservation tags with `preserved/` so they're discoverable: `git ls-remote origin "refs/tags/preserved/*"`.

**Recovery from the tag** (any clone):
```bash
git fetch origin "refs/tags/preserved/<name>:refs/tags/preserved/<name>"
git checkout preserved/<name>   # detached HEAD inspection
```
