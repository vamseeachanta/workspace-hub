"""Offline, non-production identity example; not complete run admission.

Authority: docs/architecture/algorithm-run-dataset-contract.yaml, identity.
Profile and all synthetic fixture numbers: docs/examples/algorithm-run-identity.md.
The restricted ASCII-key/integer profile does not implement full JCS.
"""

import hashlib
import json
import re
import unicodedata


# Pinned by identity.canonicalization.version, never contract_version.
CANONICALIZATION_VERSION = "identity-jcs-1"
VERSION_FIELDS = (
    "algorithm_id",
    "semantic_version",
    "clean_git_commit",
    "input_schema_version",
    "output_schema_version",
    "environment_digest",
)


def _normalize(value):
    """Accept only plain dictionaries, lists, strings and unitless integers."""
    if type(value) is str:
        return unicodedata.normalize("NFC", value)
    if type(value) is int:
        return value
    if type(value) is list:
        return [_normalize(item) for item in value]
    if type(value) is dict:
        if any(type(key) is not str or not key.isascii() for key in value):
            raise ValueError("object keys must be ASCII strings")
        return {key: _normalize(item) for key, item in value.items()}
    raise ValueError("unsupported value: use strings, unitless integers, lists or objects")


def canonical_bytes(value):
    """Encode the restricted profile as compact, sorted-key, NFC UTF-8 JSON.

    Booleans, null, floats (including non-finite values), Decimal and other
    types are deliberately unsupported. Callers declare integers unitless;
    this example neither infers physical dimensions nor converts units.
    """
    try:
        normalized = _normalize(value)
        return json.dumps(
            normalized, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (UnicodeError, RecursionError) as error:
        raise ValueError("value must be finite, acyclic UTF-8 data") from error


def identity_digest(identity_type, payload):
    """Hash the contract's identity-type and scheme-version domain prefix."""
    if identity_type not in ("algorithm_version_id", "run_id"):
        raise ValueError("unsupported identity type")
    prefix = f"{identity_type}\n{CANONICALIZATION_VERSION}\n".encode("ascii")
    return "sha256:" + hashlib.sha256(prefix + canonical_bytes(payload)).hexdigest()


def _required(record, field):
    if type(record) is not dict or field not in record:
        raise ValueError(f"missing {field}")
    return record[field]


def _digest(value, field):
    # SHA-256 hexadecimal length follows identity.digest in the cited contract.
    if type(value) is not str or not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
        raise ValueError(f"invalid {field}")
    return value


def algorithm_version_identity(version):
    """Select declared immutable bindings; do not discover repository state."""
    projection = {field: _required(version, field) for field in VERSION_FIELDS}
    for field, value in projection.items():
        if type(value) is not str or not value.strip():
            raise ValueError(f"invalid {field}")
    # Full hexadecimal Git revision shape from the cited identity plan.
    # Shape alone does not prove existence, cleanliness or public eligibility.
    if not re.fullmatch(r"[0-9a-f]{40}", projection["clean_git_commit"]):
        raise ValueError("invalid clean_git_commit")
    _digest(projection["environment_digest"], "environment_digest")
    return identity_digest("algorithm_version_id", projection)


def run_identity(record):
    """Bind version, opaque input-set digest, explicit controls and seed only."""
    version_id = algorithm_version_identity(_required(record, "algorithm_version"))
    input_set_id = _digest(_required(record, "input_set_id"), "input_set_id")
    parameters = _required(record, "execution_parameters")
    if type(parameters) is not dict:
        raise ValueError("execution_parameters must be an explicit object")
    seed = _required(record, "seed")
    if type(seed) is not int and seed != "deterministic:no-seed":
        raise ValueError("seed must be an integer or deterministic:no-seed")
    return identity_digest("run_id", {
        "algorithm_version_id": version_id,
        "input_set_id": input_set_id,
        "execution_parameters": parameters,
        "seed": seed,
    })


def main():
    """Print fabricated identities only; no files, network or Git discovery."""
    # Synthetic fixture values are defined in the worked-example documentation.
    record = {
        "algorithm_version": {
            "algorithm_id": "synthetic:counter",
            "semantic_version": "1.0.0",
            "clean_git_commit": "a" * 40,
            "input_schema_version": "1.0.0",
            "output_schema_version": "1.0.0",
            "environment_digest": "sha256:" + "b" * 64,
        },
        "input_set_id": "sha256:" + "d" * 64,
        "execution_parameters": {"iterations": 3, "label": "caf\u00e9"},
        "seed": 7,
        "observed_at": "2026-01-01T00:00:00Z",
    }
    print("algorithm_version_id=" + algorithm_version_identity(record["algorithm_version"]))
    print("run_id=" + run_identity(record))


if __name__ == "__main__":
    main()
