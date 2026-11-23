"""Deterministic HTML renderer for the scheduler-mutation contract."""
from __future__ import annotations

import html
from typing import Any

ISSUE_ROOT = "https://github.com/vamseeachanta/workspace-hub/issues"


def _render_operation(path: str, operation: dict[str, Any]) -> str:
    key = html.escape(f'{path}::{operation["id"]}', quote=True)
    target = html.escape(operation["target_kind"], quote=True)
    identity = html.escape(operation["scheduler_identity"], quote=True)
    binding = html.escape(operation["execution_host_binding"], quote=True)
    authorities = "".join(_render_authority(key, branch) for branch in operation["authority_branches"])
    gaps = [name for name, value in operation["transaction"].items() if not value]
    gap_text = ", ".join(f"{name}=false" for name in gaps) or "none"
    return (
        f'<section class="operation" data-operation="{key}" data-target-kind="{target}" '
        f'data-scheduler-identity="{identity}" data-execution-host-binding="{binding}">'
        f'<strong>{html.escape(operation["id"])}</strong><br>Target: {target}; '
        f'identity: {identity}; binding: {binding}<br>Authority:<ul>{authorities}</ul>'
        f'Transaction gaps: <span class="transaction-gaps" '
        f'data-transaction-for="{key}">{gap_text}</span></section>'
    )


def _render_authority(key, branch):
    mechanism = html.escape(branch["mechanism"], quote=True)
    strength = html.escape(branch["strength"], quote=True)
    authority_key = html.escape(f'{key}::{branch["id"]}', quote=True)
    label = html.escape(f'{branch["id"]}:{branch["mechanism"]}/{branch["strength"]}')
    return (f'<li data-authority="{authority_key}" data-mechanism="{mechanism}" '
            f'data-strength="{strength}">{label}</li>')


def _render_delegation(delegation: dict[str, Any]) -> str:
    terminal = delegation["terminal"]
    modes = "".join(f"<li>{_mode_label(mode)}</li>" for mode in delegation["modes"])
    return (
        '<section class="delegation"><strong>Delegate</strong><br>Immediate: '
        f'{html.escape(delegation["immediate_callee"])}<br>Terminal: '
        f'{html.escape(terminal["path"])}::{html.escape(terminal["operation"])}'
        f'<ul>{modes}</ul></section>'
    )


def _mode_label(mode):
    exit_value = html.escape(mode["exit"])
    if mode["exit"] == "swallow-3490":
        exit_value = f'<a href="{ISSUE_ROOT}/3490">swallow-3490</a>'
    prefix = html.escape(
        f'{mode["id"]}: {mode["mutation_mode"]}; args={mode["args"]}; target={mode["target"]}; exit='
    )
    return prefix + exit_value


def _render_row(surface, groups, validation):
    group = groups.get(surface.get("disposition_group"))
    issue = group["issue"]["number"] if group else None
    detail = "".join(_render_operation(surface["path"], operation)
                     for operation in surface.get("operations", []))
    if surface.get("delegation"):
        detail += _render_delegation(surface["delegation"])
    path = html.escape(surface["path"], quote=True)
    disposition = f'<a href="{ISSUE_ROOT}/{issue}">#{issue}</a>' if issue else "resolved"
    return (f'<tr data-surface="{path}"><td><code>{path}</code></td>'
            f'<td>{html.escape(surface["kind"])}</td>'
            f'<td>{html.escape(validation.statuses[surface["path"]])}</td>'
            f'<td>{detail}</td><td>{disposition}</td></tr>')


def render_html(registry, discovery, validation, digest: str) -> bytes:
    groups = {group["group_id"]: group for group in registry["disposition_groups"]}
    body = "\n".join(_render_row(surface, groups, validation)
                     for surface in sorted(registry["surfaces"], key=lambda row: row["path"]))
    document = f"""<!doctype html>
<html lang="en" data-input-digest="{digest}"><head><meta charset="utf-8">
<title>Scheduler Mutation Safety Audit</title>
<style>body{{font:16px system-ui;max-width:1200px;margin:2rem auto;padding:0 1rem}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #bbb;padding:.5rem;text-align:left}}code{{font-size:.9em}}.warning{{border-left:4px solid #b45309;padding:1rem;background:#fff7ed}}</style></head>
<body><h1>Scheduler Mutation Safety Audit</h1>
<p><strong>Input digest:</strong> <code>{digest}</code></p>
<p class="warning">Registry inclusion does not authorize live scheduler mutation.</p>
<table><thead><tr><th>Surface</th><th>Kind</th><th>Derived status</th><th>Operations</th><th>Disposition</th></tr></thead><tbody>
{body}
</tbody></table>
<h2>Limitations</h2><ul><li>Issue coordinates are validated offline; live issue state is non-authoritative.</li><li>Windows runtime behavior is source-audited on Linux and requires Windows-capable migration verification.</li><li>Branch-protection registration is outside this artifact.</li></ul>
<p>Discovered direct owners: {len(discovery.direct)}; transitive entrypoints: {len(discovery.transitive)}.</p>
</body></html>
"""
    return document.encode("utf-8")
