#!/usr/bin/env python3
"""Render skill-lint report JSON as a standalone interactive HTML document."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import sys
from pathlib import Path
from typing import Any


SEVERITY_ORDER = ["critical", "high", "medium", "low", "none", "info"]


def text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def html_text(value: Any, default: str = "") -> str:
    return html.escape(text(value, default))


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def slug(value: Any) -> str:
    raw = text(value, "unknown").lower()
    return "".join(char if char.isalnum() else "-" for char in raw).strip("-") or "unknown"


def normalize_finding(item: Any, index: int) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {
            "section": "Finding",
            "check": "unknown",
            "severity": "info",
            "title": text(item, f"Finding {index + 1}"),
            "file": "",
            "line": None,
            "evidence": "",
            "impact": "",
            "recommended_fix": "",
        }

    category = item.get("category")
    section = item.get("section") or ("Security" if category else "Finding")
    title = item.get("title") or item.get("finding") or f"Finding {index + 1}"
    impact = item.get("impact") or item.get("why_it_matters") or item.get("removal_test") or ""
    recommended = item.get("recommended_fix") or item.get("recommended_action") or ""
    severity = text(item.get("severity"), "info").lower()
    if severity not in SEVERITY_ORDER:
        severity = "info"

    return {
        **item,
        "section": section,
        "check": item.get("check") or ("security-review" if category else "unknown"),
        "severity": severity,
        "title": title,
        "file": item.get("file") or item.get("path") or "",
        "line": item.get("line"),
        "evidence": item.get("evidence") or "",
        "impact": impact,
        "recommended_fix": recommended,
    }


def finding_sort_key(finding: dict[str, Any]) -> tuple[int, str, str]:
    severity = text(finding.get("severity"), "info").lower()
    rank = SEVERITY_ORDER.index(severity) if severity in SEVERITY_ORDER else len(SEVERITY_ORDER)
    return rank, text(finding.get("check")), text(finding.get("title"))


def render_meta(label: str, value: Any) -> str:
    value_text = text(value)
    if not value_text:
        value_text = "Not provided"
    return f"""
      <div class="meta-item">
        <dt>{html_text(label)}</dt>
        <dd>{html.escape(value_text)}</dd>
      </div>
    """


def render_dict_panel(title: str, data: Any) -> str:
    if not isinstance(data, dict) or not data:
        return ""
    rows = "\n".join(
        f"<div class=\"kv\"><span>{html_text(key)}</span><strong>{html_text(value)}</strong></div>"
        for key, value in sorted(data.items())
    )
    return f"""
      <section class="panel">
        <h2>{html_text(title)}</h2>
        <div class="kv-grid">{rows}</div>
      </section>
    """


def render_item_summary(item: Any) -> str:
    if isinstance(item, dict):
        title = item.get("title") or item.get("summary") or item.get("check") or "Item"
        parts = []
        for key in ("check", "file", "files", "reason", "details"):
            if item.get(key):
                parts.append(f"<span><strong>{html_text(key)}:</strong> {html_text(item[key])}</span>")
        details = "".join(parts)
        return f"<li><strong>{html_text(title)}</strong>{details}</li>"
    return f"<li>{html_text(item)}</li>"


def render_list_panel(title: str, items: Any, empty: str) -> str:
    values = as_list(items)
    if not values:
        body = f"<p class=\"empty\">{html_text(empty)}</p>"
    else:
        body = "<ul class=\"detail-list\">" + "\n".join(render_item_summary(item) for item in values) + "</ul>"
    return f"""
      <section class="panel">
        <h2>{html_text(title)}</h2>
        {body}
      </section>
    """


def render_finding_card(finding: dict[str, Any], index: int) -> str:
    finding_id = f"finding-{index + 1}"
    severity = text(finding.get("severity"), "info").lower()
    check = text(finding.get("check"), "unknown")
    section = text(finding.get("section"), "Finding")
    file_path = text(finding.get("file"))
    line = text(finding.get("line"))
    file_label = file_path + (f":{line}" if line and line != "None" else "")
    category = text(finding.get("category"))
    score = text(finding.get("score"))
    extras = []
    if category:
        extras.append(f"<span>Category: {html.escape(category)}</span>")
    if score:
        extras.append(f"<span>Score: {html.escape(score)}</span>")
    extra_html = "".join(extras)
    return f"""
      <article id="{finding_id}" class="finding-card severity-{html.escape(severity)}"
        data-severity="{html.escape(severity)}"
        data-check="{html.escape(slug(check))}">
        <details>
          <summary>
            <span class="severity-dot" aria-hidden="true"></span>
            <span class="finding-main">
              <span class="finding-title">{html_text(finding.get("title"))}</span>
              <span class="finding-subtitle">{html.escape(section)} / {html.escape(check)}</span>
            </span>
            <span class="badge">{html.escape(severity)}</span>
          </summary>
          <div class="finding-detail">
            <div class="detail-strip">
              <span>File: {html.escape(file_label or "Not provided")}</span>
              {extra_html}
            </div>
            <h3>Evidence</h3>
            <pre>{html_text(finding.get("evidence"), "No evidence provided.")}</pre>
            <h3>Impact</h3>
            <p>{html_text(finding.get("impact"), "No impact provided.")}</p>
            <h3>Recommended Fix</h3>
            <p>{html_text(finding.get("recommended_fix"), "No recommendation provided.")}</p>
          </div>
        </details>
      </article>
    """


def filter_button(label: str, attr: str, value: str, count: int | None = None, active: bool = False) -> str:
    count_html = "" if count is None else f"<span>{count}</span>"
    pressed = "true" if active else "false"
    active_class = " active" if active else ""
    return (
        f"<button class=\"filter-btn{active_class}\" type=\"button\" {attr}=\"{html.escape(value)}\" "
        f"aria-pressed=\"{pressed}\">{html_text(label)}{count_html}</button>"
    )


def render_html(report: dict[str, Any]) -> str:
    findings = [normalize_finding(item, index) for index, item in enumerate(as_list(report.get("findings")))]
    findings.sort(key=finding_sort_key)

    generated_at = report.get("generated_at") or dt.datetime.now(dt.timezone.utc).isoformat()
    checks = [text(check) for check in as_list(report.get("checks")) if text(check)]
    if not checks:
        checks = sorted({text(finding.get("check"), "unknown") for finding in findings})

    severity_counts = {severity: 0 for severity in SEVERITY_ORDER}
    for finding in findings:
        severity_counts[text(finding.get("severity"), "info").lower()] += 1
    check_counts: dict[str, int] = {}
    for finding in findings:
        check = text(finding.get("check"), "unknown")
        check_counts[check] = check_counts.get(check, 0) + 1

    severity_buttons = filter_button("All", "data-severity-filter", "all", len(findings), True) + "\n".join(
        filter_button(severity.title(), "data-severity-filter", severity, count)
        for severity, count in severity_counts.items()
        if count
    )
    check_buttons = filter_button("All checks", "data-check-filter", "all", len(findings), True) + "\n".join(
        filter_button(check, "data-check-filter", slug(check), count)
        for check, count in sorted(check_counts.items())
    )

    nav_items = "\n".join(
        f"""
        <button class="nav-item severity-{html_text(finding.get("severity"))}" type="button" data-open="{index + 1}">
          <span>{html_text(finding.get("severity")).upper()}</span>
          <strong>{html_text(finding.get("title"))}</strong>
          <em>{html_text(finding.get("check"))}</em>
        </button>
        """
        for index, finding in enumerate(findings)
    )
    if not nav_items:
        nav_items = '<p class="empty">No findings to navigate.</p>'

    finding_cards = "\n".join(render_finding_card(finding, index) for index, finding in enumerate(findings))
    if not finding_cards:
        finding_cards = '<section class="panel"><p class="empty">No findings were reported.</p></section>'

    metadata = "\n".join(
        [
            render_meta("Target", report.get("target")),
            render_meta("Mode", report.get("mode")),
            render_meta("Checks", ", ".join(checks)),
            render_meta("Verdict", report.get("verdict")),
            render_meta("Generated", generated_at),
        ]
    )

    capabilities = render_dict_panel("Capabilities Observed", report.get("capabilities_observed"))
    fixes = render_list_panel("Fixes", report.get("fixes"), "No fixes recorded.")
    unresolved = render_list_panel("Unresolved", report.get("unresolved"), "No unresolved issues recorded.")
    validation = render_list_panel("Validation", report.get("validation"), "No validation recorded.")
    unknowns = render_list_panel("Unknowns", report.get("unknowns"), "No unknowns recorded.")

    title = text(report.get("title"), "Skill Lint Report")
    summary = text(report.get("summary"), f"{len(findings)} findings.")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html_text(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fa;
      --panel: #ffffff;
      --ink: #111827;
      --muted: #5b6472;
      --line: #d8dde6;
      --focus: #2563eb;
      --critical: #7f1d1d;
      --high: #b91c1c;
      --medium: #b45309;
      --low: #047857;
      --none: #4b5563;
      --info: #1d4ed8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.5 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      padding: 24px clamp(16px, 4vw, 44px);
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{ margin-bottom: 8px; font-size: clamp(24px, 3vw, 40px); }}
    h2 {{ font-size: 16px; margin-bottom: 12px; }}
    h3 {{ font-size: 13px; margin: 16px 0 6px; color: var(--muted); text-transform: uppercase; }}
    .eyebrow {{ color: var(--muted); font-size: 12px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(260px, 340px) minmax(0, 1fr);
      gap: 18px;
      padding: 18px clamp(16px, 4vw, 44px) 44px;
    }}
    aside {{ position: sticky; top: 16px; align-self: start; max-height: calc(100vh - 32px); overflow: auto; }}
    .panel, .finding-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin-bottom: 14px;
      box-shadow: 0 1px 2px rgba(17, 24, 39, .04);
    }}
    .panel {{ padding: 16px; }}
    .filters {{ display: grid; gap: 14px; }}
    .filter-group {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .filter-btn {{
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      border-radius: 6px;
      padding: 7px 9px;
      cursor: pointer;
      display: inline-flex;
      gap: 6px;
      align-items: center;
    }}
    .filter-btn.active {{ border-color: var(--focus); box-shadow: 0 0 0 2px rgba(37, 99, 235, .14); }}
    input[type="search"] {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 10px;
      font: inherit;
    }}
    .nav-list {{ display: grid; gap: 8px; }}
    .nav-item {{
      width: 100%;
      text-align: left;
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 6px;
      padding: 9px;
      cursor: pointer;
      display: grid;
      gap: 2px;
    }}
    .nav-item span {{ font-size: 11px; font-weight: 800; }}
    .nav-item strong {{ font-size: 13px; }}
    .nav-item em {{ color: var(--muted); font-style: normal; font-size: 12px; }}
    .overview {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
    }}
    .meta-item {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fbfcfe;
    }}
    dt {{ color: var(--muted); font-size: 12px; margin-bottom: 4px; }}
    dd {{ margin: 0; overflow-wrap: anywhere; font-weight: 650; }}
    .finding-card details {{ padding: 0; }}
    .finding-card summary {{
      display: grid;
      grid-template-columns: 12px minmax(0, 1fr) auto;
      gap: 12px;
      align-items: center;
      cursor: pointer;
      list-style: none;
      padding: 14px 16px;
    }}
    .finding-card summary::-webkit-details-marker {{ display: none; }}
    .finding-main {{ min-width: 0; }}
    .finding-title {{ display: block; font-weight: 750; overflow-wrap: anywhere; }}
    .finding-subtitle {{ color: var(--muted); font-size: 12px; }}
    .severity-dot {{ width: 10px; height: 10px; border-radius: 50%; background: var(--info); }}
    .badge {{
      border-radius: 999px;
      border: 1px solid var(--line);
      padding: 3px 8px;
      font-size: 12px;
      font-weight: 750;
    }}
    .finding-detail {{ border-top: 1px solid var(--line); padding: 14px 16px 16px; }}
    .detail-strip {{ display: flex; flex-wrap: wrap; gap: 8px; color: var(--muted); font-size: 12px; }}
    .detail-strip span {{ border: 1px solid var(--line); border-radius: 999px; padding: 3px 8px; }}
    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      background: #f3f4f6;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      margin: 0;
    }}
    .kv-grid {{ display: grid; gap: 8px; }}
    .kv {{ display: flex; justify-content: space-between; gap: 12px; border-bottom: 1px solid var(--line); padding-bottom: 8px; }}
    .kv span {{ color: var(--muted); }}
    .detail-list {{ margin: 0; padding-left: 18px; }}
    .detail-list li {{ margin-bottom: 10px; }}
    .detail-list span {{ display: block; color: var(--muted); margin-top: 2px; }}
    .empty {{ color: var(--muted); margin-bottom: 0; }}
    .hidden {{ display: none !important; }}
    .severity-critical .severity-dot {{ background: var(--critical); }}
    .severity-high .severity-dot {{ background: var(--high); }}
    .severity-medium .severity-dot {{ background: var(--medium); }}
    .severity-low .severity-dot {{ background: var(--low); }}
    .severity-none .severity-dot {{ background: var(--none); }}
    .severity-info .severity-dot {{ background: var(--info); }}
    .severity-critical .badge, .severity-critical.nav-item span {{ color: var(--critical); }}
    .severity-high .badge, .severity-high.nav-item span {{ color: var(--high); }}
    .severity-medium .badge, .severity-medium.nav-item span {{ color: var(--medium); }}
    .severity-low .badge, .severity-low.nav-item span {{ color: var(--low); }}
    .severity-none .badge, .severity-none.nav-item span {{ color: var(--none); }}
    .severity-info .badge, .severity-info.nav-item span {{ color: var(--info); }}
    @media (max-width: 840px) {{
      .layout {{ grid-template-columns: 1fr; }}
      aside {{ position: static; max-height: none; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="eyebrow">Skill Lint Report</div>
    <h1>{html_text(report.get("target"), title)}</h1>
    <p>{html.escape(summary)}</p>
  </header>
  <main class="layout">
    <aside>
      <section class="panel filters">
        <div>
          <h2>Search</h2>
          <input id="search" type="search" placeholder="Search findings, files, evidence">
        </div>
        <div>
          <h2>Severity</h2>
          <div class="filter-group">{severity_buttons}</div>
        </div>
        <div>
          <h2>Checks</h2>
          <div class="filter-group">{check_buttons}</div>
        </div>
      </section>
      <section class="panel">
        <h2>Findings</h2>
        <div class="nav-list">{nav_items}</div>
      </section>
    </aside>
    <section>
      <section class="panel">
        <h2>Overview</h2>
        <dl class="overview">{metadata}</dl>
      </section>
      {capabilities}
      <section aria-live="polite" id="result-count" class="panel"></section>
      <section id="findings">{finding_cards}</section>
      {fixes}
      {unresolved}
      {validation}
      {unknowns}
    </section>
  </main>
  <script>
    const state = {{ severity: 'all', check: 'all', query: '' }};
    const cards = Array.from(document.querySelectorAll('.finding-card'));
    const navItems = Array.from(document.querySelectorAll('.nav-item'));
    const count = document.getElementById('result-count');

    function textOf(element) {{
      return element.textContent.toLowerCase();
    }}

    function updatePressed(selector, attr, value) {{
      document.querySelectorAll(selector).forEach((button) => {{
        const active = button.getAttribute(attr) === value;
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', active ? 'true' : 'false');
      }});
    }}

    function applyFilters() {{
      let visible = 0;
      cards.forEach((card, index) => {{
        const matchesSeverity = state.severity === 'all' || card.dataset.severity === state.severity;
        const matchesCheck = state.check === 'all' || card.dataset.check === state.check;
        const matchesQuery = !state.query || textOf(card).includes(state.query);
        const show = matchesSeverity && matchesCheck && matchesQuery;
        card.classList.toggle('hidden', !show);
        if (navItems[index]) navItems[index].classList.toggle('hidden', !show);
        if (show) visible += 1;
      }});
      count.innerHTML = `<strong>${{visible}}</strong> of <strong>${{cards.length}}</strong> findings shown`;
    }}

    document.querySelectorAll('[data-severity-filter]').forEach((button) => {{
      button.addEventListener('click', () => {{
        state.severity = button.dataset.severityFilter;
        updatePressed('[data-severity-filter]', 'data-severity-filter', state.severity);
        applyFilters();
      }});
    }});

    document.querySelectorAll('[data-check-filter]').forEach((button) => {{
      button.addEventListener('click', () => {{
        state.check = button.dataset.checkFilter;
        updatePressed('[data-check-filter]', 'data-check-filter', state.check);
        applyFilters();
      }});
    }});

    document.getElementById('search').addEventListener('input', (event) => {{
      state.query = event.target.value.trim().toLowerCase();
      applyFilters();
    }});

    navItems.forEach((button) => {{
      button.addEventListener('click', () => {{
        const card = document.getElementById(`finding-${{button.dataset.open}}`);
        if (!card) return;
        const detail = card.querySelector('details');
        if (detail) detail.open = true;
        card.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }});
    }});

    applyFilters();
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a skill-lint JSON report as interactive HTML.")
    parser.add_argument("report_json", help="Path to skill-lint report data JSON")
    parser.add_argument("--output", help="HTML output path; defaults to the JSON path with .html suffix")
    args = parser.parse_args()

    report_path = Path(args.report_json).expanduser().resolve()
    if not report_path.exists():
        print(f"Report JSON not found: {report_path}", file=sys.stderr)
        return 2

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"Invalid report JSON: {error}", file=sys.stderr)
        return 2
    if not isinstance(report, dict):
        print("Report JSON must contain an object at the top level.", file=sys.stderr)
        return 2

    output_path = Path(args.output).expanduser().resolve() if args.output else report_path.with_suffix(".html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html(report), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
