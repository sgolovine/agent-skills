---
name: factory-dev
description: Carry one dispatched development task through research, planning, implementation, validation, screenshots for visible changes, and a ready `factory`-labeled pull request, using supervisor-managed subagents scaled by complexity. Use in a Factory Dev thread or when asked to build something for the Factory.
---

# Factory Dev

You are the supervisor of one Dev thread. Score the task, then research, plan, build, and validate it with fresh subagents sized to that score. Finish with a ready Factory PR and a report to the Dispatch thread. Skipping an agent moves its work to the development role; it never removes the work. You never merge: the Factory loop owns review and merge.

## Requirements

- T3 Code. Read `../../references/factory/t3.md`. If T3 is absent, report `factory-dev requires T3 Code.` and stop.
- `gh` authenticated with push and PR rights. Read `../../references/factory/github.md`; `<r>` is `owner/repo`.
- The brief gives the outcome, scope, acceptance criteria, task slug, default branch, and the Dispatch thread id. Invoked directly by a user, ask only questions that would change the result, and report in this thread instead.

## Baseline

The Dev thread is already an isolated worktree on `factory/<slug>`, created from `origin/<default branch>`. Use it; never create another worktree or `cd` elsewhere.

1. Run `git status --short --branch`, `git remote -v`, and `git worktree list`. Require a clean tree on `factory/<slug>`.
2. `git fetch --prune origin`. Require `HEAD` to be an ancestor of `origin/<default branch>`. Record `HEAD` as the start SHA.
3. Outside such a worktree (a user invoked you directly), apply `../../references/worktrees.md` with start point `origin/<default branch>` and branch `factory/<slug>`, and work only there.

## Score and allocate

Before any repository work, score the task 1–10 by scope, uncertainty, risk, and dependencies: 1–3 small and well understood, 4–5 bounded with moderate uncertainty, 6–10 broad or high risk. State the score, the reason, and the agents you will use. Rescore when findings change the scope.

| Score | Agents |
| --- | --- |
| 1–2 | None. This thread does every stage, including screenshots and the PR. |
| 3 | A development agent. It also researches, plans if needed, runs checks, and captures screenshots. |
| 4–5 | A development agent (also researches) and a separate validation agent (also captures screenshots). |
| 6–10 | A research agent unless findings already exist, a development agent, and a validation agent (also captures screenshots). |

- Add a planning agent at any score from 3 when no actionable plan with acceptance criteria exists; otherwise the development role plans. Add other agents only for a stated need.
- Delegate with the delegation block in `../../references/factory/t3.md`, or native subagents that support the chosen model. Use the newest Opus unless the brief names a model.
- Give every agent a fresh assignment: the request, its role and scope, repository instructions, worktree path, branch, start SHA, the accepted plan or predecessor findings, acceptance criteria, and the return shape. Never reuse a session for a new assignment, correction, or revalidation.
- Keep the stage order: research → plan → development → validation. Accept each stage before the next starts. Parallelize only independent work. One writer at a time in the worktree.

| Role | Returns |
| --- | --- |
| Research | Evidence, touch points, constraints, open questions. |
| Planning | The plan below. |
| Development | Implemented steps, deviations, changed files, commits, check results. |
| Validation | Each criterion met, unmet, or blocked, with evidence and screenshots. It makes no fixes. |

## Coordinate

Other Dev threads may work in the same repository. Before editing, check `t3_thread_list {settled:false}` and open Factory PRs (`gh pr list --label factory`, then `gh pr view <n> --json files`) for overlapping files or interfaces. Keep to your scope. If an overlap changes the plan, send the Dispatch thread a `QUESTION` and continue unblocked work. Before final validation, fetch `origin/<default branch>` and merge it in if it moved (never rebase published commits), resolve conflicts keeping both intents, and rerun affected checks. Name overlapping PRs in the PR body.

## Plan

Present the plan in this thread and accept it before implementation. Keep plan files out of the commit. Include:

- the outcome in concrete terms and any assumptions;
- the files, modules, APIs, and commands involved;
- ordered implementation steps;
- acceptance criteria and the evidence that proves each one (tests, commands, manual checks);
- whether the change has visible output (UI, rendered docs, CLI output, API responses). If so, the screenshot scenarios per `../../references/factory/screenshots.md`; if not, the one-line reason;
- risks, migrations, or compatibility notes when relevant.

Capture Before images at the start SHA before UI behavior changes.

## Implement

- Read the code and tests at each touch point first. Follow repository patterns. Keep the change in scope: no refactors, formatting sweeps, or dependency upgrades the task does not need.
- Add or update tests near the changed behavior. When a test is not practical, say why and use the strongest other check.
- Commit each coherent milestone as you go (for example API change, core logic, tests, docs). One commit only for a truly tiny change. No `WIP` messages and no empty commits.
- Before each commit: run the fastest relevant check, `git status --short`, stage explicit paths, and read `git diff --cached`.
- Use the repository's commit convention, else Conventional Commits.
- Push after the first commit with `git push -u origin factory/<slug>`, then after every commit. Never amend, squash, rebase, or force-push published commits.

## Validate

Run the repository's own checks: type check, lint, unit tests, integration or end-to-end tests, build, and manual checks for behavior tests do not cover. Validate the final commit against each plan step and acceptance criterion. Record each command and result; for a check that cannot run, record the command, the failure, and the risk.

For scores 3–10, an implementation issue goes to a brand-new development agent with the plan, findings, and current commit; then a brand-new validation agent revalidates when one is allocated. Repeat until the evidence supports sign-off or a concrete blocker remains. Record your sign-off with the validated SHA. Any later change voids it.

Screenshots are owned by the Dev thread at scores 1–2, the development agent at 3, and the validation agent at 4–10. They are evidence, not a substitute for checks. Only changes with visible output need them.

## Open the Factory PR

At scores 3–10 a fresh development agent may do steps 1–3; this thread does steps 4–6.

1. Confirm the branch equals the signed-off commit, every commit is pushed, and the tree is clean.
2. Write the body to a file outside the checkout per `../../references/factory/pr-writing.md`, with `## Screenshots` set to `Pending upload.` when images are planned. Create a ready (non-draft) PR, or reuse the one that already exists for the branch (`gh pr view factory/<slug>`):
   ```sh
   gh pr create --repo <r> --base <default branch> --head factory/<slug> --title "<title>" --body-file <file>
   ```
3. Upload the screenshots into the PR body per `../../references/factory/screenshots.md`. If capture or upload fails, write the blocker in `## Screenshots` and keep going.
4. Add the label last, so the Factory loop sees only a finished PR: `gh pr edit <n> --repo <r> --add-label factory`.
5. `link_pull_request {url:"<PR URL>"}` from this thread.
6. Report to the Dispatch thread with the reporting block from `../../references/factory/t3.md` and tag `[<slug>]`:
   ```
   [<slug>] DONE: pr=<PR URL> head=<oid> checks=<command: result, ...> screenshots=<uploaded|none: reason|blocked: reason>; <known gaps or none>
   [<slug>] BLOCKED: <blocker, what you tried, what you need>
   [<slug>] QUESTION: <decision needed, options, recommendation>
   ```

Never merge, request reviewers, or change repository settings. If push or PR creation is blocked, leave the branch reviewable and report `BLOCKED` with the exact error.

## Completion

Finish only when the PR exists with the `factory` label, holds the signed-off commit, and its body has validation and screenshots (or the reason or blocker). Report the branch, worktree path, commits, PR URL, checks, sign-off, and remaining risks. Leave the worktree in place; the Factory loop cleans it up after merge.
