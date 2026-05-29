---
name: create-commit
description: Create intentional Git commits from local changes using the Conventional Commits 1.0.0 format. Use when the user asks Codex to commit work, make a git commit, stage changes, prepare a commit message, split local changes into commits, or ensure commit messages follow Conventional Commits.
---

# Create Commit

## Operating Principle

Create the smallest coherent commit the work supports. Inspect the diff, protect unrelated user changes, write a Conventional Commit message that reflects behavior, and verify the message before running `git commit`.

## Workflow

1. Inspect repository state with `git status --short` and review changed files with `git diff` plus `git diff --staged` when applicable.
2. Identify the commit unit. If local changes contain unrelated work, commit only the files or hunks that belong to the requested change and leave the rest untouched. Ask before splitting or staging ambiguous changes.
3. Choose a Conventional Commit header:
   - Use `feat` for a new user-facing capability.
   - Use `fix` for a bug fix.
   - Use another lowercase type when it better describes the work, such as `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `style`, or `chore`.
   - Add a scope only when it clarifies the affected area, for example `fix(auth): ...`.
   - Add `!` or a `BREAKING CHANGE:` footer only when the commit introduces a breaking API or behavior change.
4. Write the message in this shape:

```text
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

5. Use an imperative, concise description in the header. Keep body text for why the change was needed, non-obvious implementation context, migration notes, or test coverage.
6. Validate the drafted message with `python3 <skill-dir>/scripts/validate_conventional_commit.py --message-file <file>` or `--message "<message>"`.
7. Stage deliberately with `git add <paths>` or `git add -p`; do not stage unrelated changes. Re-check `git diff --staged`.
8. Commit with a message file: `git commit -F <message-file>`.
9. Report the commit hash, final subject, staged files included, and any local changes left uncommitted.

## Message Guidance

- Prefer one commit when all changes serve one purpose; split commits when types, scopes, or user-facing purposes differ.
- Put issue references and metadata in footers, for example `Refs: #123` or `Reviewed-by: Name`.
- Use `BREAKING CHANGE: <description>` exactly uppercase when the breaking change is in a footer. `BREAKING-CHANGE:` is also valid by spec, but prefer `BREAKING CHANGE:` for readability.
- If reverting, `revert:` is acceptable; include the reverted commit SHA or issue reference in the body or footer.
- Read `references/conventional-commits.md` when the exact Conventional Commits rules matter.

## Validation

Run the validator before committing:

```sh
python3 skills/create-commit/scripts/validate_conventional_commit.py --message-file /tmp/commit-message.txt
```

The validator catches common structural errors, but the agent must still verify semantic fit: correct type, appropriate scope, and whether breaking-change signaling is truthful.
