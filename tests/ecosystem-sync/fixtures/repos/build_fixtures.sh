#!/usr/bin/env bash
# Build small git repos for signal-detector tests; never delete caller data.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
OUTPUT="$SCRIPT_DIR"
if [[ $# != 0 ]]; then
    if [[ $# != 2 || "$1" != --output-dir || -z "$2" ]]; then
        echo "usage: build_fixtures.sh [--output-dir DIRECTORY]" >&2
        exit 1
    fi
    OUTPUT="$2"
fi

# Fixture commands must not inherit bindings, identities or templates from a caller.
while IFS= read -r variable; do
    unset "$variable"
done < <(git rev-parse --local-env-vars)
unset GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS GIT_TEMPLATE_DIR
unset GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL GIT_AUTHOR_DATE
unset GIT_COMMITTER_NAME GIT_COMMITTER_EMAIL GIT_COMMITTER_DATE
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
fixture_git() {
    command git -c init.templateDir= \
        -c commit.gpgSign=false -c tag.gpgSign=false "$@"
}
refuse() {
    echo "refusing unsafe fixture output: expected empty or complete build" >&2
    exit 1
}

[[ ! -L "$OUTPUT" ]] || refuse
mkdir -p "$OUTPUT"
OUTPUT="$(cd "$OUTPUT" && pwd -P)"
MARKER="$OUTPUT/.fixtures-complete"
BASELINE_FILE="$OUTPUT/repo-with-casestudy.baseline-sha"
if [[ -f "$MARKER" && ! -L "$MARKER" ]] && \
    [[ "$(cat "$MARKER")" == ecosystem-sync-fixtures ]]; then
    for repo in repo-with-release repo-with-casestudy repo-with-readme; do
        dir="$OUTPUT/$repo"
        [[ -d "$dir/.git" && ! -L "$dir" && ! -L "$dir/.git" ]] || refuse
        [[ "$(fixture_git -C "$dir" rev-parse --show-toplevel)" == "$dir" ]] || refuse
        fixture_git -C "$dir" rev-parse --verify HEAD >/dev/null || refuse
        [[ -f "$dir/README.md" ]] || refuse
    done
    [[ -f "$BASELINE_FILE" && ! -L "$BASELINE_FILE" ]] || refuse
    [[ "$(cat "$BASELINE_FILE")" == \
        "$(fixture_git -C "$OUTPUT/repo-with-casestudy" rev-parse HEAD^)" ]] || refuse
    echo "fixtures reused"
    exit 0
fi

# The no-argument interface allows only the builder itself beside a fresh build.
while IFS= read -r -d '' entry; do
    [[ "$entry" == "$SCRIPT_DIR/build_fixtures.sh" ]] || refuse
done < <(find "$OUTPUT" -mindepth 1 -maxdepth 1 -print0)

# Fixture 1: repo with a v1.0.0 and v1.1.0 tag
mkdir -p "$OUTPUT/repo-with-release"
cd "$OUTPUT/repo-with-release"
fixture_git init -q -b main
fixture_git config user.email fixture.invalid
fixture_git config user.name fixture
echo "# Fixture" > README.md
fixture_git add README.md && fixture_git commit -q -m "init"
fixture_git tag v1.0.0
echo "v1.1" >> README.md
fixture_git add README.md && fixture_git commit -q -m "bump"
fixture_git tag v1.1.0
# Noise tags that MUST be filtered:
fixture_git tag nightly-2026-04-20
fixture_git tag snapshot-abc
fixture_git tag pre-release-1

# Fixture 2: repo with a new case study file
mkdir -p "$OUTPUT/repo-with-casestudy/case-studies"
cd "$OUTPUT/repo-with-casestudy"
fixture_git init -q -b main
fixture_git config user.email fixture.invalid
fixture_git config user.name fixture
echo "# Fixture" > README.md
fixture_git add README.md && fixture_git commit -q -m "init"
BASELINE_SHA=$(fixture_git rev-parse HEAD)
cat > case-studies/mooring-failures.md <<'MDEOF'
# Mooring failures
Case study body here.
MDEOF
mkdir -p case-studies/_draft
cat > case-studies/_draft/wip-study.md <<'MDEOF'
# draft — ignore me
MDEOF
cat > case-studies/CASE_STUDY_TEMPLATE.md <<'MDEOF'
# Template — ignore me
MDEOF
fixture_git add case-studies/
fixture_git commit -q -m "add case study + draft + template"
echo "$BASELINE_SHA" > "$OUTPUT/repo-with-casestudy.baseline-sha"

# Fixture 3: repo with README capabilities section
mkdir -p "$OUTPUT/repo-with-readme"
cd "$OUTPUT/repo-with-readme"
fixture_git init -q -b main
fixture_git config user.email fixture.invalid
fixture_git config user.name fixture
cat > README.md <<'MDEOF'
# Fixture

## Capabilities
- thing one
- thing two

## Other
irrelevant
MDEOF
fixture_git add README.md && fixture_git commit -q -m "init"

echo ecosystem-sync-fixtures > "$MARKER"
echo "fixtures built"
