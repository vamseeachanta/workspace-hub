# Execution Entry-Point Inventory (#2728)

Enumeration command: `python - <<'PY' ... Path('/mnt/local-analysis').glob('*') ... PY` plus targeted repo documentation review. Client/project child paths are intentionally redacted.

| Repo | Evidence status | Entry-point classes | Notes |
|---|---|---|---|
| workspace-hub | available | plans, review fanout, legal scan, pytest architecture fixtures, governance docs | control-plane execution contracts live here |
| digitalmodel | available as tier-1 role by docs/memory | engineering scripts, OrcaFlex/OrcaWave workflows, report generation | implementation details owned by repo |
| assetutilities | available as tier-1 role by docs/memory | shared utilities, Python tooling | owner repo policy applies |
| worldenergydata | available as tier-1 role by docs/memory | public/API ingestion and data processing | public collection source owner |
| llm-wiki | available role; live path requires registry confirmation | public knowledge pages, possible public chatbot corpus | raw/private staging is not assumed public |
| aceengineer-website | available role; live path requires registry confirmation | public website publication and demos | sanitized public outputs only |
| aceengineer-strategy | available role; live path requires registry confirmation | GTM/prospect strategy records | generic collateral belongs elsewhere |
| assethold | available as tier-1 role by memory | asset/repo data as owner policy defines | not expanded in this issue |
| client/project roots | unavailable/redacted | private execution inputs and deliverables | no tracked child paths; registry required |

Unavailable means no authoritative registry-backed local path was committed by this issue. Follow-up registry work remains blocked on #2731/#2732.
