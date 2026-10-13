# Current vs Rudder vs Resultant Force Reporting

Use this note when generating or reviewing vessel force reports that compare hull current loads (including OCIMF-style coefficients), rudder-induced loads, and combined resultants.

## Reporting Requirements

Include the comparison in every delivered artifact, not just interactive charts:

1. Machine-readable rows/CSV/JSON with separate fields for:
   - current/hull load: `X_current`, `Y_current`, `N_current`
   - rudder load: `X_rudder`, `Y_rudder`, `N_rudder`
   - total load: `X_total`, `Y_total`, `N_total`
2. Static Markdown/PDF tables with:
   - X ship force
   - Y ship/port force
   - horizontal resultant `sqrt(X^2 + Y^2)`
   - yaw moment about CoG
3. Interactive HTML charts/tables for exploration, but do not treat JavaScript-only controls as sufficient for engineering review.

## Required Conventions Beside the Table/Chart

State these explicitly:

- ship-fixed coordinate axes;
- force sign convention;
- yaw moment reference point, normally CoG;
- positive yaw sign, e.g. bow-to-port;
- whether OCIMF-style coefficients are first-cut comparison loads or vessel-specific validated coefficients.

## Verification Checklist

Before claiming completion:

- preserve already-defined study scope: basecase vessel data, current magnitude, heading/rudder grid, and any rudder-angle cap should be carried through filenames, provenance, manifests, and report titles instead of silently redefining the case;
- independently recompute `X_total = X_current + X_rudder`;
- independently recompute `Y_total = Y_current + Y_rudder`;
- independently recompute `N_total = N_current + N_rudder`;
- independently recompute current, rudder, and total horizontal resultants from their component sums;
- verify row counts against the expected engineering grid and explicitly account for any extra chart/default rows used only for plotting convenience;
- assert generated HTML contains the interactive chart/table IDs;
- assert Markdown/PDF/static report content contains the individual/current/rudder/total comparison table;
- verify JSON/provenance/manifest parse cleanly and every manifest path exists;
- regenerate final HTML/PDF artifacts and smoke-verify them.

## Shareable Report Publication Checklist

When the user needs the force-review report links to send externally, finish with a compact, verified handoff instead of only naming local artifact paths:

1. Commit and push the generated HTML/static artifacts before constructing rendered links.
2. Provide both rendered HTML links and GitHub source links.
   - For checked-in HTML, a stable rendered form is `https://rawcdn.githack.com/<owner>/<repo>/<commit>/<path-to-report.html>`.
   - Use the pushed commit SHA in rendered links when possible so the report is immutable for review.
3. Verify the rendered links before reporting them:
   - HTTP status is `200`;
   - content type is `text/html`;
   - browser-render smoke test passes;
   - JavaScript console has zero errors for the report page.
4. Include the exact verification evidence in the final handoff: pushed commit, report URLs, test result summary, and repo sync status.
5. If RawGithack shows an external-content notice on first open, mention that the reviewer should click **Open the page**; do not treat that notice as a report-rendering failure.

## Pitfall Captured

If the user asks to “review the individual and resultant forces,” a dynamic selected-case HTML table is not enough by itself. Add static comparison tables to Markdown/PDF so the review survives printing, PDF export, and non-JavaScript inspection.
