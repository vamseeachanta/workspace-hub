"""Structural checks for the synthetic layout documented in docs/examples.

Numeric expectations use the independent doubling calculation in
docs/examples/rolling-algorithm-report.md, not renderer calculations.
"""

from dataclasses import replace
from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "examples/algorithm_runs/rolling_report_example.py"


@pytest.fixture(scope="module")
def example():
    spec = importlib.util.spec_from_file_location("rolling_report_example", MODULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Element:
    def __init__(self, tag, attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []

    def find(self, tag):
        return [node for node in self.walk() if node.tag == tag]

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Element):
                yield from child.walk()

    def text(self):
        return "".join(
            child.text() if isinstance(child, Element) else child
            for child in self.children
        )


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Element("document")
        self.stack = [self.root]
        self.feed(html)
        self.close()
        assert self.stack == [self.root], "unclosed elements"

    def handle_starttag(self, tag, attrs):
        node = Element(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in {"meta", "br", "img", "link", "hr", "input"}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        assert self.stack[-1].tag == tag, "misnested elements"
        self.stack.pop()

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def sections(self):
        return {node.attrs["id"]: node for node in self.root.find("section")}


def test_required_sections_exist(example):
    contract = yaml.safe_load(
        (ROOT / "docs/architecture/algorithm-run-dataset-contract.yaml").read_text()
    )["report"]
    for runs in ((), example.synthetic_runs()):
        document = Document(example.render_report("Synthetic doubling", runs))
        sections = document.sections()
        assert set(contract["mandatory_sections"]) <= sections.keys()
        assert [node.text() for node in sections["inputs"].find("h2")] == ["Inputs"]
        assert [node.text() for node in sections["outputs"].find("h2")] == ["Outputs"]
        assert len(document.root.find("main")) == 1
        ids = [node.attrs["id"] for node in document.root.walk() if "id" in node.attrs]
        assert len(ids) == len(set(ids))
    assert "Input scalar" in sections["inputs"].text()
    assert "Doubled scalar" in sections["outputs"].text()
    assert "failed-synthetic" not in sections["outputs"].text()


def test_optional_sections_follow_applicability(example):
    full = Document(example.render_report("Synthetic doubling", example.synthetic_runs()))
    headings = {node.text() for node in full.root.find("h2")}
    assert headings == {
        "Inputs", "Outputs", "Metrics", "Plots and comparisons", "Uncertainty",
        "Diagnostics and health", "Insights", "Decision brief",
    }
    contract = yaml.safe_load(
        (ROOT / "docs/architecture/algorithm-run-dataset-contract.yaml").read_text()
    )["report"]
    assert set(full.sections()) == set(
        contract["mandatory_sections"] + contract["optional_sections"]
    )
    minimal = example.Run("minimal-synthetic", example.SUCCESS)
    assert [node.text() for node in Document(
        example.render_report("Minimal", (minimal,))
    ).root.find("h2")] == ["Inputs", "Outputs"]
    fields = {
        "metrics": {"metrics": (("Scalar [dimensionless]", "0"),)},
        "plots_and_comparisons": {"comparisons": ("Explicit run comparison",)},
        "uncertainty": {"uncertainty": ("Synthetic interval",)},
        "diagnostics_and_health": {
            "diagnostics": (example.Artifact("Warning", "fixtures/warning.txt"),)
        },
        "insights": {"insights": ("Validated synthetic claim",)},
        "decision_brief": {"decision_brief": ("Reviewed no-decision",)},
    }
    for section, changes in fields.items():
        run = replace(minimal, **changes)
        assert set(Document(example.render_report("Single section", (run,))).sections()) == {
            "inputs", "outputs", section,
        }


def test_failed_run_is_excluded_from_metrics(example):
    historical, current, failed = example.synthetic_runs()
    # Literal partition and values from the documented independent calculation.
    assert [run.label for run in (historical, current, failed)] == [
        "historical-synthetic", "current-synthetic", "failed-synthetic",
    ]
    failed = replace(
        failed, metrics=(("LEAK_METRIC", "999"),), comparisons=("LEAK_COMPARISON",),
        uncertainty=("LEAK_UNCERTAINTY",), insights=("LEAK_INSIGHT",),
        decision_brief=("LEAK_DECISION",),
        outputs=(example.Artifact("LEAK_OUTPUT", "fixtures/forbidden.json"),),
    )
    document = Document(example.render_report("Partition", (historical, current, failed)))
    sections = document.sections()
    rows = [node.text() for node in sections["metrics"].find("tr")]
    assert rows == [
        "RunMetricValue", "historical-syntheticDoubled scalar [dimensionless]2",
        "current-syntheticDoubled scalar [dimensionless]4",
    ]
    assert "failed-synthetic" in sections["diagnostics_and_health"].text()
    assert "invalid-input" in sections["diagnostics_and_health"].text()
    assert "fixtures/failed-diagnostic.txt" in {
        node.attrs["href"] for node in sections["diagnostics_and_health"].find("a")
    }
    assert "LEAK_" not in document.root.text()
    failed_only = Document(example.render_report("Failure only", (failed,)))
    assert set(failed_only.sections()) == {"inputs", "outputs", "diagnostics_and_health"}


def test_untrusted_labels_do_not_create_html_elements(example):
    payload = '<script>alert("label")</script><img src=x onerror="alert(1)">&'
    historical, _, failed = example.synthetic_runs()
    run = replace(
        historical, label=payload,
        inputs=(example.Artifact(payload, "fixtures/input.json"),),
        outputs=(example.Artifact(payload, "fixtures/output.json"),),
        metrics=((payload, payload),), comparisons=(payload,), uncertainty=(payload,),
        insights=(payload,), decision_brief=(payload,),
    )
    failed = replace(
        failed, label=payload, failure_phase=payload, failure_code=payload,
        failure_signature=payload,
        diagnostics=(example.Artifact(payload, "fixtures/diagnostic.txt"),),
    )
    document = Document(example.render_report(payload, (run, failed)))
    assert not document.root.find("script") and not document.root.find("img")
    assert payload in document.root.find("h1")[0].text()
    for section in document.sections().values():
        assert payload in section.text()
    assert all(
        not key.startswith("on") for node in document.root.walk() for key in node.attrs
    )


def test_links_are_relative(example):
    document = Document(example.render_report("Relative links", example.synthetic_runs()))
    links = [node.attrs["href"] for node in document.root.find("a")]
    assert set(links) == {
        "fixtures/historical-input.json", "fixtures/current-input.json",
        "fixtures/failed-input.json", "fixtures/historical-output.json",
        "fixtures/current-output.json", "fixtures/failed-diagnostic.txt",
    }
    assert all(link.startswith("fixtures/") and ":" not in link for link in links)


@pytest.mark.parametrize("href", [
    "https://example.invalid/artifact", "//example.invalid/artifact", "/artifact",
    "../artifact", "fixtures/../artifact", "fixtures/%2e%2e/artifact",
    "fixtures/file?redirect=external", "fixtures/file#fragment", "fixtures/",
    "javascript:alert(1)", 'fixtures/file\" onclick="alert(1)',
    "fixtures\\artifact", "fixtures/file\nname", "data:text/html,payload",
])
def test_unsafe_artifact_links_are_rejected(example, href):
    run = example.Run("synthetic", example.SUCCESS, inputs=(example.Artifact("Input", href),))
    with pytest.raises(ValueError, match="relative fixture"):
        example.render_report("Invalid link", (run,))


def test_unknown_status_is_rejected(example):
    with pytest.raises(ValueError, match="status"):
        example.render_report("Unknown", (example.Run("synthetic", "unknown"),))


def test_renderer_is_deterministic_and_does_not_modify_records(example):
    runs = example.synthetic_runs()
    assert example.render_report("Synthetic", runs) == example.render_report("Synthetic", runs)
    assert runs == example.synthetic_runs()
