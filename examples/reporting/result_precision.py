"""Run with: python -m examples.reporting.result_precision.

All values, bounds and limits are synthetic input assumptions. Independent hand
calculation: 2*3-4=2 N; error <= |2|*.1+|-1|*.2=.4 N by triangle
inequality, so [1.6,2.4] straddles the supplied 2.2 N limit. Separately,
10.04 N > 10 N, though nearest-even display to one place is 10.0 N.
"""
import json
from dataclasses import asdict

from scripts.reporting.result_precision import (
    Criterion,
    Quantity,
    Stage,
    assess,
    linear_combination,
)


def sample(value: str, error: str) -> Quantity:
    """Error is an assumed bound, not inferred from representation or digits."""
    return Quantity(
        name="resultant", unit="N", value=value,
        release="synthetic example", location="illustrative section",
        source="module docstring hand calculation; synthetic assumptions",
        native=Stage("declared storage", "synthetic assumed absolute bound", error),
        recovery=Stage("identity", "identity introduces no additional error", "0"),
        serialization=Stage("decimal text", "synthetic exact retention assumption", "0"),
        accumulation=Stage("none", "single input; no upstream sum", "0"),
    )


def worked_examples() -> dict:
    """Return inputs, method and answer; no file is written or solver invoked."""
    a, b = sample("3", ".1"), sample("4", ".2")
    combined = linear_combination([("2", a), ("-1", b)])
    limit = Criterion("2.2", "N", "<=", "synthetic supplied upper limit")
    linear = assess(combined, limit, places=1)
    rounding_input = sample("10.04", "0")
    rounding_limit = Criterion("10", "N", "<=", "synthetic supplied upper limit")
    rounding = assess(rounding_input, rounding_limit, places=1)
    return {
        "basis": "synthetic hand calculations; no native accuracy claim",
        "linear": {
            "inputs": [{"weight": weight, "quantity": asdict(q)}
                       for weight, q in combined.terms],
            "criterion": asdict(limit),
            "method": "y=2*3-4; B=abs(2)*.1+abs(-1)*.2",
            "answer": {"value": str(linear.value), "lower": str(linear.lower),
                       "upper": str(linear.upper), "display": linear.display,
                       "disposition": linear.disposition},
        },
        "rounding": {
            "input": asdict(rounding_input), "criterion": asdict(rounding_limit),
            "method": "compare 10.04 with 10 before nearest-even display rounding",
            "answer": {"display": rounding.display,
                       "disposition": rounding.disposition,
                       "rounding_sensitive": rounding.rounding_sensitive},
        },
    }


if __name__ == "__main__":
    print(json.dumps(worked_examples(), indent=2))
