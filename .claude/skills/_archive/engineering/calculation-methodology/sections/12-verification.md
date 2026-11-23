# 12 — Verification

## Purpose

Record the independent check of the calculation by a qualified person other
than the originator. Verification confirms that the method was applied
correctly, inputs are accurate, and arithmetic is free from errors.

## Schema Fields

```yaml
verification:
  checker: string             # checker name (scalar, not nested object)
  date: string                # date of verification (ISO 8601)
  method: string              # check method (e.g., "independent_calc", "line_by_line")
  findings: string            # optional — summary of findings (scalar string)
  status: string              # optional — e.g., "approved", "approved with comments"
```

> **Renderer Mapping Note:** The methodology recommends a nested `checker`
> object with `name`, `qualification`, `date`, structured `findings[]` with
> `id/description/severity/status/resolution`, `scope_of_check[]`,
> `checker_statement`, and `limitations`. The renderer uses flat scalar fields:
> `checker` (string name), `date`, `method` are required; `findings` and
> `status` are optional scalars. Encode qualification in the `checker` string,
> and consolidate finding details into the `findings` string.

## Required Content

- Checker name and qualification (encode both in `checker` string)
- Date of verification
- Method used for the independent check
- Findings summary (even if "No findings")

## Quality Checklist

- [ ] `checker` is a scalar string (not a nested object)
- [ ] `findings` is a scalar string (not a list of structured objects)
- [ ] Checker is not the same person as the originator
- [ ] All critical findings are noted as resolved in the `findings` text
- [ ] Check method is stated (not just "checked by")

## Example Snippet

```yaml
verification:
  checker: "A. Johnson, Chartered Engineer (MIStructE)"
  date: "2026-03-16"
  method: "independent_calc"
  findings: >
    V-01 (minor, resolved): Fabrication tolerance was 0.5 mm, should be
    1.0 mm per data sheet. Updated t_fab to 1.0 mm; results re-run — still
    passes. No other findings.
  status: "approved"
```

## Common Mistakes

- Using nested `checker: {name: ..., qualification: ..., date: ...}`
  (renderer expects `checker` as a scalar string)
- Using `findings` as a list of structured dicts (renderer expects a scalar string)
- Checker is the same person as the originator (not an independent check)
- "Checked" with no record of what was actually reviewed
- Critical findings listed but not marked as resolved
