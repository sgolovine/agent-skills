---
name: git-track
description: Track work on a separately requested task in Git with meaningful commits as work progresses, then push the branch and open a pull request. Use alongside a task when the user wants its changes recorded and published without prescribing a development process.
---

# Git Track

Do the work the user requested, track it in Git as you go, and open a PR when finished. This skill governs Git tracking only; the task, user instructions, and repository conventions determine how to perform the work.

## Startup gates

1. Confirm there is a separate task to perform in the current request or active conversation. Invoking this skill alone is a no-op: immediately return exactly `This skill must be run with a task`. Do not inspect or change the repository.
2. Run `git rev-parse --is-inside-work-tree` in the task directory. If it fails or does not return `true`, return exactly `This skill must run run within a git repo`. Do not initialize a repository.

## Track the task

1. Inspect repository instructions, status, staged and unstaged changes, the current branch, remotes, and recent commit messages. Record the starting state so existing work can be distinguished from task changes.
2. Use a branch suitable for the task's PR. Continue an existing task branch when appropriate; otherwise create a descriptive branch following repository conventions, defaulting to `codex/`. Establish the intended remote and PR base from repository context.
3. Perform the requested task. Commit meaningful, coherent checkpoints as work progresses. Use multiple commits for work larger than a very small change; do not defer everything into one final commit or manufacture empty or arbitrary splits.
4. Review and stage only changes belonging to the task, using paths or hunks as needed. Preserve unrelated pre-existing changes and staged work. Inspect each commit's staged diff before committing.
5. Write precise messages that reflect and elevate repository standards. Follow the repository's message format; do not impose Conventional Commits unless the repository requires or uses them. Name the concrete change in a concise subject, and explain its purpose or non-obvious consequences in the body when useful. Avoid vague messages such as `updates` or `misc fixes`.
6. Record follow-up corrections in additional focused commits. Do not squash the progression into one commit or rewrite shared history unless requested.

## Finish with a PR

1. Review the task's commits and complete diff against the intended base. Confirm all task changes are committed and unrelated work remains intact. Include validation results from the task without introducing a separate development or testing process.
2. Push the task branch to the intended remote and open a PR using the available hosting tool, such as `gh` for GitHub. If the task branch already has an open PR, update it to reflect the completed work and return its URL.
3. Give the PR a concrete title and a concise description of the resulting behavior, why it changed, and validation performed. Follow the repository's PR template when present.
4. Verify the PR's URL, head branch, and base branch. Report the commit hashes and subjects, push result, and PR link.

If the task produces no changes to propose, report that outcome without creating empty commits or a PR. If committing, pushing, or PR creation is blocked, preserve completed work and report the exact blocker and remaining step; do not claim publication succeeded.
