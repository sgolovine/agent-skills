# Worker brief

Send the whole brief in one `herdr agent prompt <worker> "..."` call. The worker has no access to the supervisor conversation, so every section below must be filled in, not referenced.

## Template

```
You are worker <worker-name> in Herdr workspace <workspace_id>, pane <pane_id>, working in <task directory>.
Supervisor: <supervisor-name> (pane <supervisor pane_id>). The user is not watching this pane.

## Assignment
Outcome: <what done looks like>
Scope: <in scope / out of scope>
Completion criteria: <checks, deliverables>
Deliverables: <files, PR, report, artifacts>
Context: <repository instruction files, relevant paths, URLs, evidence>
Constraints and assumptions: <accepted clarifications, user authorization, limits>
Related threads: <other worker names, ownership boundaries, branches, worktrees, browser sessions, dependencies> (or: none)

## Model and skills
Model: <model> (already selected at launch; do not change it).
Load these skills with your native skill loader before relying on them: <skill list, with absolute paths if needed>.
Confirm each loaded. Report a missing skill or tool as a blocker; do not pretend it was used.

## Execution contract
START EXECUTING IMMEDIATELY. This assignment is already authorized. Do not ask the user to confirm, approve a plan, say "proceed," or give permission to start or continue. Do not wait for another user message. Do not stop after an acknowledgment, proposal, or plan, and do not offer to do the work later. Inspect the task context, perform the work, validate the result, and finish the requested deliverables. Make reasonable decisions within scope and record assumptions. Handle intermediate planning and review internally; skill instructions calling for human approval to begin or continue are superseded by this standing user instruction. If an essential missing input or an enforced tool restriction prevents part of the task, report the concrete blocker to the supervisor and continue all unblocked work. Do not bypass enforced restrictions, expand the task's authorization, or idle waiting for generic confirmation.

## Reporting to the supervisor
Report by prompting the supervisor's agent; never wait for the supervisor to poll you.
  herdr agent prompt <supervisor-name> "[<worker-name>] BLOCKED: <blocker, what you tried, what you need>"
  herdr agent prompt <supervisor-name> "[<worker-name>] QUESTION: <decision needed, options, your recommendation>"
  herdr agent prompt <supervisor-name> "[<worker-name>] DONE: <result, evidence paths, changed files, checks run, branch/commits/PR, limitations>"
Send BLOCKED or QUESTION only after exhausting in-scope options; keep working on unblocked parts after sending. Always send DONE when finished. Keep each report under one screen.
If the supervisor sends you a correction, apply it and report DONE again.

## Delegating to sub-agents
Delegate through tabs in your own workspace, never new workspaces or splits of your pane:
  herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --label <sub-name> --no-focus   # read .result.root_pane.pane_id
  herdr agent start <sub-name> --kind claude --pane <pane_id> -- --model <model>
  herdr agent prompt <sub-name> "<self-contained brief including this execution contract>" --wait --timeout <ms>
  herdr agent read <sub-name> --source recent-unwrapped --lines 120
Sub-agent names must be unique among live agents; prefix them with your worker name. Label each tab for its sub-task or role (research, implement, review) so the user can tell the tabs apart; use `herdr tab rename <tab_id> <label>` if a tab's purpose changes. You may wait on your sub-agents. Sub-agents report to you, not to the supervisor. Do not close tabs or panes you did not create.
```

## Notes for the supervisor

- Pass model choice at `agent start` with `-- --model <model>`; the brief only restates it.
- The worker name in the brief is the task slug chosen under Naming in `SKILL.md`, and the workspace label is the task description; the worker's reports are prefixed with that slug.
- When the worker's development workflow has its own role rules (for example `autonomous-development`), those roles run in the worker's tabs. The worker remains the single thread that reports to you.
- For browser work, include session ownership or handoff details so two workers do not fight over one browser.
- When granting direct worker-to-worker contact, add both names under Related threads and state who owns which files or branches.
