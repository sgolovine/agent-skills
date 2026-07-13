# Research and Report Contract

## Version Resolution

For each `actions/<repository>`:

1. Open the repository README and releases page.
2. Identify the newest non-draft, non-prerelease release and the major tag recommended by current usage examples.
3. Corroborate that moving major in the repository's tags or release history. Prefer the newest stable major that the repository documents for general use; ignore preview, beta, release-candidate, experimental, and branch-only versions.
4. If the README and releases disagree, inspect the release date, tags, changelog, upgrade documentation, and repository status. Record the conflict and leave the reference unchanged unless official evidence resolves it.
5. Use the first path segment after `actions/` as the repository. For example, both `actions/cache@v3` and `actions/cache/restore@v3` resolve through `https://github.com/actions/cache`; retain `/restore` when editing.

The target ref is always the stable moving major tag `vN`, not a full semantic version or commit SHA. Never derive the target solely from the numerically largest tag: repositories can contain unsupported experiments or prereleases.

## Research Ledger

Record these fields once per repository:

- repository URL;
- current ref or refs and, when known, their corresponding releases;
- target stable major and supporting README, release, and tag or upgrade-guide URLs;
- release date or evidence-access date;
- majors crossed;
- documented breaking changes and migration requirements;
- consumer-specific risk based on the workflow's inputs, permissions, runner, and surrounding steps;
- confidence and unresolved conflicts.

Use direct official GitHub repository pages as sources. Clearly label reasoned consumer-specific conclusions as inferences rather than documented facts.

## Breaking-Risk Review

For each actual major upgrade, check all crossed-major release notes and relevant migration guidance. Look specifically for:

- minimum runner versions and bundled Node runtime changes;
- removed, renamed, or behavior-changing inputs and outputs;
- cache key, archive, authentication, token, checkout, and persistence changes;
- permission or security-default changes;
- platform, architecture, package-manager, or language-version support changes;
- deprecated scenarios and required companion-step changes.

Classify each occurrence as:

- `No major change`: already on the target major or only normalized within that major;
- `Review advised`: a major changed but no workflow-specific incompatibility was identified;
- `Potential break`: official guidance conflicts with the workflow's observed configuration;
- `Unknown`: source or current-version evidence is incomplete.

Do not silently implement migration changes outside the requested version update. Put recommended follow-up work in the report.

## HTML Report Content

Use `$html-report-builder` components and inline all CSS so the report is portable. Prefer `report-cover`, `metric-summary`, `insight-callout`, `data-table`, section headers, and appendix notes. The report must include:

1. Title, target project, generation date, workflow glob scope, and a concise overall outcome.
2. Metrics for workflow files scanned, occurrences found, unique repositories, changed occurrences, already-current occurrences, and manual-review items.
3. An occurrence table with workflow path and line, action, previous ref, target ref, status, and risk classification.
4. A breaking-change section organized by repository and crossed major, with documented changes, workflow-specific implications, recommended follow-up, and direct source links.
5. An evidence section showing how each target major was selected from the README, releases, and corroborating repository material.
6. A manual-review section for unparsed refs, unavailable repositories, conflicting version evidence, and unknown starting SHAs or branches.
7. Methodology and limitations, including that mutable major tags were intentionally requested and that the review does not execute workflows.

Render paths and action strings as escaped text. Use meaningful link labels, semantic table headers, visible text status labels, responsive table overflow, print styles, and no remote JavaScript. If nothing changed, state why rather than leaving sections blank.
