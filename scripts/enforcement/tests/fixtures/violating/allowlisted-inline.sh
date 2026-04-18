#!/usr/bin/env bash
# Fixture: exactly one potentially-triggering line, allowlisted inline.
# MUST NOT trigger check-no-abs-paths because the marker overrides it.
readme_url="https://example.com/see /home/docs/readme"  # abs-path-allowed
echo "$readme_url"
