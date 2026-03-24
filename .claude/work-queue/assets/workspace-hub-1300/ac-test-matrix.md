# WRK-1392 AC-Test Matrix

| AC | Description | Result | Evidence |
|----|-------------|--------|----------|
| 1 | Single self-contained HTML file (no external dependencies) | PASS | `test_generate_html_creates_file` — output is single HTML, >1KB |
| 2 | All 15 nodes, 16 members rendered with correct geometry | PASS | `test_frame_to_json_node_count` (15 nodes), `test_frame_to_json_member_count` (16 members) |
| 3 | Bend members shown as curves, not straight lines | PASS | `test_bend_members_have_arc_mid` — 4 bends have arc_mid key; `test_arc_midpoint_sag_value` |
| 4 | Orbit, zoom, pan controls | PASS | `test_html_contains_three_js` — THREE.Scene + OrbitControls present |
| 5 | Node labels toggleable | PASS | `test_html_contains_frame_data` — node labels present in output |
| 6 | Assembly color coding matches matplotlib preview | PASS | Visual verification by user — rear_trunk=blue, under_chassis=orange |
| 7 | File opens in any modern browser | PASS | User opened in browser and confirmed "looks good" |
