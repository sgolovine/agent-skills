# Theming

Retheme reports through CSS custom properties. Keep component markup stable and change tokens first. The default theme is a grayscale printed form; preserve its square geometry, border hierarchy, compact type, and shared edges even when adjusting colors.

## Token Groups

Edit these variables in `assets/report-kit/report.css` or override them in the final report:

| Token Group | Variables |
| --- | --- |
| Palette | `--report-ink`, `--report-muted`, `--report-bg`, `--report-surface`, `--report-border`, `--report-shade`, `--report-white` |
| Rules | `--report-outer-rule`, `--report-header-rule`, `--report-inner-rule` |
| Layout | `--report-max-width`, `--report-density` |

## Theme Pattern

Use a scoped class when one document needs multiple looks or when preserving the base kit. Keep the example neutral and grayscale:

```css
.report-theme-soft-gray {
  --report-bg: #eeeeee;
  --report-shade: #d9d9d9;
  --report-muted: #444444;
}
```

Apply it to `<body class="report-theme-soft-gray">` or a wrapper.

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
