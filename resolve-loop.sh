#!/bin/bash
cd /tmp/wh-reconcile
MS_RE='^\.claude/state/|^\.claude/memory/|config/ai-tools/|docs/reports/provider-|machine-equality-matrix|docs/strategy/gtm/|docs/solver/queue-dashboard\.md|config/agents/claude/memory-snapshots/MEMORY\.md'
iter=0
while [ -d .git/sequencer ] && [ $iter -lt 40 ]; do
  iter=$((iter+1))
  conflicted=$(git diff --name-only --diff-filter=U)
  [ -z "$conflicted" ] && { echo "ITER$iter: no conflicts?!"; git -c core.editor=true cherry-pick --continue 2>&1 | tail -1; continue; }
  other=$(echo "$conflicted" | grep -vE "$MS_RE" || true)
  if [ -n "$other" ]; then
    echo "ITER$iter: STOP - non-machine-state conflicts need manual review:"
    echo "$other"
    git log --oneline -1 CHERRY_PICK_HEAD
    break
  fi
  echo "ITER$iter: $(echo "$conflicted" | wc -l) machine-state conflicts -> keeping origin version"
  echo "$conflicted" | xargs git checkout --ours --
  git add -A
  out=$(git -c core.editor=true cherry-pick --continue 2>&1)
  if echo "$out" | grep -q "nothing to commit"; then
    echo "ITER$iter: commit became empty -> skipping"
    git cherry-pick --skip 2>&1 | tail -1
  else
    echo "ITER$iter: continued: $(echo "$out" | grep -E ^[ | tail -1)"
  fi
done
[ -d .git/sequencer ] || echo "SEQUENCER COMPLETE"
