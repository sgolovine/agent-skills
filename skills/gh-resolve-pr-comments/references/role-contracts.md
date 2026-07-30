# Role Contracts

Load this file before delegating PR comment resolution work. Keep GitHub writes under Supervisor control.

## Shared Worker Handoff

Every worker receives:

- control checkout path, assigned PR worktree root, local worktree branch, and PR URL/number,
- base branch, head repository, head ref, base SHA, current head SHA, and expected remote head OID,
- comment URL, comment ID, thread ID, file path, line/range, and quoted comment text when working on one comment,
- run directory and evidence directory,
- `BROWSER_SESSION_STATE_FILE`, Playwright command prefix, assigned tab or tab-creation instructions, viewport, and the no-separate-browser rule for browser work,
- current worktree status summary and the rules to preserve unrelated changes and keep all repository operations inside the assigned worktree,
- expected return shape and whether GitHub writes are prohibited.

The control checkout is read-only worker context. Workers must not create, remove, or repoint worktrees. Only the Supervisor may push commits, post GitHub comments, or resolve threads.

Workers should return compact structured output. Include source URLs, commands, screenshots, logs, commit hashes, and uncertainty; do not paste unbounded logs.

Local evidence paths and browser session state are for worker handoffs only. GitHub replies may include public artifact links or concise evidence summaries, but never local filesystem paths, `BROWSER_SESSION_STATE_FILE`, daemon tokens, secrets, environment values, or raw logs.

## Classifier Agent

Task:

1. Read the PR review threads, PR conversation comments, requested-changes reviews, existing bot/supervisor replies, and current GitHub resolution state.
2. Classify only reviewer comments and unresolved discussion items. Do not treat a prior `Codex resolution` summary as new work unless it asks for new work.
3. Return three lists:

```json
{
  "pr": "https://github.com/owner/repo/pull/123",
  "resolved": [
    {
      "comment_id": "string",
      "thread_id": "string|null",
      "url": "string",
      "summary": "string",
      "reason": "already resolved in GitHub | satisfied by Codex resolution reply | duplicate | obsolete",
      "evidence": "string"
    }
  ],
  "actionable": [
    {
      "comment_id": "string",
      "thread_id": "string|null",
      "url": "string",
      "location": "path:line or PR conversation",
      "summary": "string",
      "requested_outcome": "string",
      "why_actionable": "string",
      "dependencies": ["string"]
    }
  ],
  "non_actionable": [
    {
      "comment_id": "string",
      "thread_id": "string|null",
      "url": "string",
      "summary": "string",
      "reason": "summary | acknowledgement | screenshot label | no requested work | duplicate without new ask"
    }
  ]
}
```

Classifier confidence must come from current GitHub state plus the latest PR head. If a later human reply appears after a `Codex resolution` reply, classify the later human reply independently.

## Planning Agent

Input: one actionable comment plus PR context.

Task:

1. Verify the issue before planning edits. Inspect the current code, PR diff, surrounding ownership boundaries, existing tests, and runtime behavior when needed.
2. For browser/web behavior, use the assigned shared Playwright tab and store screenshots under the evidence directory.
3. Discover project checks before planning completion criteria. Inspect package scripts, test configs, CI files, Makefiles, task runners, and local docs.
4. If the issue cannot be verified, return `unable_to_verify` with attempted commands, observations, missing information, and the exact questions for the Supervisor to post.
5. If verified, produce an implementation plan with:
   - original comment URL and text,
   - verified problem statement and evidence,
   - affected files/modules and relevant code context,
   - step-by-step implementation plan,
   - exact checks/tools the Implementation agent must run before completion,
   - expected browser screenshots, logs, or other verification artifacts,
   - commit guidance,
   - risks, rollback notes, and constraints.
6. Spawn a Plan Linter with only the draft plan and needed code context. Revise until the linter returns `100/100`.

Planning output:

```json
{
  "status": "planned | unable_to_verify",
  "comment_id": "string",
  "comment_url": "string",
  "verified_issue": "string",
  "evidence": ["path-or-command-summary"],
  "plan": ["ordered concrete steps"],
  "required_checks": ["exact command or tool"],
  "required_verification": ["screenshot/log/test expectation"],
  "commit_guidance": "string",
  "lint_score": 100,
  "lint_notes": []
}
```

