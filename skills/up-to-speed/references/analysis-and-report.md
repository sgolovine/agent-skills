# Analysis and Report Contract

## Audience and Evidence

Write for a senior full-stack TypeScript developer who is new to this repository. Explain unfamiliar language or ecosystem conventions by mapping them to useful architectural concepts, but do not teach common engineering fundamentals.

Use repository evidence in this order: executable source and configuration, manifests and lockfiles, tests, CI configuration, then prose documentation. Attach concrete paths to important claims. Record contradictions, missing configuration, and uncertain behavior instead of smoothing them over. Do not claim that a command passes or a workflow succeeds unless it was actually observed.

## Coverage

Inspect the sources relevant to the repository rather than applying a fixed ecosystem checklist:

- Root identity: primary documentation, license, manifests, lockfiles, language and runtime pins, environment examples, containers, infrastructure, generated-code declarations, and ownership metadata.
- Structure and runtime: entrypoints, routing or transport boundaries, domain modules, persistence, external integrations, shared code, configuration loading, deployment units, and data or request flow.
- Packages: workspace declarations and build graphs first, then package manifests and deployable units outside the workspace graph. Deduplicate nested manifests that do not define an independent package.
- Tooling: package and task runners, compiler or transpiler, bundler, local development, linting, formatting, type checking, code generation, migrations, logging, observability, and debugging.
- Testing: test runners, assertion and mocking tools, browser or integration harnesses, commands, configs, test locations and naming, fixtures, coverage, and CI integration.
- AI: all scoped `AGENTS.md` and `CLAUDE.md` files, plus repository-local skills, prompts, commands, rules, hooks, and agent or MCP configuration. Summarize scope and behavior-changing rules; do not reproduce them wholesale.
- Automation: GitHub Actions, GitLab CI, CircleCI, Jenkins, Buildkite, Azure Pipelines, Bitbucket Pipelines, Travis, Drone, release automation, deployment definitions, pre-commit hooks, and other detected equivalents.

For a monorepo, account for every discovered package. Each package must appear in the package inventory and in every applicable libraries, tooling, and testing section. Mark shared or inherited configuration explicitly instead of repeating it, and mark missing package-specific coverage as absent rather than silently omitting the package.

## HTML Report Content

Create `<repo-root>/__up_to_speed__/report.html` with the compact grayscale printed-form system from `$html-report-builder`. Use one `h1`, the exact `h2` headings below, and the smallest useful visual forms. A curated structure tree and compact comparison tables are preferable to decorative charts.

Keep the first viewport useful: report title, repository name and root, generation date, analyzed revision or branch when available, package count, dominant runtime or language, and three to five high-value takeaways.

### Summary

Give a brief architectural briefing and a short productivity-oriented orientation: what kind of system this is, its major boundaries, and where a developer is likely to make their first changes. Do not repeat the later inventories.

### Intent

Explain the product or operational purpose, primary users or consumers, main inputs and outputs, and core runtime flow based on findings. Separate documented intent from implementation-derived inference.

### Project Structure

Include:

- a curated tree showing entrypoints, important source roots, configuration, tests, automation, and generated or infrastructure boundaries;
- the organization and dependency direction between major modules or deployable units;
- key configuration-loading and execution paths;
- for monorepos, a complete package matrix with path, role, runtime, entrypoint, internal dependencies, and build or deploy unit, followed by concise package profiles where the matrix cannot capture important differences.

Do not reproduce an exhaustive directory listing.

### Key Libraries

List only libraries that define architecture or materially shape implementation: application frameworks, transport, UI or state, persistence, authentication, validation, serialization, queues, external service clients, and observability. Include locally declared versions when useful, which packages use them, why they matter here, and evidence paths. Avoid dependency dumps.

### Devtooling Stack

Summarize the package manager, runtime and version management, build graph, compiler or transpiler, bundler, local development workflow, linting, formatting, type checking, generation, migrations, logging or observability, containers, and debugging. Include exact configured commands and config locations, grouped by root versus package scope. Highlight non-obvious ordering or prerequisites without inventing a setup tutorial.

### Testing Stack

Identify frameworks and supporting libraries, test layers, exact commands, config locations, test locations and naming conventions, fixtures, coverage, and CI enforcement. Show package-level differences and call out notable gaps such as packages with no discovered tests or commands.

### AI

Summarize applicable repository AI instructions, their scopes and precedence, repository-local skills or commands, and behavior-changing rules that affect future work. Include paths. State clearly when no repository-local AI guidance was found.

### CI and Actions

List each detected automation system and configuration path. Summarize triggers, jobs or stages, matrices, caching, artifacts, quality gates, security checks, release or deployment flows, and local command equivalents. Distinguish configured behavior from run status and state clearly when no CI configuration was found.

## Closing Evidence

End with compact methodology and limitations notes: ignored generated or vendored areas, inaccessible or ambiguous files, inferred claims, and whether commands or workflows were inspected only or executed. Escape all source-derived content, keep exact data in semantic tables, provide visible text labels for status, and use no remote JavaScript.
