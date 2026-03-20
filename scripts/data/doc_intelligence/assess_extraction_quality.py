"""Quality assessment for deep-extracted worked examples.

Assigns ``use_as_test`` flag based on data completeness and merges
deep extraction records over classifier-derived records.
"""


def assess_example(example: dict) -> dict:
    """Assess a single worked example and set quality flags.

    Sets ``use_as_test: True`` when the example has:
    - At least one numerical input
    - A non-None expected_value

    Always sets ``extraction_source: 'deep'``.
    """
    result = dict(example)
    result["extraction_source"] = "deep"

    inputs = result.get("inputs", [])
    expected = result.get("expected_value")

    has_numerical_input = any(
        isinstance(i.get("value"), (int, float)) for i in inputs
    )
    has_expected = expected is not None

    result["use_as_test"] = has_numerical_input and has_expected
    return result


def merge_deep_over_classifier(
    classifier_records: list[dict],
    deep_records: list[dict],
) -> list[dict]:
    """Merge deep extraction records over classifier-derived records.

    Deep records take priority. Classifier records are kept only when
    no deep record covers the same source page.
    """
    if not deep_records:
        return list(classifier_records)

    deep_pages = set()
    for rec in deep_records:
        key = (rec.get("source_book", ""), rec.get("page", 0))
        deep_pages.add(key)

    merged = list(deep_records)
    for rec in classifier_records:
        source = rec.get("source", {})
        key = (source.get("document", ""), source.get("page", 0))
        if key not in deep_pages:
            merged.append(rec)
    return merged
