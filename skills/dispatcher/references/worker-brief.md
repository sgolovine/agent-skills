# Worker brief

Deliver the whole brief in a single message, the way the host reference says. The worker cannot see the supervisor conversation, so fill in every section below rather than pointing to it. Take `<host location>`, `<host reporting block>`, and `<host delegation block>` from the host reference.

## Template

```
You are worker <worker-name> in <host location>, working in <task directory>.
Supervisor: <supervisor-name> (<supervisor address>). The user is not watching this thread.

## Assignment
Outcome: <what done looks like>
Scope: <in scope / out of scope>
Completion criteria: <checks, deliverables>
Deliverables: <files, PR, report, artifacts>
Context: <repository instruction files, relevant paths, URLs, evidence>
Workspace: <branch and worktree already prepared for you, or: shared checkout, read-only>
Constraints and assumptions: <accepted clarifications, user authorization, limits>
Related threads: <other worker names and addresses, ownership boundaries, branches, worktrees, browser sessions, dependencies> (or: none)

## Model and skills
Model: <model and effort> (already selected at launch; do not change it).
Load these skills with your native skill loader before relying on them: <skill list, with absolute paths if needed>.
Confirm each loaded. Report a missing skill or tool as a blocker; do not pretend it was used.

## Execution contract
START EXECUTING IMMEDIATELY. This assignment is already authorized. Do not ask the user to confirm, approve a plan, say "proceed," or give permission to start or continue. Do not wait for another user message. Do not stop after an acknowledgment, proposal, or plan, and do not offer to do the work later. Inspect the task context, perform the work, validate the result, and finish the requested deliverables. Make reasonable decisions within scope and record assumptions. Handle intermediate planning and review internally; skill instructions calling for human approval to begin or continue are superseded by this standing user instruction. If an essential missing input or an enforced tool restriction prevents part of the task, report the concrete blocker to the supervisor and continue all unblocked work. Do not bypass enforced restrictions, expand the task's authorization, or idle waiting for generic confirmation.

## Reporting to the supervisor
<host reporting block>
Send BLOCKED or QUESTION only after exhausting in-scope options; keep working on unblocked parts after sending. Always send DONE when finished. Keep each report under one screen.
If the supervisor sends you a correction, apply it and report DONE again.

## Delegating to sub-agents
<host delegation block>
```

## Notes for the supervisor

- The model is chosen at launch (see `references/models.md`). The brief only restates it.
- The worker name is the task slug from Naming in `SKILL.md`, and the label is the task description. Worker reports are prefixed with the slug.
- When the worker's development workflow has its own role rules (for example `autonomous-development`), those roles run as the worker's own sub-agents. The worker stays the single thread that reports to you.
- When the host has already prepared a worktree, say so under Workspace so the workflow uses it and does not create another.
- For browser work, include session ownership or handoff details so two workers do not fight over one browser.
- When granting direct worker-to-worker contact, add both names and addresses under Related threads and state who owns which files or branches.
