"""Closed coverage and private report inventory for authority audits."""

GITHUB_SURFACES = (
    "actions", "artifacts", "caches", "comments", "commit-comments", "commits",
    "discussions", "forks", "git-trees", "issues", "lfs", "packages", "pages",
    "pulls", "release-assets", "releases", "review-comments", "reviews", "rulesets",
    "run-logs", "timeline", "wiki",
)
REQUIRED_COVERAGE = ("git", *GITHUB_SURFACES)
REQUIRED_REPORT_FILES = ("coverage.json", "findings.bin", "reachability.json")
