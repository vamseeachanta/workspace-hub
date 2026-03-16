---
name: git-advanced-3-git-bisect
description: 'Sub-skill of git-advanced: 3. Git Bisect (+2).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 3. Git Bisect (+2)

## 3. Git Bisect


**Basic Bisect:**
```bash
# Start bisect
git bisect start

# Mark current version as bad
git bisect bad

# Mark known good commit
git bisect good v1.0.0

# Git checks out a commit - test it
# If bad:
git bisect bad
# If good:
git bisect good

# Continue until found
# Git will show: "abc123 is the first bad commit"

# End bisect
git bisect reset
```

**Automated Bisect:**
```bash
# Create test script
cat > test-bug.sh << 'EOF'
#!/bin/bash
# Return 0 if good, non-zero if bad
npm test -- --grep "specific test"
EOF
chmod +x test-bug.sh

# Run automated bisect
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
git bisect run ./test-bug.sh

# Git will find the bad commit automatically
git bisect reset
```

**Bisect with Skip:**
```bash
# If commit can't be tested (won't build)
git bisect skip

# Skip range of commits
git bisect skip abc123..def456
```

**Bisect Log and Replay:**
```bash
# Save bisect session
git bisect log > bisect.log

# Replay session
git bisect replay bisect.log
```


## 4. Git Rerere (Reuse Recorded Resolution)


**Enable Rerere:**
```bash
# Enable globally
git config --global rerere.enabled true

# Check status
git config --get rerere.enabled
```

**Using Rerere:**
```bash
# When you resolve a conflict, git records the resolution
git merge feature-branch
# Resolve conflicts...
git add .
git commit

# Next time same conflict occurs, git auto-applies resolution
git merge another-branch
# "Resolved 'file.txt' using previous resolution."

# If auto-resolution is wrong, forget it
git rerere forget path/to/file
```

**Rerere Management:**
```bash
# View recorded resolutions
ls .git/rr-cache/

# Clean old resolutions
git rerere gc

# Show diff of recorded resolution
git rerere diff
```


## 5. Git Reflog


**Basic Reflog:**
```bash
# Show reflog
git reflog

# Show reflog with dates
git reflog --date=relative

# Show reflog for specific ref
git reflog show feature-branch

# Output
# abc123 HEAD@{0}: commit: Latest commit
# def456 HEAD@{1}: checkout: moving from main to feature
# ghi789 HEAD@{2}: commit: Previous commit
```

**Recovery with Reflog:**
```bash
# Recover deleted branch
git reflog
# Find last commit of deleted branch: abc123
git checkout -b recovered-branch abc123

# Undo hard reset
git reflog
# Find state before reset: HEAD@{2}
git reset --hard HEAD@{2}

# Recover lost stash
git fsck --unreachable | grep commit
git show <commit-hash>
git stash apply <commit-hash>

# Recover from bad rebase
git reflog
# Find pre-rebase state: HEAD@{5}
git reset --hard HEAD@{5}
```

**Reflog Expiration:**
```bash
# Check expiration settings
git config --get gc.reflogexpire  # Default: 90 days
git config --get gc.reflogexpireunreachable  # Default: 30 days

# Extend reflog retention
git config --global gc.reflogexpire 180.days
```
