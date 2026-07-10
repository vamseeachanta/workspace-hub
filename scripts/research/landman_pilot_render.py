"""Deterministic YAML and human-readable HTML for the Landman pilot."""

from __future__ import annotations

import html
import json

import yaml

from scripts.research.landman_pilot_decision import build_decision


def html_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(value)}</th>" for value in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def html_list(values: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{value}</li>" for value in values) + "</ul>"


def _score_sections(decision: dict) -> list[tuple[str, str]]:
    rows = [
        [
            html.escape(item["jurisdiction"]),
            html.escape(item["display_score"]),
            str(item["eligible"]),
            html.escape(", ".join(item["failed_gates"]) or "none"),
        ]
        for item in decision["candidates"]
    ]
    alternatives = [
        html.escape(
            f"{item['jurisdiction']}: {item['display_score']} "
            f"({', '.join(item['failed_gates']) or 'eligible'})"
        )
        for item in decision["candidates"]
    ]
    scorecard = html_table(
        ["Jurisdiction", "Raw score", "Eligible", "Failed gates"], rows
    )
    return [
        ("Ranked Scorecard", scorecard),
        ("Ranked Alternatives", html_list(alternatives)),
    ]


def _sensitivity_section(decision: dict) -> tuple[str, str]:
    rows = [
        [
            html.escape(item["added_criterion"]),
            html.escape(item["removed_criterion"]),
            str(item["total_weight"]),
            html.escape(item["winner"] or "owner decision required"),
        ]
        for item in decision["sensitivity"]
    ]
    return "Sensitivity", html_table(["Added", "Removed", "Total", "Winner"], rows)


def _workflow_sections(decision: dict) -> list[tuple[str, str]]:
    keys = ("id", "owner", "input", "output", "evidence_requirement", "stop_condition")
    workflow_rows = [
        [html.escape(stage[key]) for key in keys] for stage in decision["workflow"]
    ]
    persona_rows = [
        [html.escape(item["id"]), html.escape(item["responsibility"])]
        for item in decision["personas"]
    ]
    workflow = html_table(
        ["Stage", "Owner", "Input", "Output", "Evidence", "Stop condition"],
        workflow_rows,
    )
    personas = html_table(["Persona", "Responsibility"], persona_rows)
    return [("Workflow", workflow), ("Personas", personas)]


def _source_links(decision: dict) -> list[str]:
    class_sources = [
        {"id": f"{candidate['id']}-{item['class']}", "source_url": item["source_url"]}
        for candidate in decision["candidates"]
        for item in candidate["evidence_classes"]
    ]
    return [
        f'<a href="{html.escape(item["source_url"], quote=True)}">'
        f"{html.escape(item['id'])}</a>"
        for item in [*decision["source_ledger"], *class_sources]
    ]


def _report_sections(decision: dict) -> list[tuple[str, str]]:
    summary = (
        f"<p>Status: {html.escape(decision['decision_status'])}</p>"
        f"<p>Reason: {html.escape(decision['decision_reason'])}</p>"
        f"<p>Closeout ready: {decision['closeout_ready']}</p>"
    )
    boundaries = [
        html.escape(f"{key}: {value}")
        for key, value in decision["evidence_boundaries"].items()
    ]
    sections = [("Decision", summary), *_score_sections(decision)]
    sections.extend([_sensitivity_section(decision), *_workflow_sections(decision)])
    sections.extend(
        [
            ("Evidence Boundaries", html_list(boundaries)),
            ("Risks", html_list([html.escape(item) for item in decision["risks"]])),
            (
                "Success Criteria",
                html_list([html.escape(item) for item in decision["success_criteria"]]),
            ),
            ("Sources", html_list(_source_links(decision))),
        ]
    )
    return sections


def render_html(decision: dict) -> str:
    body = "\n".join(
        f"<section><h2>{title}</h2>{content}</section>"
        for title, content in _report_sections(decision)
    )
    data = json.dumps(
        decision, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    legal = html.escape(decision["legal_boundary"])
    return (
        '<!doctype html>\n<html lang="en">\n<head><meta charset="utf-8">'
        "<title>Landman Pilot Decision</title></head>\n<body><main>"
        f"<h1>Landman Pilot Decision</h1>{body}<p>{legal}</p></main>"
        f'<script id="decision-data" type="application/json">{data}</script>'
        "</body>\n</html>\n"
    )


def render_outputs(evidence: dict) -> tuple[str, str]:
    decision = build_decision(evidence)
    document = yaml.safe_dump(
        decision,
        sort_keys=True,
        allow_unicode=False,
        default_flow_style=None,
        width=1000,
    )
    return document, render_html(decision)
