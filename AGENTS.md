# Repository Guidelines

## Project Shape

This repo stores reusable Codex CLI skills. Create and edit skills inside `skills/<skill-name>/`; keep repo utilities in `scripts/`.

Skill folders should be installable by `scripts/install-agent-skills.ts`, which discovers directories under `skills/` that contain `SKILL.md`.

## Skill Format

When a user asks to create a skill, assume they want a Codex CLI skill unless they specify another target. Codex CLI is the only supported harness format for new work. Do not add new harness-specific manifests or adapters for other agents unless the user explicitly asks to migrate legacy content.

Every skill must include `SKILL.md` with YAML frontmatter:

```markdown
---
name: skill-name
description: Short trigger-focused description of what the skill does and when to use it.
---
```

Use lowercase, hyphenated names for skill directories and `name` values. Keep the frontmatter description specific enough for trigger selection.

## Skill Authoring

Treat the model as capable. Preserve intent, domain facts, brittle procedures, required tools, safety constraints, and validation steps; cut generic coaching and repeated warnings.

Prefer this structure:

- One short operating principle.
- A direct workflow with only behavior-changing steps.
- Compact validation instructions.
- Conditional details in `references/`, reusable code in `scripts/`, and assets in `assets/`.

Move long examples, schemas, variant-specific instructions, and rarely used background out of `SKILL.md` so agents load them only when needed.

## Repository Workflows

- Use `rg` or `rg --files` first when inspecting files.
- Use `npm run tsc` to type-check TypeScript changes.
- Avoid editing installed `node_modules/` content.
- Keep unrelated local changes intact; do not clean up or revert work outside the task.

## Before Finishing

For skill changes, verify:

- The skill is under `skills/<skill-name>/`.
- `SKILL.md` has valid frontmatter with `name` and `description`.
- The skill targets Codex CLI behavior only.
- Large or conditional material is behind progressive disclosure.
- Any changed scripts or TypeScript pass the relevant local check.
