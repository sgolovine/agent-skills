---
name: html-report-builder
description: Build standalone HTML reports from reusable, themeable components in a compact grayscale printed-form style. Use when Codex needs to create, assemble, style, or improve an HTML report, static dashboard report, executive summary, analysis page, data table report, printable report, or report with headings, subheadings, tables, metrics, callouts, and basic charts.
---

# HTML Report Builder

## Operating Principle

Assemble reports from the component kit, then adapt the content, hierarchy, and data to the user's source material while preserving the kit's compact printed-form visual system.

## Workflow

1. Resolve the report purpose, audience, source data, output path, and whether the result should be a single self-contained HTML file or an HTML file with adjacent assets.
2. Read `references/component-directory.md` first. Treat it as the directory and single source of truth for available components and asset locations.
3. For a new report, start from `assets/report-kit/report-template.html`. For an existing report, copy or merge `assets/report-kit/report.css`.
4. Copy component markup only from `assets/report-kit/components.html`, using the `data-component` IDs listed in the directory. Keep semantic HTML, ARIA labels, table headers, and CSS class names intact unless the report requires a clear change.
5. Load only the focused reference files needed for the task:
   - `references/report-composition.md` for report structure, heading hierarchy, and section order.
   - `references/data-display.md` for tables, metrics, and basic chart choices.
   - `references/theming.md` for CSS variables, theming, responsive behavior, and print styling.
   - `references/printed-form-style-reference.md` when creating or changing theme, styling, density, component shape, or visual treatment.
6. Keep the default style stark, grayscale, square, dense, and print-oriented. Transfer only visual rules from any style reference; never copy its subject matter, wording, labels, examples, or domain-specific class names into a report.
7. Prefer static, dependency-free charts from the kit for simple comparisons, distributions, trends, and proportions. Use a charting library only when the user needs interaction, precise axes, large datasets, or chart types outside the kit.
8. Theme by editing CSS custom properties in `:root` or adding a scoped theme class. Preserve the strong rules, square geometry, compact type scale, and shared-edge layout unless the user explicitly requests a different style.
9. Before finishing, verify the HTML renders cleanly in a browser when feasible. Check desktop and mobile widths, print styles for printable reports, table overflow, chart labels, contrast, and that no text overlaps or clips. Confirm the report contains only the user's content and generic kit placeholders, never content from a style reference.

## Resource Map

| Resource | Use |
| --- | --- |
| `references/component-directory.md` | Start here. Catalog of every component, source file, and intended use. |
| `references/report-composition.md` | Report outlines, heading rules, page structure, and accessibility checks. |
| `references/data-display.md` | Guidance for tables, metric cards, CSS charts, SVG sparklines, and chart fallbacks. |
| `references/theming.md` | CSS variables, theme scopes, print behavior, and responsive rules. |
| `references/printed-form-style-reference.md` | Default visual rules for grayscale palette, square components, strong borders, compact typography, shared edges, and print density. |
| `assets/report-kit/report-template.html` | Starter report shell with linked CSS and example sections. |
| `assets/report-kit/report.css` | Themeable CSS tokens and component styles. |
| `assets/report-kit/components.html` | Canonical component markup. Copy snippets from this file by `data-component`. |

## Report Requirements

- Use one `h1` per report and preserve a logical heading order.
- Keep the first viewport useful: title, context, date or scope, and key takeaways.
- Put raw data in tables when exact values matter; add chart summaries for visual scanning.
- Keep CSS variables near the top of the file so downstream agents can retheme quickly.
- Use uppercase styling through CSS rather than rewriting source content in uppercase.
- For standalone delivery, inline or copy the CSS into the final artifact when external asset paths would break.
