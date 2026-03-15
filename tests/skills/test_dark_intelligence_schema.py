"""TDD tests for dark intelligence archive YAML schema validation
and end-to-end calculation verification from archive data.

AC7: Schema validation tests
AC5: Worked example — archive YAML → calculation → verified output
"""

import math
import os
import re

import yaml

SCHEMA_PATH = "config/schemas/dark-intelligence-archive.yaml"
ARCHIVE_PATH = (
    "knowledge/dark-intelligence/geotechnical/pile_capacity/"
    "dark-intelligence-api-rp-2geo-alpha-method.yaml"
)


def load_schema():
    with open(SCHEMA_PATH) as f:
        return yaml.safe_load(f)


def load_archive():
    with open(ARCHIVE_PATH) as f:
        return yaml.safe_load(f)


def validate_archive(archive, schema):
    """Validate an archive entry against the schema. Returns list of errors."""
    errors = []

    # Check required fields
    for field in schema["required_fields"]:
        if field not in archive:
            errors.append(f"Missing required field: {field}")

    # Check field constraints
    constraints = schema.get("field_constraints", {})

    if "source_type" in archive and "source_type" in constraints:
        allowed = constraints["source_type"]["allowed"]
        if archive["source_type"] not in allowed:
            errors.append(
                f"source_type '{archive['source_type']}' not in {allowed}"
            )

    if "source_description" in archive and "source_description" in constraints:
        min_len = constraints["source_description"]["min_length"]
        if len(archive["source_description"]) < min_len:
            errors.append(
                f"source_description too short (min {min_len} chars)"
            )

    if "extracted_date" in archive and "extracted_date" in constraints:
        pattern = constraints["extracted_date"]["pattern"]
        if not re.match(pattern, archive["extracted_date"]):
            errors.append(f"extracted_date does not match pattern {pattern}")

    if "legal_scan_passed" in archive and "legal_scan_passed" in constraints:
        if archive["legal_scan_passed"] is not True:
            errors.append("legal_scan_passed must be true")

    # Check list constraints
    list_constraints = schema.get("list_constraints", {})
    for list_name, spec in list_constraints.items():
        if list_name not in archive:
            continue
        items = archive[list_name]
        if not isinstance(items, list):
            errors.append(f"{list_name} must be a list")
            continue
        min_items = spec.get("min_items", 0)
        if len(items) < min_items:
            errors.append(f"{list_name} needs >= {min_items} items, got {len(items)}")
        req_fields = spec.get("required_fields", [])
        for i, item in enumerate(items):
            if isinstance(item, dict):
                for rf in req_fields:
                    if rf not in item:
                        errors.append(f"{list_name}[{i}] missing field: {rf}")
        if spec.get("at_least_one_test"):
            has_test = any(
                isinstance(item, dict) and item.get("use_as_test") is True
                for item in items
            )
            if not has_test:
                errors.append(f"{list_name} must have at least one use_as_test: true")

    return errors


# ── AC7: Schema validation tests ──


class TestSchemaExists:
    def test_schema_file_exists(self):
        assert os.path.exists(SCHEMA_PATH)

    def test_schema_has_required_fields(self):
        schema = load_schema()
        assert "required_fields" in schema
        assert len(schema["required_fields"]) >= 10

    def test_schema_has_field_constraints(self):
        schema = load_schema()
        assert "field_constraints" in schema
        assert "source_type" in schema["field_constraints"]
        assert "legal_scan_passed" in schema["field_constraints"]

    def test_schema_has_list_constraints(self):
        schema = load_schema()
        assert "list_constraints" in schema
        for key in ["equations", "inputs", "outputs", "worked_examples"]:
            assert key in schema["list_constraints"]


