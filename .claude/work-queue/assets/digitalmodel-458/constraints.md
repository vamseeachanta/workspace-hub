# Constraints: WRK-1381

- Must satisfy `WRK-1381` acceptance criteria, especially `>= 10` traced GZ curves.
- Must preserve source traceability for each curve condition.
- Must write failing tests before fixture/schema expansion.
- Must avoid relying on source assets not present in the current workspace unless they are
  surfaced during later stages.
- Must keep issue `#458` synchronized as the human-review thread.
- Claim/activation cannot proceed until Stage 5 and Stage 7 gate evidence exists.
