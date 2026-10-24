"""Source validation parity required by issue #3445.

Expected results follow independent contract reasoning: a known source, literal
relative endpoint, and scalar query mapping pass syntax. Every malformed type or
path fails before a fetch. Network availability is unknowable without I/O, so
syntax success alone must never yield routable_now=true. No live API is used.
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fetch_from_api as api


@pytest.mark.parametrize(
    "source,endpoint,params",
    [
        (None, "Production", None),
        ([], "Production", None),
        ({}, "Production", None),
        ("", "Production", None),
        ("unknown", "Production", None),
        ("bsee", None, None),
        ("bsee", [], None),
        ("bsee", "", None),
        ("bsee", "   ", None),
        ("bsee", "Production\x00", None),
        ("bsee", "Production\n", None),
        ("bsee", "https://example.invalid/records", None),
        ("bsee", "//example.invalid/records", None),
        ("bsee", "../records", None),
        ("bsee", "records/../other", None),
        ("bsee", "records/./other", None),
        ("bsee", "records//other", None),
        ("bsee", "records\\other", None),
        ("bsee", "records?query=value", None),
        ("bsee", "records#fragment", None),
        ("bsee", "%2e%2e/other", None),
        ("bsee", "Production", []),
        ("bsee", "Production", "year=value"),
        ("bsee", "Production", {None: "value"}),
        ("bsee", "Production", {"": "value"}),
        ("bsee", "Production", {"field": []}),
        ("bsee", "Production", {"field": {}}),
        ("bsee", "Production", {"field": float("nan")}),
        ("bsee", "Production", {"field": float("inf")}),
        ("bsee", "Production", {"field": "value\x00"}),
    ],
)
def test_malformed_context_has_identical_status_and_execution_errors(
    source, endpoint, params, tmp_path
):
    """All paths reject the same context; expected fetch and write counts are zero."""
    fetcher = Mock()
    output = tmp_path / "not-created"
    status = api.source_status(source, endpoint, params=params)
    assert status["syntax_validation"] == "FAILED"
    assert status["requirements_satisfied"] is False
    assert status["routable_now"] is False
    assert status["io_validation"] == "NOT_EVALUATED"
    for execute in (
        lambda: api.validate_source_context(source, endpoint, params=params),
        lambda: api.build_api_url(source, endpoint, params=params),
        lambda: api.fetch_api_data(
            source, endpoint, params=params, output_dir=output, fetcher=fetcher
        ),
    ):
        with pytest.raises(api.SourceContextError) as error:
            execute()
        assert error.value.code == status["reason_codes"][0]
    fetcher.assert_not_called()
    assert not output.exists()


@pytest.mark.parametrize(
    "endpoint", ["Production", "/Production", "records/detail.json"]
)
def test_valid_context_status_defers_io_and_execution_uses_same_url(
    endpoint, monkeypatch
):
    """Hand calculation: valid syntax + no I/O evidence => not routable yet."""
    monkeypatch.setattr(
        api.os.environ, "get", Mock(side_effect=AssertionError("environment read"))
    )
    monkeypatch.setattr(
        api, "_default_fetcher", Mock(side_effect=AssertionError("network read"))
    )
    params = {"label": "a b"}
    assert api.source_status("bsee", endpoint, params=params) == {
        "syntax_validation": "PASSED",
        "requirements_satisfied": True,
        "routable_now": False,
        "io_validation": "NOT_EVALUATED",
        "reason_codes": ["IO_VALIDATION_DEFERRED"],
    }
    # Expected URL follows the existing registry base + endpoint + query encoding.
    expected = (
        api.get_api_registry()["bsee"]["base_url"] + endpoint.lstrip("/") + "?label=a+b"
    )
    fetcher = Mock(return_value={"records": []})
    assert api.fetch_api_data("bsee", endpoint, params=params, fetcher=fetcher) == {
        "records": []
    }
    fetcher.assert_called_once_with(expected)


def test_unavailable_source_is_deferred_in_status_and_failure_propagates():
    """Offline syntax cannot establish availability; failed I/O never becomes success."""
    fetcher = Mock(side_effect=OSError("unavailable"))
    assert api.source_status("bsee", "Production")["routable_now"] is False
    with pytest.raises(OSError, match="unavailable"):
        api.fetch_api_data("bsee", "Production", fetcher=fetcher)
    fetcher.assert_called_once()


@pytest.mark.parametrize("key", [[], {}, True, "", " ", "invalid\x00"])
def test_malformed_key_uses_structured_error_without_echoing_input(key):
    with pytest.raises(api.SourceContextError) as error:
        api.build_api_url("bsee", "Production", api_key=key)
    assert error.value.code == "INVALID_API_KEY"
    assert str(error.value) == "INVALID_API_KEY"


def test_registry_copy_cannot_change_validation_authority():
    registry = api.get_api_registry()
    registry["bsee"]["endpoints"].clear()
    assert api.get_api_registry()["bsee"]["endpoints"]


@pytest.mark.parametrize("pages", ["1", "2"])
def test_cli_invalid_source_never_fetches(pages, monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["fetch", "--source", "bsee", "--endpoint", "../bad", "--max-pages", pages],
    )
    fetcher = Mock(side_effect=AssertionError("network used"))
    monkeypatch.setattr(api, "_default_fetcher", fetcher)
    with pytest.raises(SystemExit) as error:
        api.main()
    assert error.value.code == 2  # argparse's existing usage-error convention.
    assert "INVALID_ENDPOINT" in capsys.readouterr().err
    fetcher.assert_not_called()


def test_cli_status_uses_shared_validation_and_performs_no_io(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["fetch", "--source", "bsee", "--endpoint", "Production", "--status"],
    )
    monkeypatch.setattr(
        api, "_default_fetcher", Mock(side_effect=AssertionError("network used"))
    )
    api.main()
    assert json.loads(capsys.readouterr().out) == api.source_status(
        "bsee", "Production"
    )


@pytest.mark.parametrize("params", ["broken", "=value", "field=value,broken"])
def test_cli_does_not_silently_drop_malformed_params(params, monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["fetch", "--source", "bsee", "--endpoint", "Production", "--params", params],
    )
    fetcher = Mock()
    monkeypatch.setattr(api, "_default_fetcher", fetcher)
    with pytest.raises(SystemExit):
        api.main()
    assert "INVALID_PARAMS" in capsys.readouterr().err
    fetcher.assert_not_called()


@pytest.mark.parametrize("source", ["bsee", "eia", "imo"])
def test_all_registry_sources_have_offline_status(source, monkeypatch):
    monkeypatch.setattr(
        api.os.environ, "get", Mock(side_effect=AssertionError("environment read"))
    )
    endpoint = api.get_api_registry()[source]["endpoints"][0]
    assert api.source_status(source, endpoint)["syntax_validation"] == "PASSED"
    assert api.source_status(source, endpoint)["io_validation"] == "NOT_EVALUATED"


def test_unencodable_numeric_param_has_status_execution_parity():
    """Python's runtime integer conversion bound must apply to both consumers."""
    digits = sys.get_int_max_str_digits()
    if not digits:
        pytest.skip("runtime integer string conversion is unbounded")
    # A decimal power at the runtime's digit limit needs one additional digit.
    params = {"value": 10**digits}
    assert api.source_status("bsee", "Production", params=params)["reason_codes"] == [
        "INVALID_PARAMS"
    ]
    with pytest.raises(api.SourceContextError, match="INVALID_PARAMS"):
        api.build_api_url("bsee", "Production", params=params)