class TestArchiveValidation:
    def test_valid_archive_passes(self):
        schema = load_schema()
        archive = load_archive()
        errors = validate_archive(archive, schema)
        assert errors == [], f"Validation errors: {errors}"

    def test_missing_required_field_detected(self):
        schema = load_schema()
        archive = load_archive()
        del archive["equations"]
        errors = validate_archive(archive, schema)
        assert any("equations" in e for e in errors)

    def test_invalid_source_type_detected(self):
        schema = load_schema()
        archive = load_archive()
        archive["source_type"] = "invalid_type"
        errors = validate_archive(archive, schema)
        assert any("source_type" in e for e in errors)

    def test_legal_scan_false_detected(self):
        schema = load_schema()
        archive = load_archive()
        archive["legal_scan_passed"] = False
        errors = validate_archive(archive, schema)
        assert any("legal_scan_passed" in e for e in errors)

    def test_short_description_detected(self):
        schema = load_schema()
        archive = load_archive()
        archive["source_description"] = "short"
        errors = validate_archive(archive, schema)
        assert any("source_description" in e for e in errors)

    def test_bad_date_format_detected(self):
        schema = load_schema()
        archive = load_archive()
        archive["extracted_date"] = "March 15, 2026"
        errors = validate_archive(archive, schema)
        assert any("extracted_date" in e for e in errors)

    def test_missing_equation_field_detected(self):
        schema = load_schema()
        archive = load_archive()
        del archive["equations"][0]["latex"]
        errors = validate_archive(archive, schema)
        assert any("latex" in e for e in errors)

    def test_no_test_examples_detected(self):
        schema = load_schema()
        archive = load_archive()
        for ex in archive["worked_examples"]:
            ex["use_as_test"] = False
        errors = validate_archive(archive, schema)
        assert any("use_as_test" in e for e in errors)


# ── AC5: Calculation verification from archive data ──


class TestPileAxialCapacityFromArchive:
    """Verify calculation implementation against dark intelligence archive outputs."""

    def setup_method(self):
        self.archive = load_archive()
        self.example = next(
            ex for ex in self.archive["worked_examples"] if ex.get("use_as_test")
        )
        self.inputs = self.example["inputs"]
        self.expected = self.example["outputs"]
        # Build tolerance map from archive outputs
        self.tolerances = {}
        for out in self.archive["outputs"]:
            self.tolerances[out["symbol"]] = out["tolerance"]

    def test_alpha_factor(self):
        """API RP 2GEO Sec 7.3 — alpha = 0.5 * (Su/sigma_v')^(-0.5)"""
        from scripts.calculations.pile_axial_capacity import compute_alpha

        alpha = compute_alpha(
            su_kpa=self.inputs["undrained_shear_strength_kpa"],
            sigma_v_eff_kpa=self.inputs["effective_overburden_kpa"],
        )
        assert abs(alpha - self.expected["alpha"]) < self.tolerances["alpha"]

    def test_unit_skin_friction(self):
        """f = alpha * Su"""
        from scripts.calculations.pile_axial_capacity import compute_unit_skin_friction

        f = compute_unit_skin_friction(
            su_kpa=self.inputs["undrained_shear_strength_kpa"],
            sigma_v_eff_kpa=self.inputs["effective_overburden_kpa"],
        )
        assert abs(f - self.expected["unit_skin_friction_kpa"]) < self.tolerances["f"]

    def test_skin_friction_capacity(self):
        """Qf = pi * D * f * L"""
        from scripts.calculations.pile_axial_capacity import compute_skin_friction_capacity

        qf = compute_skin_friction_capacity(
            pile_diameter_m=self.inputs["pile_diameter_m"],
            pile_length_m=self.inputs["pile_length_m"],
            su_kpa=self.inputs["undrained_shear_strength_kpa"],
            sigma_v_eff_kpa=self.inputs["effective_overburden_kpa"],
        )
        assert abs(qf - self.expected["skin_friction_capacity_kn"]) < self.tolerances["Q_f"]

    def test_end_bearing_capacity(self):
        """Qp = Nc * Su * Ap"""
        from scripts.calculations.pile_axial_capacity import compute_end_bearing_capacity

        qp = compute_end_bearing_capacity(
            pile_diameter_m=self.inputs["pile_diameter_m"],
            su_kpa=self.inputs["undrained_shear_strength_kpa"],
            nc=self.inputs["bearing_capacity_factor"],
        )
        assert abs(qp - self.expected["end_bearing_capacity_kn"]) < self.tolerances["Q_p"]

    def test_total_axial_capacity(self):
        """Q = Qf + Qp — full end-to-end from archive inputs to expected output"""
        from scripts.calculations.pile_axial_capacity import compute_total_axial_capacity

        q = compute_total_axial_capacity(
            pile_diameter_m=self.inputs["pile_diameter_m"],
            pile_length_m=self.inputs["pile_length_m"],
            su_kpa=self.inputs["undrained_shear_strength_kpa"],
            sigma_v_eff_kpa=self.inputs["effective_overburden_kpa"],
            nc=self.inputs["bearing_capacity_factor"],
        )
        assert abs(q - self.expected["total_axial_capacity_kn"]) < self.tolerances["Q"]
