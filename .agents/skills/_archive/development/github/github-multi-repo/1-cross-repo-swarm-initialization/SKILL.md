---
name: github-multi-repo-1-cross-repo-swarm-initialization
description: 'Sub-skill of github-multi-repo: 1. Cross-Repo Swarm Initialization (+4).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. Cross-Repo Swarm Initialization (+4)

## 1. Cross-Repo Swarm Initialization


```bash
# List organization repositories
REPOS=$(gh repo list org --limit 100 --json name,description,languages \
  --jq '.[] | select(.name | test("frontend|backend|shared"))')

# Get repository details
REPO_DETAILS=$(echo "$REPOS" | jq -r '.name' | while read -r repo; do
  gh api repos/org/$repo --jq '{name, default_branch, languages, topics}'
done | jq -s '.')

# Initialize swarm with repository context
npx ruv-swarm github multi-repo-init \
  --repo-details "$REPO_DETAILS" \
  --repos "org/frontend,org/backend,org/shared" \
  --topology hierarchical \
  --shared-memory \
  --sync-strategy eventual
```


## 2. Repository Discovery


```bash
# Search organization repositories
REPOS=$(gh repo list my-organization --limit 100 \
  --json name,description,languages,topics \
  --jq '.[] | select(.languages | keys | contains(["TypeScript"]))')

# Analyze repository dependencies
DEPS=$(echo "$REPOS" | jq -r '.name' | while read -r repo; do
  if gh api repos/my-organization/$repo/contents/package.json --jq '.content' 2>/dev/null; then
    gh api repos/my-organization/$repo/contents/package.json \
      --jq '.content' | base64 -d | jq '{name, dependencies, devDependencies}'
  fi
done | jq -s '.')

echo "Found $(echo "$REPOS" | jq length) TypeScript repositories"
echo "Dependencies: $DEPS"
```


## 3. Synchronized Dependency Update


```bash
# Create tracking issue
TRACKING_ISSUE=$(gh issue create \
  --repo org/main-repo \
  --title "Dependency Update: typescript@5.0.0" \
  --body "Tracking issue for updating TypeScript across all repositories" \
  --label "dependencies,tracking" \
  --json number -q .number)

# Get all repos with TypeScript
TS_REPOS=$(gh repo list org --limit 100 --json name | jq -r '.[].name' | \
  while read -r repo; do
    if gh api repos/org/$repo/contents/package.json 2>/dev/null | \
       jq -r '.content' | base64 -d | grep -q '"typescript"'; then
      echo "$repo"
    fi
  done)

# Update each repository
echo "$TS_REPOS" | while read -r repo; do
  gh repo clone org/$repo /tmp/$repo -- --depth=1
  cd /tmp/$repo

  npm install --save-dev typescript@5.0.0

  if npm test; then
    git checkout -b update-typescript-5
    git add package.json package-lock.json
    git commit -m "chore: Update TypeScript to 5.0.0

Part of #$TRACKING_ISSUE"

    git push origin HEAD
    gh pr create \
      --title "Update TypeScript to 5.0.0" \
      --body "Updates TypeScript to version 5.0.0

Tracking: #$TRACKING_ISSUE" \
      --label "dependencies"
  else
    gh issue comment $TRACKING_ISSUE \
      --body "Failed to update $repo - tests failing"
  fi
  cd -
  rm -rf /tmp/$repo
done
```


## 4. Initialize Multi-Repo Swarm


```javascript
// Initialize multi-repo swarm

// Store multi-repo state
    action: "store",
    key: "multi-repo/state",
    value: JSON.stringify({
        repositories: ["frontend", "backend", "shared"],
        topology: "hierarchical",
        syncStrategy: "eventual"
    })
})

// Orchestrate synchronized operations
    task: "Update dependencies across all TypeScript repositories",
    strategy: "parallel",
    priority: "high"
})
```


## 5. Security Patch Coordination


```bash
# Scan all repos for vulnerable dependency
VULN_REPOS=()
for repo in $(gh repo list org --limit 100 --json name -q '.[].name'); do
  if gh api repos/org/$repo/contents/package.json 2>/dev/null | \
     jq -r '.content' | base64 -d | grep -q '"lodash": "4.17.19"'; then
    VULN_REPOS+=("$repo")
  fi
done

echo "Found ${#VULN_REPOS[@]} repos with vulnerable lodash"

# Create security tracking issue
SECURITY_ISSUE=$(gh issue create \
  --repo org/security-tracking \
  --title "SECURITY: Update lodash to 4.17.21" \
  --body "Critical security update for lodash CVE-XXXX

Affected repos:
$(printf '- %s\n' "${VULN_REPOS[@]}")" \
  --label "security,critical")

# Patch each repo
for repo in "${VULN_REPOS[@]}"; do
  gh repo clone org/$repo /tmp/$repo -- --depth=1
  cd /tmp/$repo

  npm install lodash@4.17.21
  npm audit fix

  git checkout -b security-lodash-update
  git add package.json package-lock.json
  git commit -m "security: Update lodash to 4.17.21

Fixes CVE-XXXX
Tracking: $SECURITY_ISSUE"

  git push origin HEAD
  gh pr create \
    --title "SECURITY: Update lodash to 4.17.21" \
    --body "Critical security update" \
    --label "security,critical"

  cd -
  rm -rf /tmp/$repo
done
```
