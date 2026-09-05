---
name: autonomous-development
description: "Run an end-to-end autonomous feature development workflow in a code repository: create an isolated task branch and linked worktree from the correct base, plan and implement the change, commit and push coherent checkpoints throughout development, validate the result, and open a draft pull request. Use when the user hands Codex a feature, bug fix, refactor, or repository change request and wants Codex to carry it through to a PR."
---

# Autonomous Development

## Operating Principle

Move like a careful project maintainer: isolate every task in a new branch and linked worktree, preserve unrelated work, make the intended parent explicit, plan before editing, checkpoint coherent progress with conventional commits and pushes, verify with the repo's own checks, and open a draft PR only when the implementation and evidence are coherent.

## Inputs

Accept a repository change request such as a feature, bug fix, refactor, test addition, docs update, or investigation with implementation. If the request is materially ambiguous, ask the smallest set of blocking questions before touching files.

Infer the target repository from the current working directory. If no git repository is present, stop and report that this workflow requires a git checkout.

## Baseline

1. Inspect repository state before changing anything: `git status --short --branch`, `git remote -v`, and `git worktree list`.
2. Identify a parent branch from `main`, `master`, or `develop`:
   - If the user names the parent, require it to be one of those three and to exist; otherwise stop and ask for a supported parent.
   - When the user does not name the parent, use the remote default branch when it is one of those three; resolve an unset `origin/HEAD` with `git remote show origin`.
   - If the remote default is unavailable or has another name, use an existing branch in this order: `main`, `master`, then `develop`.
   - If none exists, stop and ask which supported parent branch to create or use. Do not base autonomous development on any other branch.
3. Preserve unrelated local work. Do not overwrite, revert, stash, or commit pre-existing user changes. A dirty original checkout does not need to be cleaned.
4. Fetch remotes with pruning. Choose `origin/<parent>` as the start point when available; otherwise use the local parent and note that push and PR steps may be blocked.
5. Read [the shared linked worktree contract](../../references/worktrees.md), then apply it before planning or editing, even when the original checkout is clean. Use:
   - the original checkout as the control checkout,
   - the selected parent ref as the start point,
   - `codex/<short-kebab-summary>` as the unique local branch unless the user requests another name,
   - a unique sibling path such as `../<repo>-worktrees/<short-kebab-summary>`.
6. Never develop directly on `main`, `master`, or `develop`. Perform all remaining repository work from the linked worktree and leave it in place for review or follow-up unless the user explicitly requests cleanup.

## Coordinate With Other Agents

Other agents may be working on the same code in different worktrees. Worktree isolation does not prevent overlapping changes or integration conflicts. Coordinate with those agents so everyone's work can land successfully.

- Before editing, use available agent coordination channels to identify active work that overlaps the task. Share the intended scope, branch, and affected files or interfaces; agree on ownership, dependencies, and landing order where work overlaps.
- Keep affected agents informed when scope, shared interfaces, or dependencies change. Preserve their work, and resolve conflicting approaches together rather than overwriting changes or silently duplicating implementation. If coordination is unavailable, report the unresolved overlap and continue independent work.
- Before the final validation and PR, fetch the latest parent and check relevant companion branches or PRs. Incorporate required landed changes into the task branch without rewriting published checkpoints, resolve conflicts while preserving both tasks' intended behavior, and rerun affected checks. Document companion PRs, dependencies, and the agreed landing order in the PR and handoff; report any unresolved integration blocker. Coordination does not authorize merging PRs or modifying another agent's branch or worktree.

## Plan

Before editing, create a concise implementation plan in the conversation. If the change is large enough to warrant a plan file, keep that file out of the commit and PR. Include:

- the requested outcome in concrete terms,
- relevant files, modules, APIs, commands, or workflows discovered from the repo,
- assumptions and any accepted clarifications,
- ordered implementation steps,
- validation criteria that define done behavior, and the evidence required before opening the PR: test commands, manual checks, screenshots, or logs,
- risks, migrations, compatibility concerns, or rollout notes when relevant.

If the plan reveals a material gap, ask before implementation. Otherwise proceed.

## Implementation

1. Read the existing code and tests around the planned touch points before editing.
2. Follow repository patterns for architecture, naming, style, dependencies, tests, and error handling.
3. Keep changes scoped to the request. Do not perform opportunistic refactors, formatting sweeps, dependency upgrades, or unrelated cleanup.
4. Update or add tests near the changed behavior. When tests are not practical, explain why and use the strongest available validation.
5. Update documentation, examples, migrations, or configuration only when required by the changed behavior.
6. Review the diff while working to catch accidental edits, generated noise, secret material, or unrelated changes.
7. Create and publish checkpoints throughout development:
   - Commit after each coherent milestone, such as a schema or API change, the core implementation, tests, or documentation. For a small atomic task, one implementation commit is sufficient.
   - Before each checkpoint, run the fastest relevant targeted check and inspect the staged diff. Keep each commit focused and leave the branch in a usable state when practical.
   - Follow the repository's documented or recent commit convention. If none is clear, use Conventional Commits 1.0.0 (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, and similar).
   - Push immediately after the first commit with `git push -u origin <branch>`, then push again after every later commit. Do not wait until the end of a multi-milestone task to publish all progress.
   - Do not use meaningless checkpoint messages such as `WIP`, and do not amend, squash, rebase, or force-push already published checkpoints unless the user explicitly asks.

## Validation

Run the repo's relevant checks before opening the PR. Prefer discovered project commands over generic guesses:

- type checks,
- lint or formatting checks,
- unit tests,
- integration or end-to-end tests,
- build commands,
- targeted manual verification for UI or behavior that automated tests do not cover.

If a check fails, fix the cause and rerun the relevant check. If a check cannot be run because of missing credentials, services, packages, time, or environment constraints, record the exact command, failure, and residual risk in the PR.

Before each commit, review `git status --short` and the relevant diff, then the staged diff after staging. Run the complete relevant validation suite before the final push and PR.

## Finalize And Open PR

1. Stage only files that belong to the task. If validation or review produced final changes, commit them with the same checkpoint rules; do not leave task changes uncommitted.
2. Confirm every commit has been pushed and the local task branch is synchronized with its upstream.
3. Open a draft pull request by default with `gh pr create --draft --base <parent>`, where `<parent>` is the parent branch established earlier. Use a ready-for-review PR only when the user explicitly requests it. If `gh` is unavailable or unauthenticated, leave the branch pushed and report the compare URL as the blocker instead of retrying other tooling.
4. Write the PR body with:
   - summary of the user-facing or developer-facing change,
   - implementation notes that matter for review,
   - validation commands and outcomes,
   - known gaps, skipped checks, or follow-up work,
   - screenshots or artifact links when UI or visual behavior changed.

Do not merge the PR, mark it ready, request reviewers, or modify remote repository settings unless the user explicitly asks.

## Completion Criteria

Finish only after reporting the branch, linked worktree path, pushed commits, PR URL, validation performed, and any skipped checks or unresolved risks. Leave the linked worktree in place for review or follow-up unless the user explicitly asks to remove it. If pushing or opening a PR is blocked, keep the branch and commits reviewable and report the exact blocker.
