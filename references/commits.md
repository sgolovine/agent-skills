# Commits

Shared style for agent-written Git commits.

## Format

Always use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/#specification):

```text
<type>[optional scope][optional !]: <description>

<body>

[optional footer(s)]
```

- Type: `feat` for a new capability, `fix` for a bug fix. Otherwise `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `style`, `chore`, or `revert`.
- Scope: only when it clarifies the affected area, for example `fix(auth): ...`.
- Breaking change: `!` before the colon, or a `BREAKING CHANGE: <description>` footer. Use it only when the change breaks an API or behavior.
- Footers: git-trailer form, for example `Refs: #123`. Put issue references and metadata here.

## Title and body

Use the title and the body. The title says what changed. The body says why, plus what a reviewer cannot see in the diff: non-obvious decisions, migration notes, and how the change was tested. Omit the body only for a trivial change, such as a typo fix.

- Title: imperative, lowercase description, no period, 72 characters or fewer.
- Body: one blank line after the title. Wrap at 72 characters. Short paragraphs or `-` lists.

## Writing

Write the title and body in Simplified Technical English as described in [ste.md](ste.md). Keep the message concise and easy to read: short sentences, one idea per sentence, active voice, and concrete nouns such as the file, function, or command. Do not change identifiers, commands, or paths.

## Example

```text
fix(auth): refresh the token before it expires

The client refreshed the token only after a 401 response. Each
expired request failed once and then retried.

- Refresh the token 60 seconds before `expiresAt`.
- Add tests for the refresh timer and the retry path.

Refs: #123
```
