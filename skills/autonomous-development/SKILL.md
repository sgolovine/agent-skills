---
name: autonomous-development
description: "Run an end-to-end autonomous feature development workflow in a code repository: establish a clean git baseline from the correct base branch, create a plan with validation criteria, implement the plan, test the code, commit the work, push a branch, and open a draft pull request. Use when the user hands Codex a feature, bug fix, refactor, or repository change request and wants Codex to carry it through to a PR."
---

# Autonomous Development

## Operating Principle

Move like a careful project maintainer: preserve unrelated work, make the intended base explicit, plan before editing, verify with the repo's own checks, and open a draft PR only when the implementation and evidence are coherent.

## Inputs

Accept a repository change request such as a feature, bug fix, refactor, test addition, docs update, or investigation with implementation. If the request is materially ambiguous, ask the smallest set of blocking questions before touching files.

Infer the target repository from the current working directory. If no git repository is present, stop and report that this workflow requires a git checkout.

## Baseline

1. Inspect repository state before changing anything:
   - `git status --short --branch`
   - `git remote -v`
   - `git branch --show-current`
   - `git rev-parse --show-toplevel`
2. Identify the base branch:
   - Use the branch named by the user when provided.
   - Otherwise use the remote default branch from `origin/HEAD`.
   - If that is unavailable, choose the existing `main` or `master` branch only when unambiguous; otherwise ask.
3. Preserve unrelated local work:
   - If the working tree has uncommitted changes before starting, inspect enough to decide whether they are relevant.
   - Do not overwrite, revert, stash, or commit pre-existing user changes without explicit intent.
   - If unrelated changes would block baseline setup, create a separate worktree or ask for direction.
4. Update the base branch:
   - Fetch remotes with pruning.
   - Switch to the base branch or create a worktree from it if needed to protect local state.
   - Fast-forward the base branch from its upstream. If fast-forward is impossible, stop and report the branch divergence.
5. Create a task branch from the updated base branch. Use `codex/<short-kebab-summary>` unless the user requests another name. Avoid reusing an existing branch unless it is clearly the active task branch.

## Plan

Before editing, create a concise implementation plan in the conversation or a project-local plan file when the change is large. Include:

- the requested outcome in concrete terms,
- relevant files, modules, APIs, commands, or workflows discovered from the repo,
- assumptions and any accepted clarifications,
- ordered implementation steps,
- validation criteria that define done behavior,
- test commands, manual checks, screenshots, logs, or review evidence required before opening the PR,
- risks, migrations, compatibility concerns, or rollout notes when relevant.

If the plan reveals a material gap, ask before implementation. Otherwise proceed.

## Implementation

1. Read the existing code and tests around the planned touch points before editing.
2. Follow repository patterns for architecture, naming, style, dependencies, tests, and error handling.
3. Keep changes scoped to the request. Do not perform opportunistic refactors, formatting sweeps, dependency upgrades, or unrelated cleanup.
4. Update or add tests near the changed behavior. When tests are not practical, explain why and use the strongest available validation.
5. Update documentation, examples, migrations, or configuration only when required by the changed behavior.
6. Review the diff while working to catch accidental edits, generated noise, secret material, or unrelated changes.

## Validation

Run the repo's relevant checks before opening the PR. Prefer discovered project commands over generic guesses:

- type checks,
- lint or formatting checks,
- unit tests,
- integration or end-to-end tests,
- build commands,
- targeted manual verification for UI or behavior that automated tests do not cover.

If a check fails, fix the cause and rerun the relevant check. If a check cannot be run because of missing credentials, services, packages, time, or environment constraints, record the exact command, failure, and residual risk in the PR.

Before committing, inspect:

- `git status --short`
- `git diff`
- `git diff --stat`
- staged diff after staging

## Commit And PR

1. Stage only files that belong to the task.
2. Commit the implementation with a focused message that follows the repository's convention. If no convention is discoverable, use Conventional Commits.
3. Push the task branch to the remote.
4. Open a draft pull request by default. Use a ready-for-review PR only when the user explicitly requests it.
5. Set the PR base to the baseline branch established earlier.
6. Write the PR body with:
   - summary of the user-facing or developer-facing change,
   - implementation notes that matter for review,
   - validation commands and outcomes,
   - known gaps, skipped checks, or follow-up work,
   - screenshots or artifact links when UI or visual behavior changed.

Do not merge the PR, mark it ready, request reviewers, or modify remote repository settings unless the user explicitly asks.

## Completion Criteria

Finish only after reporting the branch, PR URL, validation performed, and any skipped checks or unresolved risks. If opening a PR is blocked, still leave the branch and commits in a reviewable state and report the exact blocker.
