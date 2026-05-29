# Agent Skills

Install the skills in this repo with:

```sh
npm run install:skills
```

A collection of reusable Codex CLI skills.

## Available Skills

| Skill | Description |
| --- | --- |
| `conversation-to-skill` | Create a Codex CLI skill from an existing conversation or thread. Use when the user asks to turn a completed discussion, workflow, debugging session, prompt, procedure, or discovered domain knowledge into an installable skill, especially when the result must be created through subagent drafting, validation, and overprompting reduction. |
| `create-commit` | Create intentional Git commits from local changes using the Conventional Commits 1.0.0 format. Use when the user asks Codex to commit work, make a git commit, stage changes, prepare a commit message, split local changes into commits, or ensure commit messages follow Conventional Commits. |
| `reduce-overprompting` | Evaluate and rewrite Codex skills for cognitive load, signal-to-noise ratio, and overprompting. Use when reviewing a SKILL.md file, skill folder, prompt pack, agent instruction set, or bundled workflow to decide whether it preserves useful degrees of freedom, overloads the agent with incidental constraints, or needs a tighter rewrite. |

## Layout

- `skills/` contains installable skill folders.
- `scripts/` contains project utilities.

## Checks

Run the TypeScript check with:

```sh
npm test
```
