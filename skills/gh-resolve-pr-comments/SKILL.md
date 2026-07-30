---
name: gh-resolve-pr-comments
description: Resolve GitHub pull request review comments in an isolated linked worktree per PR with supervisor-managed subagents. Use when given a GitHub PR link, multiple PR links, or a GitHub repository link and asked to classify, plan, implement, verify, commit, and reply to unresolved PR comments or review threads.
---

# GH Resolve PR Comments

## Operating Principle

Treat each unresolved PR comment as a tracked work item on an isolated copy of the exact PR head: create a dedicated linked worktree before repository-backed evaluation, classify first, verify before editing, implement only from a linted plan, verify independently, then publish and reply with evidence that a later classifier can recognize as resolved.

## Inputs

Accept:

- one GitHub PR URL,
- multiple GitHub PR URLs,
- one GitHub repository URL.

For a repository URL, list all open PRs and process them as if the user had supplied those PR links directly. All PRs in one run must have the same base repository as the current checkout; if supplied PR URLs span repositories, ask the user to split them into repository-specific runs. If the GitHub target is missing, inaccessible, or not specific enough to identify PRs, ask one concise clarification and stop.

## Setup

Use the current agent as **Supervisor**. Spawn subagents for worker roles when the harness supports subagents; otherwise preserve the same role boundaries in a serialized run.

1. Resolve the GitHub targets. Use the GitHub connector when available, or `gh`/GitHub API commands when that is the local pattern. Gather PR metadata, branch refs, review threads, PR conversation comments, requested changes, prior automated replies, and current resolution state. Record each PR's base repository, head repository, head ref, and immutable current head OID.
2. Confirm that the local checkout matches the target base repository and inspect its status and remotes. Preserve unrelated local changes; this checkout is only the control checkout for fetching refs and managing linked worktrees.
3. Read [the shared linked worktree contract](../../references/worktrees.md).
4. Before any repository-backed classification, planning, runtime evaluation, or editing, create one dedicated worktree per PR:
   - Fetch the recorded head ref directly from its head repository into a unique local ref without checking it out, then require the fetched commit to equal GitHub's recorded head OID.
   - Apply the linked worktree contract with the verified head OID as the start point, a unique local branch such as `codex/pr-<number>-comments-<suffix>`, and a unique sibling path outside the control checkout.
   - Record the worktree as `PR_WORKTREE` and the fetched OID as the expected remote head. All workers must use that PR's worktree as their repository root; never evaluate or modify PR code in the control checkout.
5. Create a run directory outside every checkout, for example `../<repo>-worktrees/_runs/pr-comment-resolution/<YYYYMMDD-HHMMSS>/`, with per-PR evidence subdirectories.
6. Read `$playwright-browser` from `/home/sgolovine/Projects/agent-skills/skills/playwright-browser/SKILL.md`, then start exactly one shared headless Playwright session from a PR worktree root after the run directory exists:

   ```sh
   PLAYWRIGHT_BROWSER_SCRIPT="/home/sgolovine/Projects/agent-skills/skills/playwright-browser/scripts/playwright-browser.mjs"
   node "$PLAYWRIGHT_BROWSER_SCRIPT" start --run-dir "$RUN_DIR" --fresh --url about:blank
   BROWSER_SESSION_STATE_FILE="$RUN_DIR/browser-session/session.json"
   node "$PLAYWRIGHT_BROWSER_SCRIPT" status --state-file "$BROWSER_SESSION_STATE_FILE"
   ```

   If the target repo has no installed `playwright` dependency or a shared session cannot be started, do not install a transient browser dependency with `npx`; record the limitation and continue only with non-browser verification where that is sufficient.
7. Read `references/role-contracts.md` before spawning worker agents. Every worker receives its assigned `PR_WORKTREE`; every browser-using worker also receives the shared session state file, command prefix, assigned tab instructions, viewport, evidence directory, and the rule that no separate browser session may be created.

## Workflow

