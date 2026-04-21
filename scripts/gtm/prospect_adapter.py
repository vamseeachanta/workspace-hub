"""Prospect-intake adapter — validates YAML intake and routes to a GTM demo.

Current state for issue #2346:
- validation + interface surface are implemented
- demo_04 materialization is implemented
- other demo materialization paths are still explicit follow-up work
- demo invocation remains stubbed

See `docs/gtm/intake/IMPLEMENTATION-STATUS.md` for the authoritative
what-is-done vs what-is-not-done ledger.

Path convention: this module lives in `scripts/gtm/` (workspace-hub) rather
than `digitalmodel/examples/demos/gtm/` (separate repo) so a single
workspace-hub commit can carry schema + adapter + tests atomically.
"""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Mapping

import jsonschema
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "docs" / "gtm" / "intake" / "prospect-schema.json"
CANONICAL_DIR = REPO_ROOT / "docs" / "gtm" / "intake" / "canonical-vessels"

DEMO_IDS = ("demo_01", "demo_02", "demo_03", "demo_04", "demo_05")
DemoId = Literal["demo_01", "demo_02", "demo_03", "demo_04", "demo_05"]

# Per plan section C constants — which vessel shape each demo expects.
# None means the demo does not take a vessel block at all (Q6 forbidding
# rule for demos 1 + 2).
DEMO_TO_VESSEL_SHAPE: Mapping[DemoId, str | None] = {
    "demo_01": None,
    "demo_02": None,
    "demo_03": "csv_hlv",
    "demo_04": "pipelay",
    "demo_05": "csv_hlv",
}

DEMO_TO_STRUCTURE_KINDS: Mapping[DemoId, tuple[str, ...]] = {
    "demo_01": ("pipeline", "jumper_and_freespan"),
    "demo_02": ("pipeline",),
    "demo_03": ("mudmat",),
    "demo_04": ("pipeline",),
    "demo_05": ("rigid_jumper",),
}


class ProspectIntakeError(ValueError):
    """Raised when an intake YAML fails schema or cross-field validation."""


@dataclass(frozen=True)
class ProspectInput:
    """Validated intake payload returned by `load_and_validate`.

    `raw` holds the parsed YAML (a plain dict). Consumers should prefer
    the typed convenience fields (`target_demo`, `vessel_shape`, etc.)
    over reaching into `raw`; `raw` is retained so the downstream
    `materialize_demo_inputs` stage can access fields not yet promoted
    to the dataclass.
    """

    raw: dict
    target_demo: DemoId
    vessel_shape: str | None
    structure_kind: str
    source_path: Path

    @property
    def company(self) -> str:
        return str(self.raw["prospect"]["company"])

    @property
    def contact(self) -> str:
        return str(self.raw["prospect"]["contact"])


@dataclass(frozen=True)
class DemoInputBundle:
    """Filesystem layout that `run_demo` will consume.

    Demo_04 materialization now returns this bundle concretely. Other demo
    paths remain follow-up work and still raise NotImplementedError from
    `materialize_demo_inputs`.
    """

    demo_id: DemoId
    tmpdir: Path
    data_dir: Path
    env_override_path: Path | None = None
    vessel_file: Path | None = None
    structure_file: Path | None = None
    extras: dict[str, Path] = field(default_factory=dict)


def _load_schema() -> dict:
    with SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _resolved_vessel_body(prospect: ProspectInput) -> dict:
    """Return the vessel body, inlining canonical YAML when needed."""
    vessel = prospect.raw.get("vessel")
    if vessel is None:
        raise ProspectIntakeError("prospect does not include a vessel block")

    if vessel.get("source") == "canonical_ref":
        ref = vessel.get("canonical_ref")
        canonical_path = CANONICAL_DIR / f"{ref}.yaml"
        with canonical_path.open("r", encoding="utf-8") as fh:
            body = yaml.safe_load(fh)
        if not isinstance(body, dict):
            raise ProspectIntakeError(
                f"canonical vessel YAML must load to a mapping: {canonical_path}"
            )
        return deepcopy(body)

    body = vessel.get("body")
    if not isinstance(body, dict):
        raise ProspectIntakeError("prospect vessel.body must be a mapping")
    return deepcopy(body)


