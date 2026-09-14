---
name: autonomous-development
description: "Run autonomous repository development through a supervisor and specialized workers: rightsize the task, research, plan, implement in an isolated branch and linked worktree, publish coherent checkpoints, validate, and open a draft pull request. Use when the user hands Codex a feature, bug fix, refactor, or repository change request and wants Codex to carry it through to a PR."
---

# Autonomous Development

## Operating Principle

Use the main thread as the supervisor and delegate all task execution to worker agents. Preserve worktree isolation, an explicit parent, planning before implementation, coherent commits and pushes, and repository checks; require supervisor sign-off on validation before opening a draft PR and completing the task.

## Inputs

Accept a repository change request such as a feature, bug fix, refactor, test addition, docs update, or investigation with implementation. If the request is materially ambiguous, ask the smallest set of blocking questions before touching files.

Infer the target repository from the current working directory; have the first worker verify it during baseline setup. If no git repository is present, stop and report that this workflow requires a git checkout.

## Supervisor And Worker Workflow

1. **Rightsize first.** Before dispatching workers or starting repository work, the supervisor analyzes the request's scope, uncertainty, risk, dependencies, and available context. State which worker types are needed, how many of each, and why. Small tasks may use a subset; larger tasks may need multiple workers of each type. Reassess this allocation when worker findings change the scope.
2. **Keep execution in workers.** The supervisor owns request analysis, resource allocation, assignments, handoffs, user communication, and acceptance decisions. Workers perform all research, repository inspection and setup, planning, edits, checks, Git operations, and PR creation. If subagent tools are unavailable, report that blocker instead of doing the workers' jobs in the main thread.
3. **Route in order:** research → planning → development → validation. Omit research only when sufficient findings are already available; omit planning only when an actionable plan with acceptance criteria is already supplied or accepted. Pass that existing material forward. Every implementation requires a development worker and a separate validation worker. Parallelize independent work within a stage; downstream work starts only after its prerequisite outputs are accepted by the supervisor.
4. **Use fresh sessions.** Spawn a brand-new subagent for every assignment, including each stage, correction, and revalidation. Never resume, repurpose, or give another assignment to an existing subagent. Pass context through explicit handoffs; messages to an active worker may clarify its current assignment.
5. **Make handoffs sufficient.** Give each worker the request, assigned scope and role, repository instructions, control checkout and established worktree/branch, relevant predecessor findings or accepted plan, acceptance criteria, and required output. Have workers return findings or changes, evidence, blockers, and next-stage inputs. When several workers contribute, reconcile their outputs before accepting the stage. Follow the shared worktree contract's single-writer rule, including commands that generate files.

| Worker type | Responsibility and handoff |
| --- | --- |
| Research agent | Investigate the problem and relevant code, tests, constraints, and dependencies. Return evidence, affected touch points, and unresolved questions for planning. |
| Planning agent | Turn the request and research into the implementation plan below. Define ordered steps, ownership where work is split, and acceptance criteria for development and validation. |
| Development agent | Execute the accepted plan, make scoped changes, run development checks, and commit and push coherent checkpoints. Return the implemented steps, deviations, changed files, commit IDs, and validation evidence. Also handle assigned integration or PR finalization work. |
| Validation agent | Independently inspect and test the development result against the accepted plan and original request. Report each criterion as met, unmet, or blocked, with evidence and actionable findings. Do not make implementation fixes. |

The first selected worker performs baseline setup before its stage-specific work; all later workers receive the resulting worktree, branch, parent ref, and start SHA.

## Baseline

Assigned worker:

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

Other agents may be working on the same code in different worktrees. Worktree isolation does not prevent overlapping changes or integration conflicts. The supervisor coordinates ownership and handoffs; assigned workers perform repository comparisons and integration changes.

- Before editing, use available agent coordination channels to identify active work that overlaps the task. Share the intended scope, branch, and affected files or interfaces; agree on ownership, dependencies, and landing order where work overlaps.
- Keep affected agents informed when scope, shared interfaces, or dependencies change. Preserve their work, and resolve conflicting approaches together rather than overwriting changes or silently duplicating implementation. If coordination is unavailable, report the unresolved overlap and continue independent work.
- Before the final validation and PR, fetch the latest parent and check relevant companion branches or PRs. Incorporate required landed changes into the task branch without rewriting published checkpoints, resolve conflicts while preserving both tasks' intended behavior, and rerun affected checks. Document companion PRs, dependencies, and the agreed landing order in the PR and handoff; report any unresolved integration blocker. Coordination does not authorize merging PRs or modifying another agent's branch or worktree.

## Plan

Before implementation, the planning worker returns a concise plan for the supervisor to review and present in the conversation. When this stage is omitted, review and present the existing plan instead. If the change is large enough to warrant a plan file, keep that file out of the commit and PR. Include:

- the requested outcome in concrete terms,
- relevant files, modules, APIs, commands, or workflows discovered from the repo,
- assumptions and any accepted clarifications,
- ordered implementation steps,
- validation criteria that define done behavior, and the evidence required before opening the PR: test commands, manual checks, screenshots, or logs,
- risks, migrations, compatibility concerns, or rollout notes when relevant.

If the plan reveals a material gap, the supervisor obtains the needed clarification before accepting it. Dispatch development only after the supervisor accepts the plan.

## Implementation

Assigned development worker:

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

A fresh validation worker reviews the diff and independently runs the repo's relevant checks against the completed implementation before opening the PR. Prefer discovered project commands over generic guesses:

- type checks,
- lint or formatting checks,
- unit tests,
- integration or end-to-end tests,
- build commands,
- targeted manual verification for UI or behavior that automated tests do not cover.

Return a validation report identifying the validated commit, coverage of each accepted plan step and acceptance criterion, commands and outcomes, and any missing or incorrect behavior. If a check cannot be run because of missing credentials, services, packages, time, or environment constraints, record the exact command, failure, and residual risk for the PR.

The supervisor reviews the report against the request and accepted plan. If validation finds an implementation issue or an unmet plan requirement, spawn a **brand-new development agent** with the plan, findings, and current worktree/commit to fix it. Never send fixes back to an earlier development session. After its changes are committed and pushed, spawn a **brand-new validation agent** to check the correction and affected behavior. Repeat until the evidence supports acceptance, or report a concrete blocker with the work left reviewable. Route material plan gaps through a fresh planning agent before further development.

The supervisor explicitly records validation sign-off only when the evidence supports fulfillment of the request and accepted plan. Document any accepted validation limitations; do not treat an unmet requirement as complete. Changes after sign-off invalidate it and require fresh validation and supervisor sign-off before finalization.

Development workers review `git status --short` and the relevant diff before each commit, then the staged diff after staging. Validation workers run the complete relevant validation suite before PR finalization.

## Finalize And Open PR

After validation sign-off, assign a fresh development worker to finalize the branch and PR:

1. Confirm task changes are committed and the branch still matches the signed-off commit. If final changes are needed, return through development, fresh validation, and supervisor sign-off before opening the PR. Stage only files that belong to the task and follow the checkpoint rules.
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

The supervisor finishes only after reviewing the finalization worker's handoff, confirming that the PR contains the signed-off commit, and reporting the branch, linked worktree path, pushed commits, PR URL, validation performed, supervisor sign-off, and any skipped checks or unresolved risks. Leave the linked worktree in place for review or follow-up unless the user explicitly asks to remove it. If pushing or opening a PR is blocked, keep the branch and commits reviewable and report the exact blocker.
