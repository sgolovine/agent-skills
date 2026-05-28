# Agent Skills

A collection of my agent skills.

## Layout

- `skills/` contains installable skill folders.
- `scripts/` contains project utilities.

## Install Skills

Run the TypeScript installer:

```sh
npm run install:skills
```

The installer uses `@clack/prompts` to choose a global Codex skills folder or a project folder, then installs selected skills as symlinks.

Run the TypeScript check with:

```sh
npm test
```
