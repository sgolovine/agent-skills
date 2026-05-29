# Conventional Commits 1.0.0 Reference

Source: https://www.conventionalcommits.org/en/v1.0.0/#specification

## Required Shape

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Breaking changes may also be marked in the header:

```text
<type>[optional scope]!: <description>
```

## Core Rules

- A commit must start with a type, optional scope, optional `!`, then `: ` and a description.
- `feat` must be used for a new feature.
- `fix` must be used for a bug fix.
- Other types are allowed, including `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `style`, and `chore`.
- A scope is optional and appears in parentheses after the type, such as `feat(parser):`.
- A body may appear after one blank line following the description.
- Footers may appear one blank line after the body. Footer tokens use `-` instead of whitespace, except `BREAKING CHANGE`.
- A breaking change must be indicated by `!` before the colon in the header or by a footer token `BREAKING CHANGE:` or `BREAKING-CHANGE:`.
- `BREAKING CHANGE` must be uppercase when used as a footer token.
- Conventional Commit units are not case-sensitive for implementors except `BREAKING CHANGE`.

## Footer Pattern

Footers follow a git-trailer-like pattern:

```text
Token: value
Token #value
BREAKING CHANGE: description
```

Examples:

```text
Reviewed-by: Z
Refs: #123
BREAKING CHANGE: environment variables now take precedence over config files
```
