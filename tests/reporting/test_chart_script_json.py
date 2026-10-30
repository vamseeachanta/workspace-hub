"""Parse Chart.js configurations without executing JavaScript.

Supported chart and scale names: config/reporting/calculation-report-schema.yaml,
optional_sections.charts (type_enum and scale_enum). All coordinates, counts and
labels below are literal hand-constructed serialization data, with no engineering
meaning; expected subsets are written independently of the generator.
"""

import json
from html.parser import HTMLParser

import pytest

from generate_calc_report import build_chart_scripts


CALL_PREFIX = "new Chart(document.getElementById("


def _chart_configurations(scripts):
    """Decode entire calls in order; braces and call text in strings are data."""
    decoder = json.JSONDecoder()
    cursor = 0
    configurations = []
    while cursor < len(scripts):
        assert scripts.startswith(CALL_PREFIX, cursor), "Unexpected call prefix"
        cursor += len(CALL_PREFIX)
        canvas_id, cursor = decoder.raw_decode(scripts, cursor)
        assert isinstance(canvas_id, str), "Canvas identifier must be a string"
        assert scripts.startswith("), ", cursor), "Unexpected canvas argument ending"
        cursor += len("), ")
        config, cursor = decoder.raw_decode(scripts, cursor)
        assert isinstance(config, dict), "Configuration must be an object"
        assert scripts.startswith(");", cursor), "Unexpected configuration ending"
        cursor += len(");")
        configurations.append((canvas_id, config))
        if cursor < len(scripts):
            assert scripts[cursor] == "\n", "Trailing configuration debris"
            cursor += len("\n")
            assert cursor < len(scripts), "Trailing configuration debris"
    return configurations


def _chart(chart_type, **overrides):
    """Two independent synthetic series, each with two literal points."""
    chart = {
        "id": "synthetic-" + chart_type,
        "title": "Synthetic serialization data",
        "type": chart_type,
        "x_label": "Synthetic x",
        "y_label": "Synthetic y",
        "datasets": [
            {"label": "First series", "data": [[1, 2], [3, 5]]},
            {"label": "Second series", "data": [[7, 11], [13, 17]]},
        ],
    }
    chart.update(overrides)
    return chart


@pytest.mark.parametrize(
    "chart_type, expected_type",
    [("bar", "bar"), ("line", "line"), ("scatter", "scatter"), ("log_log", "scatter")],
)
@pytest.mark.parametrize(
    "scale_settings, expected_x, expected_y",
    [
        ({}, "linear", "linear"),
        ({"x_scale": "linear", "y_scale": "linear"}, "linear", "linear"),
        ({"x_scale": "log"}, "logarithmic", "linear"),
        ({"y_scale": "log"}, "linear", "logarithmic"),
        ({"x_scale": "log", "y_scale": "log"}, "logarithmic", "logarithmic"),
    ],
    ids=["defaults", "linear-both", "log-x", "log-y", "log-both"],
)
def test_chart_configuration_literal_data_and_scales(
    chart_type, expected_type, scale_settings, expected_x, expected_y
):
    configurations = _chart_configurations(
        build_chart_scripts([_chart(chart_type, **scale_settings)])
    )
    assert len(configurations) == 1
    canvas_id, config = configurations[0]
    assert canvas_id == "chart-synthetic-" + chart_type
    assert config["type"] == expected_type
    datasets = config["data"]["datasets"]
    assert len(datasets) == 2
    assert [dataset["label"] for dataset in datasets] == ["First series", "Second series"]
    if chart_type == "bar":
        assert config["data"]["labels"] == [1, 3]
        assert [dataset["data"] for dataset in datasets] == [[2, 5], [11, 17]]
    else:
        assert [dataset["data"] for dataset in datasets] == [
            [{"x": 1, "y": 2}, {"x": 3, "y": 5}],
            [{"x": 7, "y": 11}, {"x": 13, "y": 17}],
        ]
    scales = config["options"]["scales"]
    assert scales["x"]["title"] == {"display": True, "text": "Synthetic x"}
    assert scales["y"]["title"] == {"display": True, "text": "Synthetic y"}
    if chart_type == "bar":
        # Bar x is categorical; the linear y default is implicit in Chart.js.
        assert "type" not in scales["x"]
        if expected_y == "logarithmic":
            assert scales["y"]["type"] == "logarithmic"
        else:
            assert "type" not in scales["y"]
    else:
        assert scales["x"]["type"] == expected_x
        assert scales["y"]["type"] == expected_y


