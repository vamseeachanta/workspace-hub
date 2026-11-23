"""Pure synthetic rolling-report layout; no publication or dataset access.

Section vocabulary: docs/architecture/algorithm-run-dataset-contract.yaml, report.
Fixture values: independent calculation in docs/examples/rolling-algorithm-report.md.
Run this file to write the example HTML to standard output.
"""

from dataclasses import dataclass
from html import escape
import re


SUCCESS = "succeeded_validated_reproducible"
FAILURE = "reproducible_failure"


@dataclass(frozen=True)
class Artifact:
    label: str
    href: str


@dataclass(frozen=True)
class Run:
    """Presentation data; supplied optional evidence is already applicable.

    This example does not validate scientific claims, review or acceptance.
    Inputs include every displayed run. Only successful runs supply analytical
    sections and primary outputs; failures supply health evidence instead.
    """

    label: str
    status: str
    inputs: tuple[Artifact, ...] = ()
    outputs: tuple[Artifact, ...] = ()
    metrics: tuple[tuple[str, str], ...] = ()
    comparisons: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    diagnostics: tuple[Artifact, ...] = ()
    failure_phase: str = ""
    failure_code: str = ""
    failure_signature: str = ""
    insights: tuple[str, ...] = ()
    decision_brief: tuple[str, ...] = ()


def _link(artifact: Artifact) -> str:
    # Confine references to the illustrative fixture directory. Restrict the
    # alphabet as well as escaping HTML: escaping alone cannot prevent active
    # URL schemes, traversal, encoded traversal or platform-specific paths.
    if re.fullmatch(
        r"fixtures/(?:[A-Za-z0-9_-][A-Za-z0-9_.-]*/)*[A-Za-z0-9_-][A-Za-z0-9_.-]*",
        artifact.href,
    ) is None:
        raise ValueError("artifact link must be a relative fixture reference")
    return f'<a href="{escape(artifact.href, quote=True)}">{escape(artifact.label)}</a>'


def _section(section_id: str, title: str, body: str) -> str:
    return f'<section id="{section_id}"><h2>{title}</h2>{body}</section>'


def _inventory(runs: tuple[Run, ...], field: str) -> str:
    items = [
        f"<li><strong>{escape(run.label)}</strong>: {_link(artifact)}</li>"
        for run in runs for artifact in getattr(run, field)
    ]
    return "<ul>" + "".join(items) + "</ul>" if items else "<p>No applicable artifacts.</p>"


def render_report(algorithm: str, runs: tuple[Run, ...]) -> str:
    """Return a complete HTML document without reading or writing any files.

    Caller order is retained, allowing historical and latest runs in one report.
    Optional text is prequalified presentation evidence, never trusted HTML.
    Dataset revisions, source commits and acceptance are deliberately unbound.
    """
    if any(run.status not in {SUCCESS, FAILURE} for run in runs):
        raise ValueError("unsupported run status")
    successful = tuple(run for run in runs if run.status == SUCCESS)
    sections = [
        _section("inputs", "Inputs", _inventory(runs, "inputs")),
        _section("outputs", "Outputs", _inventory(successful, "outputs")),
    ]
    metric_rows = [
        f"<tr><td>{escape(run.label)}</td><td>{escape(label)}</td>"
        f"<td>{escape(value)}</td></tr>"
        for run in successful for label, value in run.metrics
    ]
    if metric_rows:
        sections.append(_section(
            "metrics", "Metrics",
            "<table><thead><tr><th>Run</th><th>Metric</th><th>Value</th></tr></thead>"
            "<tbody>" + "".join(metric_rows) + "</tbody></table>",
        ))
    for field, section_id, title in (
        ("comparisons", "plots_and_comparisons", "Plots and comparisons"),
        ("uncertainty", "uncertainty", "Uncertainty"),
    ):
        body = _optional_text(successful, field)
        if body:
            sections.append(_section(section_id, title, body))
    health = []
    for run in runs:
        if run.status == FAILURE or run.diagnostics:
            body = f"<h3>{escape(run.label)}</h3>"
            if run.status == FAILURE:
                body += (
                    "<p>Failed run: excluded from analytical sections and primary outputs.</p>"
                    f"<dl><dt>Phase</dt><dd>{escape(run.failure_phase)}</dd>"
                    f"<dt>Code</dt><dd>{escape(run.failure_code)}</dd>"
                    f"<dt>Signature</dt><dd>{escape(run.failure_signature)}</dd></dl>"
                )
            body += _inventory((run,), "diagnostics")
            health.append(body)
    if health:
        sections.append(_section("diagnostics_and_health", "Diagnostics and health", "".join(health)))
    for field, title in (("insights", "Insights"), ("decision_brief", "Decision brief")):
        body = _optional_text(successful, field)
        if body:
            sections.append(_section(field, title, body))
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{escape(algorithm)} — synthetic rolling report</title></head><body><main>"
        f"<h1>{escape(algorithm)}</h1>"
        "<p>Synthetic layout example. Immutable data, source commits and exact dataset "
        "revisions are not integrated; this report is not publication evidence.</p>"
        + "".join(sections) + "</main></body></html>"
    )


def _optional_text(runs: tuple[Run, ...], field: str) -> str:
    items = [
        f"<li><strong>{escape(run.label)}</strong>: {escape(text)}</li>"
        for run in runs for text in getattr(run, field)
    ]
    return "<ul>" + "".join(items) + "</ul>" if items else ""


def synthetic_runs() -> tuple[Run, ...]:
    """Literal fixtures; arithmetic and applicability basis are in the example doc."""
    return (
        Run(
            "historical-synthetic", SUCCESS,
            inputs=(Artifact("Input scalar", "fixtures/historical-input.json"),),
            outputs=(Artifact("Doubled scalar", "fixtures/historical-output.json"),),
            metrics=(("Doubled scalar [dimensionless]", "2"),),
        ),
        Run(
            "current-synthetic", SUCCESS,
            inputs=(Artifact("Input scalar", "fixtures/current-input.json"),),
            outputs=(Artifact("Doubled scalar", "fixtures/current-output.json"),),
            metrics=(("Doubled scalar [dimensionless]", "4"),),
            comparisons=(
                "historical-synthetic (2) versus current-synthetic (4), dimensionless; "
                "difference 2, from the documented doubling calculation.",
            ),
            uncertainty=(
                "Illustrative absolute interval [3, 5], dimensionless: current value "
                "plus or minus 1; assumed bound, no statistical confidence claimed.",
            ),
            insights=(
                "Synthetic validated comparison: current-synthetic exceeds "
                "historical-synthetic, using the displayed doubled scalar metric.",
            ),
            decision_brief=(
                "Illustrative reviewed no-decision. Alternatives: historical-synthetic "
                "and current-synthetic. Constraint: synthetic evidence only. "
                "Recommendation: obtain qualified data before choosing.",
            ),
        ),
        Run(
            "failed-synthetic", FAILURE,
            inputs=(Artifact("Invalid input scalar", "fixtures/failed-input.json"),),
            diagnostics=(Artifact("Curated diagnostic", "fixtures/failed-diagnostic.txt"),),
            failure_phase="input-validation", failure_code="invalid-input",
            failure_signature="synthetic-invalid-scalar",
        ),
    )


if __name__ == "__main__":
    print(render_report("Synthetic doubling", synthetic_runs()))
