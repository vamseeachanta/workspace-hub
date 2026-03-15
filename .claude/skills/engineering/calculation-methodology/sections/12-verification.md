# 12 — Verification

## Purpose

Record the independent check of the calculation by a qualified person other
than the originator. Verification confirms that the method was applied
correctly, inputs are accurate, and arithmetic is free from errors.

## Schema Fields

```yaml
verification:
  checker:
    name: string
    qualification: string      # e.g., "Chartered Engineer"
    date: date
  method: enum                 # independent_calc | line_by_line | alternative_software
  scope_of_check:
    - string                   # what was checked
  findings:
    - id: string               # finding reference (e.g., "V-01")
      description: string
      severity: enum           # critical | minor | observation
      status: enum             # resolved | open
      resolution: string
  checker_statement: string    # formal verification statement
  limitations: string          # any aspects not independently checked
```

## Required Content

- Checker name and qualification (must differ from originator)
- Date of verification
- Method used for the independent check
- Formal checker statement of adequacy
- List of findings (even if empty — state "no findings")

## Quality Checklist

- [ ] Checker is not the same person as the originator
- [ ] Check method is stated (not just "checked by")
- [ ] All critical findings are resolved before document issue
- [ ] Checker statement is explicit ("I have verified..." not just a signature)
- [ ] Limitations of the check are stated (partial check acknowledged)

## Example Snippet

```yaml
verification:
  checker:
    name: "A. Johnson"
    qualification: "Chartered Engineer (MIStructE)"
    date: 2026-03-16
  method: independent_calc
  scope_of_check:
    - "Input values verified against data sheets"
    - "Burst pressure calculation independently recomputed"
    - "Collapse pressure calculation independently recomputed"
    - "Unity checks and overall status verified"
  findings:
    - id: "V-01"
      description: "Fabrication tolerance was 0.5 mm, should be 1.0 mm per data sheet"
      severity: minor
      status: resolved
      resolution: "Updated t_fab to 1.0 mm; results re-run — still passes"
  checker_statement: >
    I have independently verified the calculation methodology, input data,
    and arithmetic. All findings have been resolved. The calculation is
    technically adequate for issue.
  limitations: "Sensitivity analysis (section 10) reviewed but not re-run"
```

## Common Mistakes

- Checker is the same person as the originator (not an independent check)
- "Checked" with no record of what was actually reviewed
- Critical findings listed but not marked as resolved
- No checker statement — just a signature block
- Check performed on a previous revision and not updated after changes
