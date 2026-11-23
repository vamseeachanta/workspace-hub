#!/usr/bin/env bash
# Build small git repos for signal-detector tests.
# Idempotent: rebuilds from scratch.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
rm -rf "$HERE/repo-with-release" "$HERE/repo-with-casestudy" "$HERE/repo-with-readme"

# Fixture 1: repo with a v1.0.0 and v1.1.0 tag
mkdir -p "$HERE/repo-with-release"
cd "$HERE/repo-with-release"
git init -q -b main
git config user.email test@example.com
git config user.name test
echo "# Fixture" > README.md
git add README.md && git commit -q -m "init"
git tag v1.0.0
echo "v1.1" >> README.md
git add README.md && git commit -q -m "bump"
git tag v1.1.0
# Noise tags that MUST be filtered:
git tag nightly-2026-04-20
git tag snapshot-abc
git tag pre-release-1

# Fixture 2: repo with a new case study file
mkdir -p "$HERE/repo-with-casestudy/case-studies"
cd "$HERE/repo-with-casestudy"
git init -q -b main
git config user.email test@example.com
git config user.name test
echo "# Fixture" > README.md
git add README.md && git commit -q -m "init"
BASELINE_SHA=$(git rev-parse HEAD)
cat > case-studies/mooring-failures.md <<'MDEOF'
# Mooring failures
Case study body here.
MDEOF
cat > case-studies/_draft/wip-study.md 2>/dev/null || mkdir -p case-studies/_draft
cat > case-studies/_draft/wip-study.md <<'MDEOF'
# draft — ignore me
MDEOF
cat > case-studies/CASE_STUDY_TEMPLATE.md <<'MDEOF'
# Template — ignore me
MDEOF
git add case-studies/
git commit -q -m "add case study + draft + template"
echo "$BASELINE_SHA" > "$HERE/repo-with-casestudy.baseline-sha"

# Fixture 3: repo with README capabilities section
mkdir -p "$HERE/repo-with-readme"
cd "$HERE/repo-with-readme"
git init -q -b main
git config user.email test@example.com
git config user.name test
cat > README.md <<'MDEOF'
# Fixture

## Capabilities
- thing one
- thing two

## Other
irrelevant
MDEOF
git add README.md && git commit -q -m "init"

echo "fixtures built at $HERE"
