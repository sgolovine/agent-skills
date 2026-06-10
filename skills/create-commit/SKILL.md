---
name: create-commit
description: Create intentional Git commits from local changes using the Conventional Commits 1.0.0 format. Use when the user asks Codex to commit work, make a git commit, stage changes, prepare a commit message, split local changes into commits, or ensure commit messages follow Conventional Commits.
---

# Create Commit

## Operating Principle

Commit the complete current repository change set. Inspect the whole diff, decide the exact number of focused commits before staging, write Conventional Commit messages that reflect behavior, and verify each message before running `git commit`.

## Workflow

1. Inspect repository state with `git status --short` and review the complete change set with `git diff` plus `git diff --staged` when applicable.
2. Look over the entire diff before staging and decide how many commits should be created. Treat a single commit as a deliberate conclusion, not the default.
3. Plan focused commits that cover every tracked, staged, unstaged, and untracked change in the repository. Prefer multiple concise commits when changes have distinct purposes, types, scopes, risk profiles, or review contexts; avoid broad "miscellaneous" grouping. The plan must assign every local change to exactly one commit.
4. Choose a Conventional Commit header for each planned commit:
   - Use `feat` for a new user-facing capability.
   - Use `fix` for a bug fix.
   - Use another lowercase type when it better describes the work, such as `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `style`, or `chore`.
   - Add a scope only when it clarifies the affected area, for example `fix(auth): ...`.
   - Add `!` or a `BREAKING CHANGE:` footer only when the commit introduces a breaking API or behavior change.
5. Write each message in this shape:

```text
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

6. Use an imperative, concise description in the header. Keep body text for why the change was needed, non-obvious implementation context, migration notes, or test coverage.
7. Validate each drafted message with `python3 <skill-dir>/scripts/validate_conventional_commit.py --message-file <file>` or `--message "<message>"`.
8. Stage deliberately with `git add <paths>` or `git add -p` so every local change is included in exactly one planned commit. Re-check `git diff --staged`.
9. Commit with a message file: `git commit -F <message-file>`.
10. Report each commit hash, final subject, and files included.

## Message Guidance

- Prefer one commit only when all changes serve one tightly defined purpose. Split commits when types, scopes, user-facing purposes, implementation layers, generated artifacts, documentation, tests, or cleanup work can be reviewed independently. The split should partition the complete local change set rather than exclude files.
- More commits are preferable to one broad commit when the work naturally separates into coherent review units.
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