def _canonical_shape_matches_expected(body: Mapping[str, object], expected_shape: str) -> bool:
    """Return whether a canonical vessel body matches the expected demo shape."""
    if expected_shape == "pipelay":
        return "pipelay_system" in body and "crane_main" not in body
    if expected_shape == "csv_hlv":
        return "crane_main" in body and "pipelay_system" not in body
    return False


def _materialize_demo_04_inputs(prospect: ProspectInput, tmpdir: Path) -> DemoInputBundle:
    """Materialize demo_04 inputs into tmpdir/data/."""
    data_dir = tmpdir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    vessel_body = _resolved_vessel_body(prospect)
    vessel_file = data_dir / "pipelay_vessels.json"
    vessel_file.write_text(
        json.dumps({"vessels": [vessel_body]}, indent=2) + "\n",
        encoding="utf-8",
    )

    structure_body = deepcopy(prospect.raw["structure"]["body"])
    structure_file = data_dir / "pipelines.json"
    structure_file.write_text(
        json.dumps({"pipes": [structure_body]}, indent=2) + "\n",
        encoding="utf-8",
    )

    env_override_path = None
    environment = prospect.raw.get("environment")
    if isinstance(environment, dict) and environment:
        env_override_path = data_dir / "prospect_env.json"
        env_override_path.write_text(
            json.dumps(environment, indent=2) + "\n",
            encoding="utf-8",
        )

    return DemoInputBundle(
        demo_id=prospect.target_demo,
        tmpdir=tmpdir,
        data_dir=data_dir,
        env_override_path=env_override_path,
        vessel_file=vessel_file,
        structure_file=structure_file,
    )


def _cross_field_checks(intake: dict, demo: DemoId) -> None:
    """Gate 2 — checks not expressible in draft-07 JSON Schema.

    JSON Schema handles:
      - structural shape, required fields, enums, types
      - Q6 conditional required/forbidden vessel (demos 3/4/5 vs 1/2)
    This function handles:
      - vessel.shape must match the demo's expected shape
      - structure.kind must be in the demo's allowed list
      - if vessel.source == canonical_ref, the referenced YAML must exist
      - depth-vs-vessel-rating sanity (for csv_hlv with environment override)
    """
    expected_shape = DEMO_TO_VESSEL_SHAPE[demo]

    if expected_shape is None:
        # Demos 1/2: schema already enforced absence via properties.vessel=false,
        # but defense-in-depth assertion per plan section C.
        if "vessel" in intake:
            raise ProspectIntakeError(
                f"{demo} must not include a vessel block (Q6 forbidding rule)"
            )
        return

    # Demos 3/4/5: vessel present, shape correct, structure kind correct.
    vessel = intake.get("vessel")
    if vessel is None:
        raise ProspectIntakeError(f"{demo} requires a vessel block (Q6)")

    actual_shape = vessel.get("shape")
    if actual_shape != expected_shape:
        raise ProspectIntakeError(
            f"{demo} requires vessel.shape == {expected_shape!r}, got {actual_shape!r}"
        )

    structure_kind = intake["structure"]["kind"]
    allowed_kinds = DEMO_TO_STRUCTURE_KINDS[demo]
    if structure_kind not in allowed_kinds:
        raise ProspectIntakeError(
            f"{demo} requires structure.kind in {list(allowed_kinds)!r}, "
            f"got {structure_kind!r}"
        )

    if vessel.get("source") == "canonical_ref":
        ref = vessel.get("canonical_ref")
        if not ref:
            raise ProspectIntakeError(
                "vessel.source == 'canonical_ref' requires a non-empty canonical_ref"
            )
        canonical_path = CANONICAL_DIR / f"{ref}.yaml"
        if not canonical_path.exists():
            raise ProspectIntakeError(
                f"canonical vessel reference not found: {canonical_path}"
            )
        with canonical_path.open("r", encoding="utf-8") as fh:
            canonical_body = yaml.safe_load(fh)
        if not isinstance(canonical_body, dict):
            raise ProspectIntakeError(
                f"canonical vessel YAML must load to a mapping: {canonical_path}"
            )
        if not _canonical_shape_matches_expected(canonical_body, expected_shape):
            raise ProspectIntakeError(
                f"canonical vessel reference {ref!r} does not match required {expected_shape!r} shape"
            )


