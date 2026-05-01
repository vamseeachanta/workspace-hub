#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

stamp = datetime.now().astimezone().isoformat(timespec='seconds')
entries = [
    ("digitalmodel-suction-pile-sizing", Path("/mnt/ace/digitalmodel/references/suction-pile-sizing/MOVE-LOG.md"), 4, 235464, "/mnt/ace/digitalmodel/references/suction-pile-sizing", "/mnt/ace/digitalmodel/references/suction-pile-sizing/_from_elements", ".planning/intel/elements-ingest/dedupe-merge-assessment/01-digitalmodel-suction-pile-sizing.option-d-hardlink-merge.log"),
    ("assethold-casa-grande-77017", Path("/mnt/ace/assethold/casa-grande-77017/MOVE-LOG.md"), 3, 16703705, "/mnt/ace/assethold/casa-grande-77017", "/mnt/ace/assethold/casa-grande-77017/_from_elements", ".planning/intel/elements-ingest/dedupe-merge-assessment/02-assethold-casa-grande-77017.option-d-hardlink-merge.log"),
    ("digitalmodel-qgis", Path("/mnt/ace/digitalmodel/tools/qgis/MOVE-LOG.md"), 3, 398492107, "/mnt/ace/digitalmodel/tools/qgis", "/mnt/ace/digitalmodel/tools/qgis/_from_elements", ".planning/intel/elements-ingest/dedupe-merge-assessment/03-digitalmodel-qgis.option-d-hardlink-merge.log"),
    ("digitalmodel-riser-toolbox", Path("/mnt/ace/digitalmodel/references/riser-toolbox/MOVE-LOG.md"), 8, 510241677, "/mnt/ace/digitalmodel/references/riser-toolbox", "/mnt/ace/digitalmodel/references/riser-toolbox/_from_elements", ".planning/intel/elements-ingest/dedupe-merge-assessment/04-digitalmodel-riser-toolbox.option-d-hardlink-merge.log"),
    ("doris-62092-sesa", Path("/mnt/ace/doris/62092_sesa/MOVE-LOG.md"), 418, 1465267463, "/mnt/ace/doris/62092_sesa", "/mnt/ace/doris/62092_sesa/_from_elements", ".planning/intel/elements-ingest/dedupe-merge-assessment/05-doris-62092-sesa.option-d-hardlink-merge.log"),
    ("doris-university", Path("/mnt/ace/doris/training/MOVE-LOG.md"), 564, 11060962662, "/mnt/ace/doris/training", "/mnt/ace/doris/training/_from_elements", ".planning/intel/elements-ingest/dedupe-merge-assessment/06-doris-university.option-d-hardlink-merge.log"),
    ("doris-codes-specs", Path("/mnt/ace/doris/codes/_from_elements/MOVE-LOG.md"), 35197, 26411658490, "/mnt/ace/doris/codes", "/mnt/ace/doris/codes/_from_elements/codes-doris", ".planning/intel/elements-ingest/dedupe-merge-assessment/07-doris-codes-specs.option-d-hardlink-merge.log"),
    ("acma-projects-31522-woodfibre", Path("/mnt/ace/acma-projects/31522-woodfibre-lng/MOVE-LOG.md"), 5364, 1879405139855, "/mnt/ace/acma-projects/31522-woodfibre-lng", "/mnt/ace/acma-projects/31522-woodfibre-lng/_from_elements", ".planning/intel/elements-ingest/dedupe-merge-assessment/08-acma-projects-31522-woodfibre.option-d-hardlink-merge.log"),
]

for bucket, path, files, bytes_, parent, stage, log in entries:
    block = f"""

## Option D dedupe-merge completed — {stamp}

- Related issue: https://github.com/vamseeachanta/workspace-hub/issues/2526
- Bucket: `{bucket}`
- Final parent target: `{parent}`
- Retained staging source: `{stage}`
- Merge method: `rsync -aHAX --ignore-existing --link-dest=<stage> <stage>/ <parent>/`
- Merge behavior: hardlink-preserving parent materialization; no source/staging deletion
- Files verified in parent: {files:,}
- Bytes represented: {bytes_:,}
- Verification: PASS — same relative path, same size, same device+inode hardlink identity
- Merge log: `{log}`
- Verification summary: `.planning/intel/elements-ingest/option-d-merge-verification-summary.tsv`
- Retention: keep `/mnt/elements` source and `_from_elements/` staging until retention gate is explicitly closed
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(block)
    print(path)
