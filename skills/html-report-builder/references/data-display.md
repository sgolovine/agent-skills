# Data Display

Choose the least complex display that preserves the meaning of the source data.

## Tables

Use `comparison-table` when rows are options, scenarios, vendors, segments, or recommendations. Keep cells concise and use status pills only for categorical states.

Use `data-table` when exact values matter. Preserve units in headers or cells, align numeric values consistently, and keep source values available even when also charted.

For wide tables:

- Keep them inside `.table-wrap`.
- Prefer fewer columns over smaller text.
- Move long notes below the table when they reduce readability.

## Metrics

Use `metric-summary` for 3-4 headline values. Each metric should include:

- a plain-language label,
- a value with units,
- an optional delta or qualifier,
- a short caption only when the value is otherwise ambiguous.

## Basic Charts

The kit supports static chart components without JavaScript.

| Chart | Component ID | Good For | Avoid When |
| --- | --- | --- | --- |
| Horizontal bars | `bar-chart` | Ranking categories or comparing normalized values. | Values require precise axes or many categories. |
| Stacked bar | `stacked-bar` | Showing a whole split into parts. | More than 5 segments or negative values. |
| Sparkline | `sparkline-panel` | Showing a compact trend next to a metric. | Exact point values must be read from the chart. |
| Donut progress | `donut-progress` | One completion, share, or target progress value. | Comparing several categories. |

## Chart Data Rules

- Store chart values in visible text as well as visual attributes.
- For `bar-chart`, set `--value` to a percentage width and keep the label value visible.
- For `stacked-bar`, ensure segment widths add to `100%`.
- For `sparkline-panel`, update the SVG `polyline` points and the adjacent summary text.
- For `donut-progress`, set `--percent` to a percent value and update the center label.

## When To Use A Library

Use a charting library only when the report needs interaction, tooltips, zooming, many series, precise axes, or chart types outside this kit. Keep a static table fallback when the report must print or be archived.