## Plan Linter

Score the plan out of `100`. Passing requires `100/100` and no open questions.

- `20` verification basis: the issue is reproduced or convincingly confirmed from current code/PR state.
- `25` implementation specificity: steps name files, functions, data flow, and expected behavior.
- `25` test and evidence criteria: exact commands, screenshots, logs, or assertions are listed.
- `15` repo fit: the plan follows local architecture, scripts, conventions, and ownership boundaries.
- `15` safety: git state, unrelated changes, rollback, concurrency, and external side effects are addressed.

Return:

```json
{
  "score": 85,
  "blocking_issues": ["specific ambiguity or missing fact"],
  "suggested_fixes": ["specific edit to the plan"],
  "open_questions": ["question that must be answered before implementation"]
}
```

Reject plans containing unresolved placeholders such as `TBD`, `maybe`, `if necessary`, or unchecked assumptions about available tools. If the only blocker is missing external information, tell the Planning agent to mark the comment `unable_to_verify`.

## Implementation Agent

Input: one linted plan with `lint_score: 100`.

Task:

1. From the assigned PR worktree, re-check git status, local `HEAD`, and the current PR head before editing. Stop if either the worktree or remote head differs from the Supervisor's expected state.
2. Implement only the approved plan. If reality diverges, stop and return the deviation to the Supervisor rather than improvising materially different work.
3. Preserve unrelated local changes. Do not rewrite history unless explicitly instructed by the user.
4. Run every required check/tool from the plan. Add or update focused tests when the plan calls for them or the risk justifies them.
5. Create one or more detailed local commits when files changed. Include PR/comment context in commit bodies when useful. Do not create an empty commit for evidence-only work.
6. Return changed files, commit hashes, checks run, check results, evidence paths, final worktree status, and any plan deviations.

Implementation agents do not push, post GitHub comments, or mark threads resolved.

## Verification Agent

Input: original comment, final plan, implementation report, commit hashes, and evidence directory.

Task:

1. Independently inspect the diff and relevant code path from the assigned PR worktree.
2. Re-run the required checks or a defensible subset when full checks are too expensive; report any skipped checks with reasons.
3. Verify the comment's requested outcome:
   - for browser/web behavior, use the shared Playwright session and capture screenshots,
   - for backend/CLI behavior, capture bounded command output or logs,
   - for documentation-only changes, inspect rendered or source output as appropriate.
4. Return `pass`, `fail`, or `inconclusive` with evidence paths and concise reasoning.

If verification fails or is inconclusive, the Supervisor routes the item back to Planning or Implementation instead of posting a resolved reply.

## Supervisor GitHub Replies

For code-changing items, post a resolved reply only after independently verified commits have been pushed and GitHub reports the pushed commit as the current PR head. For evidence-only items, require independent verification and confirm that the PR head remains at the expected OID; no commit or push is required. Reply to the original comment or review thread whenever possible. If GitHub only allows a PR-level reply, link the original comment URL.

Resolved template:

```markdown
Codex resolution: resolved

Comment: <original comment URL>
Plan: <one or two sentence plan summary>
Implementation: <commit hashes and concise change summary>
Verification: <checks/screenshots/logs with public artifact links or concise evidence summaries>
Notes: <risk, skipped checks, or no-code-change explanation if relevant>
```

Unable-to-verify template:

```markdown
Codex resolution: unable to verify

Comment: <original comment URL>
Attempted verification: <commands, screenshots, code paths, or observations>
Missing information: <specific questions or unavailable environment/data>
Next step needed: <what a developer/reviewer can provide>
```

PR summary template:

```markdown
Codex resolution summary

Resolved: <count and linked comment IDs>
Unable to verify: <count and linked comment IDs>
Non-actionable: <count and linked comment IDs>
Commits: <hashes>
Checks: <commands and status>
Evidence: <public artifact links or summarized local evidence>
```

Use the exact `Codex resolution` markers so future Classifier runs can distinguish completed work from new reviewer requests.
