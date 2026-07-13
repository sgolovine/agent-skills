---
name: commit-and-pr
description: Create intentional Conventional Commits from all local repository changes, push the current branch, and open a GitHub pull request with the GitHub CLI. Use when the user asks to commit and publish work, turn a working tree or existing branch into a PR, or create commits and a PR in one workflow.
---

# Commit and PR

## Operating Principle

Gate on GitHub CLI availability, commit the complete local change set in focused Conventional Commits, push when needed, and use `gh` to create or find the pull request. A clean working tree or a branch with no unpushed commits skips that phase; it does not stop PR creation.

## Required Startup Gate

Run this before any repository inspection or mutation:

```sh
command -v gh >/dev/null 2>&1
```

If it fails, report that GitHub CLI is required and stop the skill immediately. Do not inspect, stage, commit, branch, push, or attempt a PR. Do not substitute another GitHub tool or API.

## Workflow

1. After the installation gate passes, verify GitHub CLI access with `gh auth status` and repository access with `gh repo view`. Stop without changing the repository if either fails.
2. Inspect the current branch, remotes, upstream, repository status, staged diff, unstaged diff, and untracked files. Resolve the base branch with `gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'`.
3. If HEAD is detached, stop and report the blocker. If the current branch is the base branch and local changes need commits, create a short, descriptive branch before staging. Otherwise retain the current branch.
4. If the working tree contains changes, review the complete change set and decide the exact number of focused commits before staging. Include every tracked, staged, unstaged, and untracked change in exactly one planned commit. Split changes when purposes, types, scopes, risks, or review contexts differ.
5. Draft each commit message in Conventional Commits 1.0.0 form:

```text
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

6. Use `feat` for new user-facing capability, `fix` for a bug fix, or another fitting lowercase type such as `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `style`, or `chore`. Keep the header imperative and concise. Signal a breaking change only when truthful.
7. Validate every message before committing:

```sh
python3 <skill-dir>/scripts/validate_conventional_commit.py --message-file <message-file>
```

8. Stage each planned commit deliberately, inspect `git diff --staged`, and commit with `git commit -F <message-file>`. Repeat until the complete local change set is committed. If the working tree was already clean, skip steps 4–8 and continue.
9. Compare the branch with its upstream. Push with `git push --set-upstream origin HEAD` only when the branch has no upstream or contains unpushed commits. If nothing needs pushing, continue directly to the PR step.
10. Review the complete branch diff and commit list against the base branch. Create a concise PR title and a body that summarizes the change and records validation performed. Write the body to a file.
11. Use `gh pr view --json url` to detect an existing PR for the branch. If one exists, return its URL. Otherwise open the PR with:

```sh
gh pr create --base <base-branch> --head <current-branch> --title <title> --body-file <body-file>
```

12. Do not stop merely because there are no unstaged changes, no staged changes, or no unpushed commits. Proceed directly to PR discovery or creation. If GitHub reports that the branch has no commits to propose against the base branch, report that exact blocker.
13. Verify the resulting PR with `gh pr view --json number,title,url,baseRefName,headRefName`.

## Commit Guidance

- Treat one commit as a deliberate conclusion, not the default. Prefer multiple focused commits when the changes can be reviewed independently.
- Read `references/conventional-commits.md` when exact message rules matter.
- Preserve unrelated local work by assigning it to an intentional commit rather than dropping, reverting, or hiding it.

## Completion Report

Report each created commit hash, subject, and included files; whether a push occurred; and the PR number, title, base branch, head branch, and URL.
