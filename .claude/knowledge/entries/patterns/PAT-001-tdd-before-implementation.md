---
id: PAT-001
type: pattern
title: "TDD before implementation"
category: testing
tags: [tdd, testing, red-green-refactor, quality]
repos: [workspace-hub]
confidence: 0.9
created: "2026-01-30"
last_validated: "2026-01-30"
source_type: manual
related: [ADR-001]
status: active
access_count: 0
---

# TDD Before Implementation

## Problem

Implementation without tests leads to untested edge cases, unclear requirements, and code that is difficult to refactor. Tests written after implementation tend to test the implementation rather than the behavior.

## Solution

Follow the Red-Green-Refactor cycle:
1. **Red**: Write a failing test that defines the expected behavior
2. **Green**: Write the minimal code to make the test pass
3. **Refactor**: Improve code while keeping tests green

Tests are the specification. When a test fails, the implementation is wrong (not the test). Only modify tests when requirements change.

## When to Use

- All new features and bug fixes
- Any public API changes
- Integration points with external systems
- Critical business logic

## Examples

- Writing a new bash script: define expected output/behavior in test first
- Adding a new skill: define SKILL.md contract, write validation test, then implement
- Fixing a bug: write test that reproduces the bug, then fix it
