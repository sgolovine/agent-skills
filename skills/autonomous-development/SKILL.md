---
name: autonomous-development
description: "Carry a repository change request to a draft pull request: score the task, then research, plan, implement in an isolated branch and linked worktree, publish coherent checkpoints, validate, and open the PR. Delegates stages to fresh subagents when the score warrants it, or runs every stage in one thread when the task is small, the user asks, or subagents are unavailable. Use when the user hands Codex a feature, bug fix, refactor, or repository change request and wants it carried through to a PR."
---

# Autonomous Development

## Operating Principle

The main thread is the supervisor. It sets up the baseline, accepts each stage, signs off validation, and owns every operation against the git provider: PR creation, PR body edits, and screenshot upload. Workers do stage work in the shared linked worktree and publish commits with `git push`. When a role is not staffed, its work moves to another role; it is never dropped.

## Inputs

Accept a repository change request such as a feature, bug fix, refactor, test addition, docs update, or investigation with implementation. If the request is materially ambiguous, ask the smallest set of blocking questions before touching files.

The user does not approve the plan unless they asked to review plans at the outset. In that case, present the plan and wait for approval before development.

## Score And Staff The Task

Before any repository work, score the request from 1 to 10 by scope, uncertainty, risk, and dependencies. State the score, a one-line rationale, the tier, and the agents you will spawn. Rescore when findings change the scope; the new tier applies to stages not yet started.

| Tier | Score | Fits | Research and plan | Development | Validation and screenshots |
| --- | --- | --- | --- | --- | --- |
| Solo | 1–2 | One small, well-understood change | supervisor | supervisor | supervisor |
| Delegated | 3 | Small change that benefits from a clean context | planning worker | development worker | development worker |
| Validated | 4–5 | Bounded change with moderate uncertainty or coordination | planning worker | development worker | validation worker |
| Researched | 6–10 | Broad, uncertain, or high-risk change | research worker, then planning worker | development worker | validation worker |

