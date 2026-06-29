# Component Directory

This file is the report kit directory and the single source of truth for what components exist. Component markup lives only in `assets/report-kit/components.html`; copy snippets from there by `data-component`.

## Asset Inventory

| Item | Path | Purpose |
| --- | --- | --- |
| Starter report | `assets/report-kit/report-template.html` | Base HTML document for a new report. |
| Component library | `assets/report-kit/components.html` | Canonical markup snippets, each marked with `data-component`. |
| Theme CSS | `assets/report-kit/report.css` | CSS variables, responsive rules, print styles, and component classes. |

## Reference Inventory

| Reference | Load When |
| --- | --- |
| `references/report-composition.md` | Choosing a report structure, section order, heading hierarchy, or accessibility checks. |
| `references/data-display.md` | Choosing tables, metrics, chart types, chart fallbacks, or data formatting. |
| `references/theming.md` | Retheming, changing density, making print-ready output, or adapting responsiveness. |
| `references/solid-ui-style-reference.md` | Creating or changing visual style using Solid UI as the theme and component-shape reference. |

## Component Catalog

| Component ID | Category | Use When | Notes |
| --- | --- | --- | --- |
| `report-cover` | Structure | Opening a report with title, subtitle, scope, date, and metadata. | Use once near the top. |
| `section-header` | Headings | Starting a major report section with kicker, title, and summary. | Keeps heading hierarchy consistent. |
| `subsection-header` | Headings | Introducing a smaller topic inside a section. | Use below a section header. |
| `metric-summary` | Metrics | Showing 3-4 key measures before deeper detail. | Supports positive, negative, and neutral deltas. |
| `insight-callout` | Narrative | Highlighting a takeaway, risk, decision, or recommendation. | Pair with evidence or next action. |
| `comparison-table` | Tables | Comparing options, segments, vendors, or scenarios. | Best for short text and mixed qualitative values. |
| `data-table` | Tables | Showing exact rows and values from source data. | Wrap with `.table-wrap` for overflow on mobile. |
| `bar-chart` | Charts | Comparing category magnitudes with simple percentages or normalized values. | Set `--value` from `0%` to `100%`. |
| `stacked-bar` | Charts | Showing composition across 2-5 parts. | Segment widths should add to `100%`. |
| `sparkline-panel` | Charts | Showing a compact trend beside a headline number. | Use SVG points for the trend line. |
| `donut-progress` | Charts | Showing one proportional value such as completion or share. | Set `--percent` as a CSS angle percent. |
| `timeline` | Process | Showing phases, milestones, events, or status history. | Keep entries short. |
| `appendix-notes` | Appendix | Capturing methodology, assumptions, definitions, or footnotes. | Use at the end. |

## Selection Rules

- For a general report, use `report-cover`, `metric-summary`, `section-header`, one table, one chart, and `appendix-notes`.
- For an executive report, lead with `metric-summary` and `insight-callout`, then add supporting `data-table` or `bar-chart` evidence.
- For analysis reports, use more `section-header` and `subsection-header` blocks, keep exact values in `data-table`, and add charts only where they reduce comparison effort.
- For printable reports, load `references/theming.md` and keep component widths within the template shell.
- For new visual styling, load `references/solid-ui-style-reference.md` and keep the copy-paste, themeable component model.
