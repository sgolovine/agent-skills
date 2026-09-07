---
name: coordinate
description: Coordinate Codex CLI work with other agents active in the same repository, agree on ownership and shared changes, and commit and push coherent checkpoints throughout the task. Use when multiple agents are working concurrently in a repository or the user requests coordinated development.
---

# Coordinate

Other agents are working in the same repository. Coordinate with them throughout the task and publish progress through commits and pushes as you work.

## Coordinate ownership

- Inspect repository instructions, working-tree status, branches, and worktrees. Use available agent coordination tools or the team's established coordination channel to identify active agents and their assignments.
- Before editing, share your scope, branch or worktree, expected files, and dependencies. Agree on ownership for overlapping files and on who integrates shared changes. Keep working on independent parts while an overlap is being resolved.
- Prefer separate worktrees and task branches when agents would otherwise share a checkout. Worktrees isolate edits but do not replace coordination over shared files or interfaces.
- Communicate changes to scope, shared interfaces, blockers, and completed checkpoints. Re-read files that another agent has changed before editing them. Preserve their work; resolve overlapping intent with the owning agent instead of overwriting it.
- If no agent communication channel is available, report that limitation, isolate your work, and defer unresolved overlapping edits. Do not assume silence establishes ownership.

## Commit and push as you work

- Create a commit after each coherent, reviewable increment and push it to the agreed remote branch. Do this throughout implementation, not only at the end. Follow the repository's commit conventions and run the checks relevant to each increment.
- Review the diff and stage only your task's changes. Inspect the staged diff before committing; do not include another agent's changes without an agreed handoff.
- In a shared checkout, coordinate exclusive access for staging and commits because agents share the Git index. Also coordinate branch switches and integration operations; do not stash, reset, clean, or otherwise disrupt another agent's work.
- Use ordinary pushes. If a push is rejected because the remote advanced, fetch and inspect the new commits, coordinate integration with the affected agents, then validate and retry. Do not force-push over shared work or rewrite another agent's commits.
- Share the pushed commit IDs, branch, validation results, and any integration needs with the other agents. If publishing is blocked by missing access or an unresolved destination, retain local commits, report the blocker, and continue independent work without repeatedly retrying the same failure.

## Finish

Verify that your completed changes are committed and pushed, report any remaining local work or publishing blockers, and hand off the final branch and commit IDs with validation results and unresolved dependencies.
