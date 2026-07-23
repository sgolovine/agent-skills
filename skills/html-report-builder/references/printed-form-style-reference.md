# Printed-Form Style Reference

Use this visual system for the report kit regardless of report subject. It defines appearance only; source all wording, labels, examples, and data from the user's material or generic placeholders.

## Visual Character

- Render the report as one compact printed form on white paper over a light-gray screen background.
- Use dark rules, white surfaces, restrained neutral fills, dense tables, and minimal ornament.
- Add one punchy accent color to section bars, headings, callout rules, and selected data marks so the hierarchy is quickly scannable.
- Keep geometry rectangular. Do not add rounded cards, pill shapes, shadows, decorative gradients, imagery, or icons.
- Make adjacent sections share edges through the report grid instead of floating as separate cards.
- Use no more than four distinct colors on the page, including neutrals and backgrounds. Ask the user before exceeding this limit for dense data.
- Never encode meaning with color alone. Pair status and chart colors with labels, values, borders, patterns, or line styles.

## Tokens

```css
:root {
  --report-ink: #172033;
  --report-muted: #172033;
  --report-bg: #e7ecf2;
  --report-surface: #ffffff;
  --report-border: #172033;
  --report-shade: #e7ecf2;
  --report-white: #ffffff;
  --report-accent: #0057b8;
  --report-accent-ink: #ffffff;
  --report-max-width: 900px;
  --report-outer-rule: 2px;
  --report-header-rule: 1.5px;
  --report-inner-rule: 1px;
}
```

## Typography

- Use `"Helvetica Neue", Helvetica, Arial, "Liberation Sans", sans-serif`.
- Set body text to `13px` with a `1.25` line height.
- Keep the title compact, bold, and uppercase through CSS.
- Style section titles, table headers, metadata labels, and metric labels as small uppercase administrative text.
- Use fixed compact sizes rather than viewport-scaled display type.

## Component Treatment

| Component | Treatment |
| --- | --- |
| Cover | `2px` dark outer border, divided banner cells, an accent report-code block, compact title, metadata block, and a ruled subtitle row. |
| Section | White cell in a two-column shared-edge grid; use `.wide` only when content needs both columns. |
| Section header | Accent fill with high-contrast text, `1.5px` bottom rule, numbered or coded kicker, and small uppercase title. |
| Table | Collapsed borders, short uppercase headers, `1px` row rules, tight cell padding, tabular numerals. |
| Metric | White grid cell with hard dividers; large but compact numeric value and small label. |
| Status | Square bordered label with visible text; color may reinforce but never replace the label. |
| Callout | Neutral or white block with a heavy accent left rule; no radius or shadow. |
| Chart | Accent and neutral marks on white or neutral tracks, square endpoints, explicit text values, and labeled legend swatches. |
| Timeline / notes | Compact divided rows or cells with the same rule hierarchy as tables. |

## Responsive And Print Behavior

- Keep the report at a `900px` maximum width on screen.
- Collapse the two-column report grid below `820px`.
- Wrap the cover metadata and simplify charts below `560px`.
- On print, use a white page background, full available width, visible dark rules, preserve the accent when available, and use `break-inside: avoid` on compact components.

## Style-Only Boundary

- Use generic report class names such as `.report-cover`, `.report-grid`, `.metric-card`, and `.table-wrap`.
- Do not reuse names tied to the reference project's language, topics, examples, or content model.
- Do not copy reference headings, body text, data rows, identifiers, links, or filenames.
- Uppercase labels with CSS; do not alter the source wording merely to imitate the reference.
