#!/usr/bin/env bash
# next-id.sh — REMOVED (WRK-5140)
#
# This script has been replaced by gh-next-id.sh which allocates WRK IDs
# from GitHub issue numbers. All callers must migrate.
#
# Usage:  gh-next-id.sh --title "Your WRK title"
# See:    https://github.com/vamseeachanta/workspace-hub/issues/1330

echo "ERROR: next-id.sh is removed. Use gh-next-id.sh --title <title> instead." >&2
echo "See: https://github.com/vamseeachanta/workspace-hub/issues/1330" >&2
exit 1
