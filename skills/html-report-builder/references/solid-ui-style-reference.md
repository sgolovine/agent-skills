# Solid UI Style Reference

Use Solid UI as a visual and architectural reference for report styling: reusable components are copied into the project, themed through tokens, and customized locally. Do not require Solid, Kobalte, corvu, Tailwind, or the Solid UI CLI for static report output unless the user explicitly asks for a Solid app.

Reference URL: `https://www.solid-ui.com/docs/introduction`

## Principles To Preserve

- Copy component code into the report artifact and adapt it locally.
- Keep primitives composable: card, badge, callout, table, separator, grid, and timeline blocks should work independently.
- Style through design tokens first, then component classes, then one-off inline values only for data-driven chart values.
- Use subtle borders, muted backgrounds, compact radius, restrained shadows, clear focus/hover states when interactive, and status badges with text labels.
- Prefer neutral surfaces with one strong accent color and semantic state colors.

## Component Shape Guidance

| Solid UI Pattern | Report Kit Equivalent | Styling Notes |
| --- | --- | --- |
| Card | `.metric-card`, `.chart-panel`, `.note-card`, `.report-section` | Use white or card surface, 1px border, 8px radius, modest padding. |
| Badge / Badge Delta | `.status-pill`, `.metric-delta` | Use small rounded pills with text and semantic color. |
| Callout | `.callout` | Use border-left accent and compact explanatory text. |
| Table / Data Table | `.table-wrap table` | Use clear headers, row borders, numeric alignment, and overflow wrapper. |
| Separator | Section borders and table borders | Prefer real spacing and borders over decorative lines. |
| Timeline | `.timeline`, `.timeline-item` | Use compact milestone rows with date and body. |
| Grid / Flex | `.grid`, `.metric-grid`, `.report-meta` | Use responsive grid utilities and wrap metadata. |

## Token Pattern

Use shadcn-style HSL tokens for the base layer, then report aliases for readability in static CSS:

```css
:root {
  --background: 220 25% 97%;
  --foreground: 222 47% 11%;
  --card: 0 0% 100%;
  --border: 214 32% 91%;
  --primary: 221 83% 53%;
  --accent: 214 95% 93%;

  --report-bg: hsl(var(--background));
  --report-text: hsl(var(--foreground));
  --report-surface: hsl(var(--card));
  --report-border: hsl(var(--border));
  --report-accent: hsl(var(--primary));
  --report-accent-soft: hsl(var(--accent));
}
```

## Static HTML Adaptation

- Use normal HTML elements instead of framework components.
- Preserve accessibility semantics that Solid UI component examples imply: labels, captions, roles, visible states, and keyboard-friendly controls when interactive controls exist.
- Do not paste Tailwind utility-heavy markup into standalone reports unless the final report includes a Tailwind build path.
- Convert component variants into classes such as `.status-pill.good`, `.metric-delta.negative`, or scoped theme classes.
