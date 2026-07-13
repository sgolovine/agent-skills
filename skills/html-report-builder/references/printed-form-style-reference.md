# Printed-Form Style Reference

Use this visual system for the report kit regardless of report subject. It defines appearance only; source all wording, labels, examples, and data from the user's material or generic placeholders.

## Visual Character

- Render the report as one compact printed form on white paper over a light-gray screen background.
- Use black rules, white surfaces, gray section bars, dense tables, and minimal ornament.
- Keep geometry rectangular. Do not add rounded cards, pill shapes, shadows, decorative gradients, imagery, or icons.
- Make adjacent sections share edges through the report grid instead of floating as separate cards.
- Keep charts monochrome. Encode status with labels, fill weight, borders, or patterns rather than color alone.

## Tokens

```css
:root {
  --report-ink: #000000;
  --report-muted: #333333;
  --report-bg: #d8d8d8;
  --report-surface: #ffffff;
  --report-border: #000000;
  --report-shade: #e6e6e6;
  --report-white: #ffffff;
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
| Cover | `2px` black outer border, divided banner cells, compact title, metadata block, and a ruled subtitle row. |
| Section | White cell in a two-column shared-edge grid; use `.wide` only when content needs both columns. |
| Section header | Gray fill, `1.5px` bottom rule, numbered or coded kicker, small uppercase title. |
| Table | Collapsed borders, short uppercase headers, `1px` row rules, tight cell padding, tabular numerals. |
| Metric | White grid cell with hard dividers; large but compact numeric value and small label. |
| Status | Square bordered label. Use white, gray, or black fills with visible text. |
| Callout | Gray or white block with a heavy black left rule; no radius or shadow. |
| Chart | Black marks on white or gray tracks, square endpoints, explicit text values, grayscale legend swatches. |
| Timeline / notes | Compact divided rows or cells with the same rule hierarchy as tables. |

## Responsive And Print Behavior

- Keep the report at a `900px` maximum width on screen.
- Collapse the two-column report grid below `820px`.
- Wrap the cover metadata and simplify charts below `560px`.
- On print, use a white page background, full available width, visible black rules, and `break-inside: avoid` on compact components.

## Style-Only Boundary

- Use generic report class names such as `.report-cover`, `.report-grid`, `.metric-card`, and `.table-wrap`.
- Do not reuse names tied to the reference project's language, topics, examples, or content model.
- Do not copy reference headings, body text, data rows, identifiers, links, or filenames.
- Uppercase labels with CSS; do not alter the source wording merely to imitate the reference.
