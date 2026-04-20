# Prospect Demo Intake

Ingress path for turning prospect-supplied vessel/structure/environment data into
a branded GTM demo report within a 48-hour SLA.

## Workflow

1. A prospect sends their vessel + structure + project conditions (email,
   LinkedIn, form).
2. Copy `prospect-template.yaml` to `docs/gtm/intake/received/YYYY-MM-DD-<company>.yaml`
   and fill in the fields. The schema (`prospect-schema.json`) is the contract.
3. Run the adapter:

   ```bash
   uv run python -m scripts.gtm.prospect_adapter <path-to-filled-yaml>
   # or with CLI flags:
   uv run python scripts/gtm/prospect_adapter.py <path-to-filled-yaml> --demo 5 --dry-run
   ```

4. The adapter will validate the YAML against `prospect-schema.json`, materialize
   the demo inputs, run the chosen demo (`demo_01`..`demo_05`), and emit a
   client-branded HTML + PDF report.
5. Delivery is dual-channel: email attachment (primary) AND a gated private URL
   on `aceengineer-website` (secondary, unless `output.publish_private_url: false`).

## Files

| File | Purpose |
|---|---|
| `prospect-schema.json` | Executable draft-07 JSON Schema; source of truth for valid intake. |
| `prospect-template.yaml` | Starter YAML with every field + contract comments. |
| `canonical-vessels/` | Pre-staged class-typical vessel YAMLs for when prospect data is incomplete. Values are class-derived from public sources with citations pinned in each file's header. NOT vessel-specific. |
| `IMPLEMENTATION-STATUS.md` | Current scaffold vs. not-done inventory. Read before claiming #2346 done. |

## Status

This intake directory is the SCAFFOLD stage of issue #2346. See
`IMPLEMENTATION-STATUS.md` for what's landed and what's deferred.
