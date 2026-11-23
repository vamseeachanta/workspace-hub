---
name: github-repo-architect-4-cross-repository-synchronization
description: 'Sub-skill of github-repo-architect: 4. Cross-Repository Synchronization
  (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 4. Cross-Repository Synchronization (+1)

## 4. Cross-Repository Synchronization


```bash
# List organization repositories
REPOS=$(gh repo list org --limit 100 --json name --jq '.[].name')

# Update common files across repositories
for repo in $REPOS; do
  echo "Updating $repo..."

  # Clone repo
  gh repo clone org/$repo /tmp/$repo -- --depth=1

*See sub-skills for full details.*

## 5. Batch Architecture Operations


```javascript
[Single Message - Repository Architecture Review]:
    // Initialize comprehensive architecture swarm

    // Analyze current structures
    Bash("ls -la packages/ruv-swarm/")
    Read("packages/ruv-swarm/package.json")

    // Search for patterns
    Bash(`gh search repos "language:javascript monorepo" --limit 5 --json fullName,stargazersCount`)

*See sub-skills for full details.*