1. **Classify comments.** Spawn one Classifier per PR. It returns clean `resolved`, `actionable`, and `non_actionable` lists with comment URLs, thread IDs, rationale, and requested outcome. Any repository inspection must use that PR's assigned worktree.
2. **Plan actionable work.** For each `actionable` comment, spawn a Planning agent to verify that the issue is present before any edits. Read-only Planning agents may run in parallel when their tools will not write; all implementation on one PR worktree is serialized.
3. **Handle unverified issues.** If a Planning agent cannot verify the issue, the Supervisor replies to the original GitHub comment with `Codex resolution: unable to verify`, the verification attempted, and the missing information or questions. Do not route that item to implementation.
4. **Lint every plan.** The Planning agent must spawn a plan-lint subagent and revise until the plan reaches `100/100` readiness with no open questions. If missing external information prevents a score of `100`, treat the item as unable to verify and comment accordingly.
5. **Implement from the plan.** Spawn an Implementation agent only after plan lint passes. The agent follows the plan in the assigned PR worktree, runs the required checks, and creates one or more detailed local commits when files change. Do not create empty commits for evidence-only comments, push, or write to GitHub from an Implementation agent.
6. **Verify independently.** After implementation, spawn a Verification agent that checks the resolved behavior from the assigned PR worktree without relying on the implementer's conclusion. Use screenshots for browser/web behavior and bounded logs or command output for backend, CLI, or non-visual work.
7. **Publish verified commits when code changed.** After verification passes, the Supervisor re-fetches the recorded PR head repository and ref and requires it to equal the expected remote head. For code-changing items, push the local worktree `HEAD` to that exact head ref with an explicit non-force refspec, require GitHub's PR head OID to equal the pushed commit, and update the expected remote head. For evidence-only items, require the PR head to remain at the expected OID and skip the push. If the remote moved or required publication fails, stop, preserve the worktree, and do not claim the comment is resolved.
8. **Reply and resolve.** The Supervisor replies to each original actionable comment or review thread with `Codex resolution: resolved`, relevant plan, implementation or no-code outcome, published commits when applicable, checks, and public artifact links or concise evidence summaries. Do not post local filesystem paths, browser session state, secrets, environment values, or raw logs to GitHub. If GitHub thread resolution is available and the evidence is sufficient, mark the conversation resolved after replying.
9. **Summarize the PR.** When all workers finish for a PR, post one PR-level summary comment listing resolved comments, non-actionable comments, unable-to-verify comments, published commits, checks, and public artifacts or evidence summaries. Use the same `Codex resolution` marker style so future Classifier runs can distinguish final summaries from new reviewer requests.
10. **Clean up runtime resources.** Stop only the shared Playwright daemon started for this run. If ownership cannot be confirmed, leave it running and report the state file and daemon log path. Leave each PR worktree in place for review or follow-up unless the user explicitly requests removal.

## Classification Rules

- `Resolved`: the GitHub thread is already resolved, or an existing commit/reply clearly satisfies the request. A supervisor reply containing `Codex resolution: resolved` plus commits or verification evidence is enough to classify the original comment as resolved unless a later human reply reopens the issue.
- `Actionable`: the comment requests a code change, test, screenshot, log, documentation update, concrete investigation, or answer that can be verified against the repository or running product.
- `Non-Actionable`: the comment is a summary, status note, standalone screenshot label, acknowledgement, duplicate without new requested work, or observation that does not ask for a change, answer, or verification artifact.

Treat reviewer questions as actionable when they require investigation or a response. Treat vague requests as actionable only if the Planning agent can verify the issue and produce a concrete plan without guessing.

## Completion Criteria

Before finishing, verify that:

- every open PR target was classified,
- every actionable comment has either a verified resolution reply or an unable-to-verify reply,
- implementation checks from each linted plan passed or failures were reported with exact reasons,
- every PR was evaluated from its own linked worktree at the verified PR head,
- code-changing work was committed and pushed to the PR head with detailed messages tied to the PR/comment context,
- browser screenshots or non-browser logs were captured where relevant,
- unrelated local changes were preserved,
- each linked worktree path and final state were reported,
- the shared Playwright session was stopped or its ownership uncertainty was reported.
