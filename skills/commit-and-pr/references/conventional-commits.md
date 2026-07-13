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

- Start with a type, optional scope, optional `!`, then `: ` and a description.
- Use `feat` for a new feature and `fix` for a bug fix. Other types are allowed.
- Put a body one blank line after the description.
- Put footers one blank line after the body. Footer tokens use `-` instead of whitespace, except `BREAKING CHANGE`.
- Indicate a breaking change with `!` before the colon or an uppercase `BREAKING CHANGE:` footer.

## Footer Pattern

```text
Reviewed-by: Z
Refs: #123
BREAKING CHANGE: describe the incompatible change
```
