# Report Composition

Use the component kit to make the report easy to scan first and useful to inspect second.

## Common Structures

### Executive Summary

1. `report-cover`
2. `metric-summary`
3. `insight-callout`
4. `section-header` for findings
5. `bar-chart` or `stacked-bar`
6. `comparison-table`
7. `appendix-notes`

### Data Analysis Report

1. `report-cover`
2. `section-header` for question and method
3. `metric-summary`
4. `data-table`
5. `bar-chart`, `sparkline-panel`, or `donut-progress`
6. `subsection-header` for interpretation
7. `appendix-notes`

### Operational Status Report

1. `report-cover`
2. `metric-summary`
3. `insight-callout` for risk or decision
4. `timeline`
5. `comparison-table` for owners, status, and next actions
6. `appendix-notes`

## Heading Rules

- Use one `h1` in `report-cover`.
- Use `h2` in `section-header`.
- Use `h3` in `subsection-header`.
- Do not skip heading levels for visual size. Change CSS classes if the visual scale needs adjustment.

## Content Rules

- Start with the report scope, date range, source, or audience-specific framing.
- Put the most decision-relevant information before supporting detail.
- Use short section summaries before dense tables.
- Keep labels concrete: prefer "Revenue by Segment" over "Chart 1".
- Use appendix notes for assumptions, caveats, methodology, definitions, and source limitations.

## Accessibility Checks

- Provide table headers with `scope="col"` and row labels with `scope="row"` when useful.
- Add `aria-label` or visible captions to charts.
- Do not rely on color alone for status; include text labels such as "On track", "At risk", or "Blocked".
- Keep chart values available as text near the visual mark or in a nearby table.