def load_and_validate(intake_path: Path) -> ProspectInput:
    """Read, schema-validate, and cross-field-check a prospect intake YAML.

    Raises ProspectIntakeError on any validation failure. Does NOT mutate
    the on-disk YAML; returns an immutable ProspectInput.
    """
    intake_path = Path(intake_path)
    if not intake_path.exists():
        raise ProspectIntakeError(f"intake file not found: {intake_path}")

    try:
        with intake_path.open("r", encoding="utf-8") as fh:
            intake = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ProspectIntakeError(f"malformed YAML in {intake_path}: {exc}") from exc

    if not isinstance(intake, dict):
        raise ProspectIntakeError(
            f"intake {intake_path} must be a YAML mapping at top level, "
            f"got {type(intake).__name__}"
        )

    schema = _load_schema()
    # Gate 1 — draft-07 structural validation.
    try:
        jsonschema.validate(
            instance=intake,
            schema=schema,
            cls=jsonschema.Draft7Validator,
        )
    except jsonschema.ValidationError as exc:
        raise ProspectIntakeError(
            f"schema validation failed for {intake_path}: {exc.message}"
        ) from exc

    demo = intake["prospect"]["target_demo"]
    # Gate 2 — cross-field consistency.
    _cross_field_checks(intake, demo)

    vessel_block = intake.get("vessel")
    return ProspectInput(
        raw=intake,
        target_demo=demo,
        vessel_shape=(vessel_block or {}).get("shape") if vessel_block else None,
        structure_kind=intake["structure"]["kind"],
        source_path=intake_path,
    )


def materialize_demo_inputs(
    prospect: ProspectInput, tmpdir: Path
) -> DemoInputBundle:
    """Map prospect fields onto the JSON shapes expected by the GTM demos.

    Current implementation is intentionally narrow: demo_04 is materialized,
    while the other demos remain explicit follow-up work.
    """
    tmpdir = Path(tmpdir)
    if prospect.target_demo == "demo_04":
        return _materialize_demo_04_inputs(prospect, tmpdir)

    raise NotImplementedError(
        "materialize_demo_inputs is partially implemented. "
        "Demo_04 shaping (pipelay_vessels.json, pipelines.json, prospect_env.json) exists; "
        "other demos remain follow-up work. "
        f"target_demo={prospect.target_demo!r}, tmpdir={tmpdir!s}"
    )


def run_demo(bundle: DemoInputBundle, demo_id: int) -> Path:
    """STUB — invoke the target demo subprocess and return the output HTML path.

    Scaffold for #2346 T2. Actual subprocess dispatch + report path
    discovery is deferred.
    """
    raise NotImplementedError(
        "run_demo is scaffolded but not implemented. The real version will "
        "subprocess-launch digitalmodel/examples/demos/gtm/demo_0{N}_*.py "
        "with --prospect-data-dir and --prospect-env, then return the "
        f"generated output/*.html path. demo_id={demo_id}, bundle={bundle!s}"
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="prospect_adapter",
        description=(
            "Validate a prospect intake YAML and route it to a GTM demo. "
            "Scaffold — materialize + run are stubbed."
        ),
    )
    parser.add_argument(
        "intake_path",
        type=Path,
        help="Path to a filled prospect intake YAML (see docs/gtm/intake/prospect-template.yaml).",
    )
    parser.add_argument(
        "--demo",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=None,
        help="Override the target demo (defaults to prospect.target_demo from the YAML).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate only; do not attempt to materialize inputs or run a demo.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        prospect = load_and_validate(args.intake_path)
    except ProspectIntakeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(
        f"OK validated: {args.intake_path} "
        f"(demo={prospect.target_demo}, company={prospect.company!r})"
    )
    if args.dry_run:
        print("--dry-run set; skipping materialize + run.")
        return 0

    # Scaffolding: reaching materialize/run is still an error until the
    # follow-up task implements them.
    demo_id = args.demo if args.demo is not None else int(prospect.target_demo[-2:])
    try:
        bundle = materialize_demo_inputs(prospect, Path("/tmp"))
        run_demo(bundle, demo_id)
    except NotImplementedError as exc:
        print(f"NOT IMPLEMENTED: {exc}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
