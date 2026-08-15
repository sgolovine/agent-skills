# HTML Report Format

Create a fresh single HTML file in the operating-system temp directory. Tailwind and Mermaid may load from CDNs; keep all report content and custom presentation in the file.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Architecture review — {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Composition

Start with repository name, date, and a compact legend: solid box is a module, dashed line is a seam, red arrow is leakage, and a thick dark box is a deep module. Skip introductory prose.

Render each candidate as an `<article>` containing:

- a short deepening title;
- strength badge (`Strong` emerald, `Worth exploring` amber, `Speculative` slate);
- dependency category badge;
- monospaced file list;
- side-by-side before and after diagrams;
- one-sentence problem and solution;
- short wins phrased as locality, leverage, interface, and test-surface gains;
- an amber ADR-conflict callout when applicable.

End with one larger top-recommendation card containing the candidate name, one-sentence rationale, and an anchor link to its card.

## Diagram selection

Let diagrams carry the explanation. Keep them about 320 pixels high and vary the visual form by candidate:

- Use Mermaid flowcharts or sequence diagrams for dependencies, call graphs, and round trips.
- Use positioned HTML boxes with inline SVG arrows when Mermaid layout obscures seam or module depth.
- Use stacked horizontal bands to show many shallow pass-through modules collapsing into one deep module.
- Use paired interface and implementation rectangles to show shallow versus deep proportions.
- Use a faded internal call tree inside one thick module to show call-graph collapse.

Use generous whitespace, restrained slate/stone colors, one accent, red only for leakage, and amber for warnings. Prefer an editorial schematic over a dashboard. Keep prose sparse; redraw a diagram that needs a paragraph of explanation.

Use the exact architecture nouns: module, interface, implementation, depth, deep, shallow, seam, adapter, leverage, locality. Do not substitute component, service, API, signature, boundary, layer, or wrapper when one of those architecture terms is intended.

Good phrasing includes:

- “Order intake module is shallow — interface nearly matches the implementation.”
- “Pricing leaks across the seam.”
- “Deepen: one interface, one place to test.”
- “Two adapters justify the seam: HTTP in production, in-memory in tests.”
