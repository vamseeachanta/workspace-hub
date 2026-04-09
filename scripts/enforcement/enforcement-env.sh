#!/usr/bin/env bash
# enforcement-env.sh — Environment variables controlling enforcement strictness
# Issues: #1876, #2017, #2027
#
# This file is git-tracked (unlike .git/hooks/enforcement-env which is local-only).
# Source it from any hook or script that needs enforcement mode awareness.
#
# Install to git hooks:
#   cp scripts/enforcement/enforcement-env.sh .git/hooks/enforcement-env
#
# Override locally:
#   export FORCE_PLAN_GATE_STRICT=0   # revert plan gate to advisory
#   export REVIEW_GATE_STRICT=0       # revert review gate to advisory
#   export DISABLE_ENFORCEMENT=1      # disable all enforcement

# Plan-approval gate: 1 = block commits without plan approval, 0 = warn only
export FORCE_PLAN_GATE_STRICT="${FORCE_PLAN_GATE_STRICT:-1}"

# Review gate: 1 = block pushes without review, 0 = warn only
export REVIEW_GATE_STRICT="${REVIEW_GATE_STRICT:-1}"

# Master kill switch: set to 1 to disable all enforcement gates
export DISABLE_ENFORCEMENT="${DISABLE_ENFORCEMENT:-0}"
