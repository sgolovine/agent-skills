# Theming

Retheme reports through CSS custom properties. Keep component markup stable and change tokens first. The default theme is a high-contrast printed form with one punchy accent; preserve its square geometry, border hierarchy, compact type, and shared edges when adjusting colors.

## Token Groups

Edit these variables in `assets/report-kit/report.css` or override them in the final report:

| Token Group | Variables |
| --- | --- |
| Palette | `--report-ink`, `--report-muted`, `--report-bg`, `--report-surface`, `--report-border`, `--report-shade`, `--report-white`, `--report-accent`, `--report-accent-ink` |
| Rules | `--report-outer-rule`, `--report-header-rule`, `--report-inner-rule` |
| Layout | `--report-max-width`, `--report-density` |

## Color Budget

- Use one punchy accent to distinguish section headers, headings, callout rules, and selected chart marks.
- Use no more than four distinct colors on a page, including neutral text, paper, background fills, and the accent. Alias multiple tokens to the same value instead of adding subtle extra shades.
- If dense data genuinely needs more than four colors, ask the user for an exception before adding them. Without an exception, distinguish series with labels, patterns, borders, or line styles.
- Keep text contrast at WCAG AA or better and never use color as the only status or data cue.

## Theme Pattern

Use a scoped class when one document needs multiple looks or when preserving the base kit. This example retains the four-color budget:

```css
.report-theme-orange {
  --report-ink: #202020;
  --report-muted: #202020;
  --report-bg: #ece8e1;
  --report-shade: #ece8e1;
  --report-surface: #ffffff;
  --report-white: #ffffff;
  --report-accent-ink: #ffffff;
  --report-border: #202020;
  --report-accent: #b93800;
}
```

Apply it to `<body class="report-theme-orange">` or a wrapper.

## Density

- Keep the default compact spacing for ordinary reports.
- Adjust `--report-density` slightly for unusually sparse or dense material.
- Use fewer columns before shrinking text below the default compact scale.

## Print

The CSS includes print rules for a white page background, visible borders, and page breaks. For print-focused reports:

- Keep charts simple.
- Avoid relying on sticky table behavior.
- Add `break-inside: avoid` to any custom block that must stay together.
- Use absolute or inlined asset paths so printed/PDF output does not lose styles.
