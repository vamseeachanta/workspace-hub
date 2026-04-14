import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "build-index-other-bucket-packs.py"
)
SPEC = spec_from_file_location("build_index_other_bucket_packs", SCRIPT_PATH)
MODULE = module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_classify_doc_class_prefers_explicit_codes() -> None:
    assert (
        MODULE.classify_doc_class(
            "disciplines/drilling/projects/x/00_inbox/Project/CAL/31057-CAL-1006-02 motion traces.xlsm"
        )
        == "calculation"
    )
    assert (
        MODULE.classify_doc_class(
            "disciplines/drilling/projects/x/05_reports/Project/PRP/7200002089 2H RFQ.pdf"
        )
        == "procurement"
    )


def test_collect_pack_records_filters_prefix_and_doc_class(tmp_path: Path) -> None:
    index_path = tmp_path / "index.jsonl"
    index_path.write_text(
        "\n".join(
            [
                '{"file_path":"disciplines/drilling/projects/a/00_inbox/A/CAL/doc-1.xlsm"}',
                '{"file_path":"disciplines/drilling/projects/a/00_inbox/A/CAL/doc-2.xlsx"}',
                '{"file_path":"disciplines/drilling/projects/a/05_reports/A/CAL/doc-3.pdf"}',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    pack_spec = MODULE.PackSpec(
        pack_id="test-pack",
        path_prefix="disciplines/drilling/projects/a/00_inbox/A/CAL",
        allowed_doc_classes=("calculation", "spreadsheet"),
        proposed_domain="drilling",
        proposed_status="reference",
        triage_action="reclassify_now",
        priority=1,
        rationale="test",
    )

    records = MODULE.collect_pack_records(index_path=index_path, pack_spec=pack_spec)
    assert records == [
        "disciplines/drilling/projects/a/00_inbox/A/CAL/doc-1.xlsm",
        "disciplines/drilling/projects/a/00_inbox/A/CAL/doc-2.xlsx",
    ]
