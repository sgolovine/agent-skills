---
name: update-github-actions
description: Update official `actions/*` references in top-level GitHub Actions workflow YAML files to each action's latest stable major version and generate a self-contained HTML change and breaking-risk report. Use when Codex is asked to audit, upgrade, modernize, or refresh GitHub-authored action versions in `.github/workflows/*.yml` or `.github/workflows/*.yaml`.
---

# Update GitHub Actions

## Operating Principle

Research each official action before changing it, limit edits to version references, and leave an evidence-backed report that makes upgrade risk visible.

## Workflow

1. Resolve the target project root from the user's request, defaulting to the current working directory. Resolve the directory containing this `SKILL.md` as `<skill-dir>`.
2. Read [references/research-and-report.md](references/research-and-report.md). Its version-resolution and report contracts are required.
3. Inventory workflow references by running:

   ```bash
   python3 <skill-dir>/scripts/scan_actions.py --root <project-root> --pretty
   ```

   Scan only `.github/workflows/*.yml` and `.github/workflows/*.yaml`. Treat every parsed `actions/<repository>[/<subpath>]@<ref>` occurrence as in scope. Group research by `actions/<repository>` while retaining every file, line, and optional subpath occurrence. Keep unparsed official-action lines in the manual-review list.
4. Research every unique repository at `https://github.com/actions/<repository>` using current web sources. Inspect its README, releases, and relevant tags, changelog, upgrade guidance, action metadata, or documentation. Determine the latest stable major according to the reference contract; do not rely on memory or search-result snippets.
5. Before editing, inspect the release and migration material for every crossed major. Record documented breaking changes, runner/runtime requirements, changed inputs or outputs, defaults, behavior, permissions, and deprecations. If the current ref is a SHA or branch, identify its associated release or major when reliable; otherwise mark the starting version as unknown.
6. Update every resolvable occurrence to `@vN`, where `N` is the latest stable major. Replace exact tags, branches, and full SHAs as well as older major tags. Preserve the action name, optional subpath, YAML quoting, indentation, and unrelated comments. Update or remove an inline comment only when it would otherwise claim a stale version. Do not alter non-`actions/*` dependencies or make consumer migration changes beyond the version token.
7. Leave an occurrence unchanged and mark it `Needs review` when the repository is unavailable, the stable major cannot be established from official evidence, or the reference cannot be safely parsed. Continue with all other actions.
8. Re-run the scanner and confirm that every resolvable occurrence uses its researched target major. Review the workflow diff for scope, and run `git diff --check` when the project is a Git worktree.
9. Invoke `$html-report-builder` to create a standalone report at `<project-root>/github-actions-update-report.html`. Follow its component-directory and render-and-verify workflow, and use the content contract in the reference file. Generate the report even when there are no workflows, no matching actions, no changes, or unresolved actions.

## Completion

Report the number of workflow files scanned, action occurrences found, references changed, already-current references, and manual-review items. Link the HTML report and identify any workflow files changed. Do not describe an upgrade as safe when evidence is incomplete.
