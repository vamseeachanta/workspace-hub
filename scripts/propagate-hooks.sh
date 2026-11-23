#!/usr/bin/env bash
# DEPRECATED: Use propagate-ecosystem.sh instead.
# This wrapper redirects to the unified propagation script.
echo "NOTE: propagate-hooks.sh is deprecated. Use propagate-ecosystem.sh instead."
echo ""
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/propagate-ecosystem.sh" --hooks-only "$@"
