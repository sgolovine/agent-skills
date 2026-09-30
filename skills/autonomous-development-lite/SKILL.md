---
name: autonomous-development-lite
description: Carry a small or bounded repository change through research, planning, implementation, validation, UI before-and-after screenshots when applicable, and a draft pull request in one agent thread. Use for unattended development without subagents or harness-specific tools.
---

# Autonomous Development Lite

Complete the request in one agent thread. Keep the research → plan → implementation → validation → PR sequence, but scale each stage to the change. Never spawn subagents, delegate stages, or require human plan approval. Use shell commands and project tools; assume no harness APIs, task managers, browser tools, or worktree helpers exist.

## 1. Establish an isolated baseline

- Infer the repository from the working directory. Read its applicable instructions and inspect `git status --short --branch`, `git remote -v`, and `git worktree list --porcelain`. Preserve pre-existing changes and other worktrees; do not stash, reset, clean, or switch the original checkout.
- Select the remote and parent branch from the request or repository guidance, otherwise use the remote default. Discover it with `git symbolic-ref --short refs/remotes/<remote>/HEAD` or `git ls-remote --symref <remote> HEAD`. Fetch the required refs, prefer the fetched remote parent, and resolve it to a commit SHA with `git rev-parse <parent-ref>^{commit}`. Record any fallback to a verified local parent. Do not assume a particular branch name. If discovery fails, use a verified repository convention and record the assumption; never silently base the work on an unrelated feature branch. Without a Git checkout or a defensible parent, report the setup blocker.
- Choose a unique task branch using repository conventions, otherwise `codex/<short-summary>`, and a unique sibling worktree path outside the repository. Create it with the native Git CLI, substituting the established values:

  ```sh
  git -C "$repo" worktree add -b "$branch" "$worktree" "$start_sha"
  git -C "$worktree" rev-parse HEAD
  git -C "$worktree" status --short --branch
  ```

  Create the destination's parent directory if necessary. Confirm HEAD equals the start SHA and the new worktree is clean. On a name or path collision, choose another name; never overwrite an existing checkout. Perform development, builds, checks, commits, and pushes from this worktree.
- Check publication prerequisites early: for GitHub, inspect `gh auth status` and repository access. An external publication blocker does not prevent useful local implementation and validation. Keep notes, logs, and screenshots outside the checkout unless they are intended project deliverables.

## 2. Research and check the plan against the request

Read the relevant code, call sites, tests, project documentation, dependency manifests, and CI configuration. Establish the current behavior, likely cause or implementation path, and project commands. Research unfamiliar APIs using authoritative documentation only when needed; avoid surveying unrelated code or dependencies.

Write a concise plan in the conversation or external task notes containing:

- The requested outcome, explicit requirements, and necessary assumptions.
- Ordered changes and affected files or interfaces.
- Acceptance criteria tied to each requirement, with tests or manual evidence that will prove them.
- For UI work, the routes, states, and viewports for comparable before-and-after captures.

Review the plan yourself against the original request before editing. Remove unrelated work and resolve gaps using repository evidence and the least disruptive interpretation consistent with the request. Record consequential assumptions and proceed without questions or approval pauses. Revise the plan if discoveries change the implementation, while preserving the requested outcome.

When runtime checks or UI captures are needed, read [runtime and screenshot guidance](references/runtime-and-screenshots.md). Capture the UI baseline before changing its behavior.

## 3. Implement

Follow existing project patterns and make scoped changes. Add or update behavioral tests where they provide meaningful coverage; update docs, configuration, or migrations when the change requires them. Run focused checks while developing and inspect the diff for accidental or unrelated edits.

Resolve ordinary tooling and environment issues yourself: use the documented runtime and lockfile-aware dependency installation, repair task-related failures, and use available local fixtures or test services. Autonomy covers task work, not changing production systems, obtaining new credentials, or overwriting someone else's work. If a prerequisite is genuinely unavailable, preserve progress and report its exact failure instead of waiting for a human or claiming success.

Commit coherent milestones using the repository's convention, falling back to Conventional Commits. One commit is sufficient for an atomic change. Inspect the staged diff and stage task files explicitly. Publish each completed milestone with `git push -u <remote> <branch>` initially and `git push <remote> <branch>` thereafter when access permits. Preserve published history; do not force-push it.

## 4. Validate against both the plan and the request

Review the complete change afresh, including committed and uncommitted diffs. Fetch the parent again and assess intervening changes; integrate required updates with a merge without rewriting published commits, then validate the resulting branch.

Run the relevant checks discovered from project docs and CI: targeted tests, type checks, lint, builds, integration checks, and runtime verification as appropriate. Scale coverage to the behavior and risk, while completing required repository checks. For UI work, exercise the affected flows and capture the after states from the final implementation. Screenshots supplement behavioral checks.

Record each acceptance criterion as met, unmet, or blocked with its evidence. Check the actual requested outcome even if the implementation follows the plan exactly. Fix discrepancies in this same thread and rerun affected checks. Any later code or integration change invalidates affected validation and screenshots. Record final commands, outcomes, and the validated commit SHA; distinguish environment failures or existing failures from regressions. An unmet or unverified requirement remains incomplete.

## 5. Open and verify the PR

Confirm task changes are committed, the worktree is clean, and the remote head matches the validated commit. Use the repository's PR template when present. Prepare a body file with the concrete problem and resulting behavior, relevant implementation notes, validation evidence, assumptions, and any limitations. For GitHub:

```sh
gh pr create --draft --base "$parent" --head "$branch" --title "$title" --body-file "$body_file"
gh pr view "$branch" --json url,baseRefName,headRefName,headRefOid,isDraft,body
```

Use a ready PR only when requested. Verify the target repository, base, head SHA, and description; reuse an existing PR for this branch rather than duplicating it after a retry. For UI changes, publish and verify the labeled screenshot pairs using the reference guidance. Non-UI tasks need no screenshots.

If validation is blocked, still open a draft PR when possible, clearly identifying incomplete criteria. If push, PR creation, or required screenshot publication fails, preserve the branch, commits, artifacts, and prepared PR body, and report the exact blocker. Never fabricate a PR or image URL. Do not merge, request reviewers, or change repository settings unless requested.

Finish with the PR URL, branch and worktree path, validated commit, checks and results, UI evidence when applicable, and any remaining blockers. Claim completion only when the request is satisfied and required evidence is published. Leave the development worktree for review and stop only processes started by this task.
