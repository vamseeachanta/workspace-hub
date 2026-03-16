# WRK-1272 Plan — Claude

## Approach
Create `split-oversized-skill.py` and `find-oversized-skills.py` with TDD.
Batch-split 293 oversized skills across 4 tiers. Verify 0 violations via eval-skills.py.

## Verdict
APPROVE — scripts-over-LLM-judgment pattern, proven aqwa hub reference.
