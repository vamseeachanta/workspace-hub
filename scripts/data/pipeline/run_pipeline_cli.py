"""CLI entry point for running ETL pipelines."""

import argparse
import logging
import sys
from pathlib import Path

logger = logging.getLogger("pipeline")

REPO_ROOT = Path(__file__).resolve().parents[3]
STATE_DIR = REPO_ROOT / "config" / "data" / "pipeline-state"
MANIFEST_PATH = REPO_ROOT / "config" / "data" / "pipeline-manifest.yaml"


def _build_eia_pipeline():
    """Build EIA production pipeline with live client."""
    from data.pipeline.pipelines.eia_production import (
        EIAProductionExtractor,
        EIAProductionLoader,
        EIAProductionTransformer,
    )
    from data.pipeline.manifest import ManifestManager
    from data.pipeline.pipeline import PipelineOrchestrator
    from data.pipeline.state import PipelineState

    try:
        from worldenergydata.eia.client import EIAFeedClient
        client = EIAFeedClient()
    except ImportError:
        logger.error("worldenergydata not importable — check PYTHONPATH")
        sys.exit(1)

    return PipelineOrchestrator(
        extractor=EIAProductionExtractor(client=client),
        transformer=EIAProductionTransformer(),
        loader=EIAProductionLoader(output_dir=REPO_ROOT / "data" / "eia"),
        state=PipelineState(STATE_DIR),
        manifest=ManifestManager(MANIFEST_PATH),
        pipeline_name="eia_production",
        source_url="https://api.eia.gov/v2/petroleum/sum/snd/w",
        refresh_cadence="weekly",
        ttl_hours=168,
    )


def _build_bsee_pipeline():
    """Build BSEE wells pipeline from local CSV."""
    from data.pipeline.pipelines.bsee_wells import (
        BSEEWellsExtractor,
        BSEEWellsLoader,
        BSEEWellsTransformer,
    )
    from data.pipeline.manifest import ManifestManager
    from data.pipeline.pipeline import PipelineOrchestrator
    from data.pipeline.state import PipelineState

    csv_path = REPO_ROOT / "data" / "modules" / "bsee" / "bsee_wells.csv"
    return PipelineOrchestrator(
        extractor=BSEEWellsExtractor(csv_path=csv_path),
        transformer=BSEEWellsTransformer(),
        loader=BSEEWellsLoader(output_dir=REPO_ROOT / "data" / "bsee"),
        state=PipelineState(STATE_DIR),
        manifest=ManifestManager(MANIFEST_PATH),
        pipeline_name="bsee_wells",
        source_url="https://www.data.bsee.gov/",
        refresh_cadence="monthly",
        ttl_hours=720,
    )


def _build_yfinance_pipeline():
    """Build yfinance prices pipeline with fixture fallback."""
    from data.pipeline.pipelines.yfinance_prices import (
        YFinancePricesExtractor,
        YFinancePricesLoader,
        YFinancePricesTransformer,
    )
    from data.pipeline.manifest import ManifestManager
    from data.pipeline.pipeline import PipelineOrchestrator
    from data.pipeline.state import PipelineState

    fixture = REPO_ROOT / "tests" / "data" / "pipeline" / "fixtures" / "yfinance_ohlcv.json"
    return PipelineOrchestrator(
        extractor=YFinancePricesExtractor(
            tickers=["AAPL", "MSFT", "XOM"],
            fixture_path=fixture if fixture.exists() else None,
        ),
        transformer=YFinancePricesTransformer(),
        loader=YFinancePricesLoader(output_dir=REPO_ROOT / "data" / "stocks" / "cache"),
        state=PipelineState(STATE_DIR),
        manifest=ManifestManager(MANIFEST_PATH),
        pipeline_name="yfinance_prices",
        source_url="https://finance.yahoo.com/",
        refresh_cadence="daily",
        ttl_hours=4,
    )


PIPELINE_BUILDERS = {
    "eia_production": _build_eia_pipeline,
    "bsee_wells": _build_bsee_pipeline,
    "yfinance_prices": _build_yfinance_pipeline,
}


def main():
    parser = argparse.ArgumentParser(description="Run an ETL pipeline")
    parser.add_argument("pipeline", choices=PIPELINE_BUILDERS.keys())
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        orch = PIPELINE_BUILDERS[args.pipeline]()
        result = orch.run(force_refresh=args.force_refresh)
        if result["skipped"]:
            logger.info("Pipeline %s skipped (cache fresh)", args.pipeline)
        else:
            logger.info(
                "Pipeline %s complete: %d records → %s",
                args.pipeline, result["record_count"], result["output_path"],
            )
    except Exception as exc:
        logger.error("Pipeline %s failed: %s", args.pipeline, exc)
        sys.exit(2)


if __name__ == "__main__":
    main()
