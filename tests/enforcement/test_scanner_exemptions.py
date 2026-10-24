"""Exemption boundaries from issue #3938 (2026), checked by Boolean cases.

Hand calculation: suppression = context AND category AND exact path AND
same-line marker AND safe structure. The positive case has every term true;
changing any single term makes the conjunction false. No measured constants
or engineering acceptance limits are involved.
"""

from dataclasses import replace

import pytest
from enforcement.scanner_exemptions import ExemptionPolicy, exemption_applies
from testing.scanner_exemption_contract import ExemptionProbe, assert_exemption_contract

CONTEXT = "literal-example"
CATEGORY = "syntax-example"
PATH = b"tests/fixtures/example.py"
MARKER = b"example-forensic"
LINE = b'PATTERN = "synthetic-example"  # example-forensic'


def policy():
    return ExemptionPolicy(CONTEXT, CATEGORY, frozenset({PATH}), MARKER)


def allows(probe):
    lines = probe.body.splitlines()
    if not 1 <= probe.line_number <= len(lines):
        return False
    line = lines[probe.line_number - 1]
    return exemption_applies(
        (policy(),), context_id=probe.context_id, rule_category=probe.rule_category,
        path=probe.path, line=line, structure_matches=line == LINE,
    )


def good_probe():
    return ExemptionProbe(CONTEXT, CATEGORY, PATH, LINE, 1)


def check_contract(adapter):
    assert_exemption_contract(
        adapter, good_probe(),
        other_categories=("secret-assignment",),
        other_paths=(b"scripts/example.py", PATH + b".backup"),
        invalid_bodies=(
            LINE.replace(b"  # example-forensic", b""),
            b"# example-forensic\n" + LINE.split(b"  #")[0],
            b'run("synthetic-example")  # example-forensic',
        ),
    )


def test_reusable_boundary_contract():
    check_contract(allows)


@pytest.mark.parametrize("field,value", [
    ("context_id", "unknown"), ("context_id", CONTEXT.upper()),
    ("rule_category", "secret-assignment"), ("rule_category", CATEGORY.upper()),
    ("path", b"tests/fixtures/nested/example.py"),
    ("path", b"tests/fixtures/../fixtures/example.py"),
    ("path", b"./tests/fixtures/example.py"),
    ("path", b"tests\\fixtures\\example.py"),
    ("line_number", 0), ("line_number", -1), ("line_number", 2),
])
def test_unknown_or_aliased_contexts_deny(field, value):
    assert allows(replace(good_probe(), **{field: value})) is False


@pytest.mark.parametrize("line", [
    LINE.replace(b"  # example-forensic", b""),
    LINE + b"-suffix", LINE + b" executable()",
    LINE + b"\nrun()", LINE + b"\r", LINE + b"\n",
    b"# example-forensic\n" + LINE,
])
def test_marker_is_exact_trailing_and_single_line(line):
    assert not exemption_applies(
        (policy(),), context_id=CONTEXT, rule_category=CATEGORY, path=PATH,
        line=line, structure_matches=True,
    )


def test_marker_allows_horizontal_whitespace_only():
    assert exemption_applies(
        (policy(),), context_id=CONTEXT, rule_category=CATEGORY, path=PATH,
        line=LINE + b" \t", structure_matches=True,
    )


def test_structure_is_required_even_with_every_other_term_matching():
    assert not exemption_applies(
        (policy(),), context_id=CONTEXT, rule_category=CATEGORY, path=PATH,
        line=LINE, structure_matches=False,
    )


def test_empty_policy_set_retires_all_contexts():
    assert not exemption_applies(
        (), context_id=CONTEXT, rule_category=CATEGORY, path=PATH,
        line=LINE, structure_matches=True,
    )


def test_policy_copies_mutable_path_input():
    paths = {PATH}
    bound = ExemptionPolicy(CONTEXT, CATEGORY, paths, MARKER)
    paths.add(b"scripts/example.py")
    assert bound.paths == frozenset({PATH})


@pytest.mark.parametrize("field,value", [
    ("context_id", ""), ("rule_category", ""), ("paths", frozenset()),
    ("sentinel", b""), ("sentinel", b"marker\nnext"), ("sentinel", b"marker\r"),
])
def test_empty_or_multiline_binding_is_rejected(field, value):
    with pytest.raises(ValueError, match="exemption"):
        replace(policy(), **{field: value})


@pytest.mark.parametrize("mutation", [
    lambda probe: replace(probe, rule_category=CATEGORY),
    lambda probe: replace(probe, context_id=CONTEXT),
    lambda probe: replace(probe, path=PATH),
    lambda probe: replace(probe, body=LINE),
    lambda probe: replace(probe, line_number=1),
])
def test_contract_detects_deliberately_broken_adapters(mutation):
    with pytest.raises(AssertionError, match="exemption contract"):
        check_contract(lambda probe: allows(mutation(probe)))


def test_contract_rejects_always_allow_and_always_deny():
    for outcome in (True, False):
        with pytest.raises(AssertionError, match="exemption contract"):
            check_contract(lambda _probe, outcome=outcome: outcome)


@pytest.mark.parametrize("field", ["other_categories", "other_paths", "invalid_bodies"])
def test_contract_rejects_missing_boundary_coverage(field):
    cases = {"other_categories": ("secret-assignment",),
             "other_paths": (b"scripts/example.py",), "invalid_bodies": (b"run()",)}
    cases[field] = ()
    with pytest.raises(ValueError, match="boundary"):
        assert_exemption_contract(allows, good_probe(), **cases)