def test_empty_query_value_is_valid_and_encoded():
    """An explicit empty value remains a query member, not an absent mapping."""
    params = {"field": ""}
    assert (
        api.source_status("bsee", "Production", params=params)["requirements_satisfied"]
        is True
    )
    assert api.build_api_url("bsee", "Production", params=params).endswith("?field=")


def test_status_rejects_supplied_malformed_key_with_execution_code():
    assert api.source_status("bsee", "Production", api_key=[])["reason_codes"] == [
        "INVALID_API_KEY"
    ]


def test_cli_status_invalid_context_outputs_structured_error(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["fetch", "--status", "--source", "unknown"])
    api.main()
    status = json.loads(capsys.readouterr().out)
    assert status["requirements_satisfied"] is False
    assert status["reason_codes"] == ["UNKNOWN_SOURCE"]


def test_invalid_context_rejected_before_credential_lookup(monkeypatch):
    """No environment or fetch access is needed to reject malformed syntax."""
    lookup = Mock(side_effect=AssertionError("environment read"))
    monkeypatch.setattr(api.os.environ, "get", lookup)
    fetcher = Mock()
    with pytest.raises(api.SourceContextError, match="INVALID_ENDPOINT"):
        api.fetch_api_data("eia", "../records", fetcher=fetcher)
    lookup.assert_not_called()
    fetcher.assert_not_called()