- Skip the planning worker when the user supplies an actionable plan with acceptance criteria; the supervisor still reviews it. Skip the research worker when the findings are already available.
- Add other workers only for a stated task-specific need or a user request.
- Use [single-agent mode](#single-agent-mode) for the Solo tier, when the user asks for one agent, or when subagent tools are unavailable. Then the supervisor fills every role at any score.

### Delegation

For the Delegated, Validated, and Researched tiers:

- Spawn a brand-new subagent for every assignment, correction, and revalidation. Never reuse or resume an earlier worker.
- A worker returns once. A planning worker returns the plan and stops; a fresh development worker implements the plan after the supervisor accepts it.
- Brief each worker with the request, its role and scope, repository instructions, the control checkout, worktree path, branch, remote, parent ref, start SHA, the accepted outputs of earlier stages, acceptance criteria, and the required output.
- Require each worker to return its findings or changes, evidence, commit IDs, blockers, and inputs for the next stage. Reconcile the outputs of parallel workers before accepting a stage.
- Workers never use `gh` or the provider's web UI.
- Follow the worktree contract's single-writer rule. Run workers in parallel only when at most one of them writes to the worktree, including caches and generated files.

### Single-Agent Mode

The supervisor performs every stage in its own thread. No one else checks the work, so:

- Record the plan in the conversation before the first edit.
- After the last implementation commit, validate in a separate pass. Re-read the request and the plan, review the full diff from the start SHA as a reviewer would, and run the complete relevant check suite, not only targeted checks.
- Fix issues in the same thread, commit, push, and rerun the affected checks. The correction cap below still applies.
- State in the PR body and the final report that the run used single-agent mode, and why.

## Baseline

The supervisor runs the baseline at every tier.

1. Confirm a git checkout with `git rev-parse --show-toplevel`. If there is none, stop and report that this workflow requires one. Inspect `git status --short --branch`, `git remote -v`, and `git worktree list`. Do not overwrite, revert, stash, or commit pre-existing work.
2. Resolve the remote: the one the user names, else the remote of the current branch's upstream, else `origin`, else the only remote. Run `git fetch --prune <remote>`.
3. Resolve the parent branch with git:
   - If the user names a parent, verify that it exists on the remote or locally.
   - Otherwise use the remote's default branch: `git symbolic-ref --short refs/remotes/<remote>/HEAD`, or `git ls-remote --symref <remote> HEAD` when the local ref is unset.
   - If neither gives an answer, stop and ask. Never use the current feature branch as the parent by assumption.
4. Use `<remote>/<parent>` as the start point when it exists. Otherwise use the local parent and note that push and PR steps may be blocked.
5. Apply [the shared linked worktree contract](shared/worktrees.md) with the original checkout as the control checkout, the start point above, a unique branch `<harness>/<short-kebab-summary>` unless the user names one, and a unique path such as `../<repo>-worktrees/<short-kebab-summary>`. Never develop on the parent branch. Do all later repository work in the worktree.
6. Check publication early with `gh auth status` and `gh repo view`. A publication blocker does not stop local work.

## Coordinate With Other Agents

Follow [the shared coordination reference](shared/coordinate.md). The supervisor owns coordination with other agents; workers report overlaps they find. Coordination never authorizes merging PRs or changing another agent's branch or worktree.

Before final validation, fetch the parent again. Merge required landed changes into the task branch without rewriting published commits, then rerun the affected checks. Record companion PRs, dependencies, and the agreed landing order for the PR body.

## Plan

The plan owner presents a concise plan in the conversation:

- the requested outcome, explicit requirements, and assumptions,
- the files, modules, APIs, and commands discovered in the repository,
- ordered implementation steps, with an owner for each part when work is split,
- acceptance criteria and the evidence that proves each one: commands, manual checks, or logs,
- screenshot scenarios per §1 of [the shared screenshots reference](shared/screenshots.md), or the one-line reason none apply,
- risks, migrations, or compatibility notes when relevant.

Keep plan files out of commits. The supervisor reviews the plan against the request, closes material gaps, and accepts it. Ask the user only about blocking ambiguity.

## Implement

The development role:

1. Before the first edit, runs the plan's checks at the start SHA and records failures that already exist.
2. Reads the code and tests around each touch point, follows repository patterns, and keeps changes in scope: no opportunistic refactors, formatting sweeps, or dependency upgrades.
3. Adds or updates tests near the changed behavior, or explains why tests are not practical. Updates docs, migrations, or configuration only when the behavior requires it.
4. Commits and pushes as it works:
   - Commit each coherent milestone before starting the next, such as an API change, the core change, tests, or docs. Use one commit only for a trivially small change, such as a typo fix. Do not make empty or artificial commits.
   - Before each commit, run the fastest relevant check, stage task files explicitly, and inspect the staged diff for unrelated edits, generated noise, and secrets.
   - Write messages per [the shared commit reference](shared/commits.md).
   - Push after the first commit with `git push -u <remote> <branch>` and after every later commit.
   - Never amend, squash, rebase, or force-push published commits unless the user asks.
5. Returns the steps done, deviations from the plan, changed files, commit IDs, and check results.

## Validate

The validation owner reviews the full diff from the start SHA against the accepted plan and the original request. It runs the relevant checks from repository docs and CI: type checks, lint, tests, builds, and manual checks for behavior that automated tests do not cover. A validation worker does not fix anything.

The validation report names the validated commit and gives, for each acceptance criterion, met, unmet, or blocked with evidence. It lists each command and outcome, separates regressions from the baseline failures, and gives the exact command, failure, and residual risk for each check that could not run.

The supervisor reviews the report against the request and plan:

- For an implementation issue, spawn a fresh development worker with the plan, the findings, the worktree, and the current commit. After it pushes, revalidate per the tier: a fresh validation worker at Validated and Researched, or the correction worker's own evidence at Delegated. Resolve a material plan gap with a fresh planning assignment before more development.
- Stop after three correction rounds. Open the draft PR with the unmet criteria under `## Known gaps`, report the blocker, and do not claim completion.
- Record sign-off explicitly only when the evidence shows that the request and plan are fulfilled. Any later commit invalidates the sign-off and needs fresh validation.

## Screenshots

The screenshot owner from the tier table follows §1–§3 of [the shared screenshots reference](shared/screenshots.md), including its skip rule for internal changes with no visible output. Screenshots supplement checks; they never replace them. The owner returns the images, their scenarios, and the commit they show. A capture blocker goes to the supervisor; it does not block validation.

## Open The PR

The supervisor:

1. Confirms that the worktree is clean, every commit is pushed, and the remote head is the signed-off commit.
2. Reuses an open PR for the branch (`gh pr list --head <branch>`). Otherwise runs `gh pr create --draft --base <parent> --head <branch>`, prefixing the head with `<fork-owner>:` when the remote is a fork. Opens a ready PR only when the user asks. If `gh` is unavailable or unauthenticated, reports the compare URL as the blocker.
3. Writes the title and body per [the shared PR writing reference](shared/pr-writing.md). Includes companion PRs, baseline failures, and single-agent mode when used.
4. Uploads the screenshots into `## Screenshots` per §4 of the screenshots reference and verifies that every image renders. For skipped screenshots, writes the one-line reason. For a blocked capture or upload, follows §5.

Do not merge the PR, mark it ready, request reviewers, or change repository settings unless the user asks.

## Completion

Finish only after the PR contains the signed-off commit and the screenshots or the reason they were skipped. Report the tier and mode, branch, worktree path, start SHA, pushed commits, PR URL, validation and sign-off, skipped checks, and unresolved risks. Leave the worktree in place unless the user asks to remove it. If pushing, opening the PR, or uploading screenshots is blocked, keep the branch reviewable and report the exact blocker.
