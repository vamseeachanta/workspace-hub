from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "email"


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def spam_rule():
    rules = load_yaml(ROOT / "scripts" / "email" / "spam-detection-rules.yaml")
    return next(rule for rule in rules["rules"] if rule["id"] == "letstok_web_form_abuse")


def matches_rule(message: dict, rule: dict) -> bool:
    haystack = " ".join(
        str(message.get(key, "")) for key in ["subject", "body", "sender", "from"]
    ).lower()
    return any(term.lower() in haystack for term in rule["contains_any"])


def test_letstok_detects_fatigue_analysis_fixture():
    assert matches_rule(
        load_yaml(FIXTURES / "letstok-01-fatigue-analysis.yaml"), spam_rule()
    )


def test_letstok_detects_offshore_engineering_fixture():
    assert matches_rule(
        load_yaml(FIXTURES / "letstok-02-offshore-engineering.yaml"), spam_rule()
    )


def test_letstok_no_false_positive_on_legitimate_corpus():
    rule = spam_rule()
    fixtures = sorted((FIXTURES / "legitimate-inquiries").glob("*.yaml"))

    assert len(fixtures) >= 10
    assert [
        fixture.name for fixture in fixtures if matches_rule(load_yaml(fixture), rule)
    ] == []