@pytest.mark.parametrize("chart_type", ["bar", "line", "scatter", "log_log"])
@pytest.mark.parametrize(
    "label",
    [
        'Quoted "series"',
        r"Backslash \\ series",
        "Unbalanced string braces }}} {",
        "Unicode Ω 雪",
        '</script><script>new Chart(document.getElementById("decoy"), {});</script>',
        "__DATASETS__",
    ],
)
def test_chart_configuration_preserves_literal_labels(chart_type, label):
    chart = _chart(chart_type, x_label=label, y_label=label)
    chart["datasets"][0]["label"] = label
    if chart_type == "bar":
        chart["datasets"][0]["data"] = [[label, 2], ["Other category", 5]]
    scripts = build_chart_scripts([chart])
    configurations = _chart_configurations(scripts)
    assert len(configurations) == 1
    canvas_id, config = configurations[0]
    assert canvas_id == "chart-synthetic-" + chart_type
    assert config["data"]["datasets"][0]["label"] == label
    assert config["data"]["datasets"][1]["label"] == "Second series"
    assert config["options"]["scales"]["x"]["title"]["text"] == label
    assert config["options"]["scales"]["y"]["title"]["text"] == label
    if chart_type == "bar":
        assert config["data"]["labels"] == [label, "Other category"]
        assert config["data"]["datasets"][0]["data"] == [2, 5]
    # A JSON round trip alone would not detect termination of an HTML script.
    assert "</script>" not in scripts.lower()


def test_chart_configuration_rejects_unbalanced_braces():
    # Hand-written malformed JSON: the outer configuration object is unclosed.
    corrupted = 'new Chart(document.getElementById("chart-broken"), {"data": {});'
    with pytest.raises(json.JSONDecodeError):
        _chart_configurations(corrupted)


def test_multiple_chart_configurations_match_rendered_canvases(minimal_valid):
    """Use the HTML parser to observe script boundaries without fetching sources."""
    from generate_calc_report import load_and_validate, render_html

    class ReportMarkup(HTMLParser):
        def __init__(self):
            super().__init__()
            self.canvas_ids = []
            self.scripts = []
            self.script_parts = None

        def handle_starttag(self, tag, attrs):
            if tag == "canvas":
                self.canvas_ids.append(dict(attrs)["id"])
            elif tag == "script":
                self.script_parts = []

        def handle_data(self, data):
            if self.script_parts is not None:
                self.script_parts.append(data)

        def handle_endtag(self, tag):
            if tag == "script" and self.script_parts is not None:
                self.scripts.append("".join(self.script_parts).strip())
                self.script_parts = None

    # Literal identifiers exercise JSON and HTML escaping independently.
    charts = [
        _chart("bar", id='bar-"quoted"'),
        _chart("line", id=r"line-\backslash"),
        _chart("scatter", id="scatter-}雪{", x_scale="log"),
        _chart("log_log", id="log-</script>", x_scale="log", y_scale="log"),
    ]
    for chart in charts:
        chart["datasets"][0]["label"] = '</script> } new Chart( " \\ Ω'
    minimal_valid["charts"] = charts
    markup = ReportMarkup()
    markup.feed(render_html(load_and_validate(minimal_valid), ""))
    wrapper_prefix = "document.addEventListener('DOMContentLoaded', function() {\n"
    wrapper_suffix = "\n});"
    chart_scripts = [script for script in markup.scripts if script.startswith(wrapper_prefix)]
    assert len(chart_scripts) == 1
    assert chart_scripts[0].endswith(wrapper_suffix)
    configurations = _chart_configurations(
        chart_scripts[0][len(wrapper_prefix):-len(wrapper_suffix)]
    )
    assert len(configurations) == 4
    expected_ids = [
        'chart-bar-"quoted"',
        r"chart-line-\backslash",
        "chart-scatter-}雪{",
        "chart-log-</script>",
    ]
    assert markup.canvas_ids == expected_ids
    assert [canvas_id for canvas_id, _ in configurations] == expected_ids
    assert [config["type"] for _, config in configurations] == [
        "bar", "line", "scatter", "scatter"
    ]
    for _, config in configurations:
        assert len(config["data"]["datasets"]) == 2
        assert config["data"]["datasets"][0]["label"] == '</script> } new Chart( " \\ Ω'


@pytest.mark.parametrize(
    "ending", ["});", ", {});", ");junk", ");\n{}", ")", ");\n"]
)
def test_chart_configuration_rejects_trailing_debris(ending):
    # The empty object is valid JSON; every suffix violates the full call grammar.
    corrupted = 'new Chart(document.getElementById("chart-broken"), {}' + ending
    with pytest.raises(AssertionError):
        _chart_configurations(corrupted)


def test_empty_charts_produce_no_configurations():
    assert build_chart_scripts([]) == ""
    assert _chart_configurations("") == []
