# Theming

Retheme reports through CSS custom properties. Keep component markup stable and change tokens first.

## Token Groups

Edit these variables in `assets/report-kit/report.css` or override them in the final report:

| Token Group | Variables |
| --- | --- |
| Base HSL | `--background`, `--foreground`, `--card`, `--card-foreground`, `--muted`, `--muted-foreground`, `--border`, `--primary`, `--primary-foreground`, `--accent`, `--accent-foreground` |
| Report Aliases | `--report-bg`, `--report-surface`, `--report-border`, `--report-shadow`, `--report-text`, `--report-muted`, `--report-subtle`, `--report-accent`, `--report-accent-strong`, `--report-accent-soft` |
| State | `--report-success`, `--report-warning`, `--report-danger`, `--report-info` |
| Layout | `--report-max-width`, `--report-radius`, `--report-gap`, `--report-density` |

## Theme Pattern

Use a scoped class when one document needs multiple looks or when preserving the base kit:

```css
.report-theme-forest {
  --primary: 151 45% 34%;
  --accent: 145 39% 92%;
  --accent-foreground: 151 56% 20%;
}
```

Apply it to `<body class="report-theme-forest">` or a wrapper.

## Density

- For executive reports, keep the default spacing.
- For dense operational reports, reduce `--report-gap` and `--report-density`.
- Do not shrink fonts below readable report text sizes; use fewer columns before using tiny text.

## Print

The CSS includes print rules for white backgrounds, reduced shadows, visible borders, and page breaks. For print-focused reports:

- Keep charts simple.
- Avoid relying on sticky table behavior.
- Add `break-inside: avoid` to any custom block that must stay together.
- Use absolute or inlined asset paths so printed/PDF output does not lose styles.
