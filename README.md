# Agent Skills

A collection of my personal agent skills. Feel free to take these skills, use them, modify them and redistribute them as you wish.

## Installation

Install the skills in this repo with. This will create a symlink between the location of the agent skill in the repo and `~/.codex/skills/<SKILL>`:

```sh
npm run install:skills
```

## Available Skills

| Skill | Description |
| --- | --- |
| [`agent-skill-security-review`](skills/agent-skill-security-review/SKILL.md) | Run an adversarial security review of untrusted Codex CLI skills, agent skill folders, or downloaded skill repositories before installation or use, only when the user provides a concrete target path. Use when asked to inspect third-party skills for prompt injection, secret access, exfiltration, install-time execution, persistence, tool poisoning, dependency risk, sandbox escape, CI compromise, or other capability abuse. |
| [`ask-me-questions`](skills/ask-me-questions/SKILL.md) | Ask targeted clarification questions before acting on a provided request. Use when the user invokes this skill with instructions and wants uncertainties, missing details, ambiguities, or conflicts surfaced whenever they cannot be resolved with at least 90% confidence. |
| [`appimage-desktop-install`](skills/appimage-desktop-install/SKILL.md) | Install a Linux AppImage as a per-user desktop app from Downloads or another local path, including stable home placement, launcher entry, provided icon, optional terminal command, and required fixed flags such as --no-sandbox. |
| [`bqe-timesheet`](skills/bqe-timesheet/SKILL.md) | Fill, verify, save, and submit BQE Core weekly timesheets using the user's authenticated Chrome session. Use when the user asks for help with BQE Core, BQE time cards, weekly timecards, or gives project/task/hour instructions for BQE. |
| [`clean-code`](skills/clean-code/SKILL.md) | Write small, direct, maintainable source code by resisting over-engineering. Use when writing, modifying, or reviewing code where the solution should stay simple, avoid speculative abstractions, and defer future-only capabilities. |
| [`conversation-to-skill`](skills/conversation-to-skill/SKILL.md) | Create a Codex CLI skill from an existing conversation or thread. Use when the user asks to turn a completed discussion, workflow, debugging session, prompt, procedure, or discovered domain knowledge into an installable skill, especially when the result must be created through subagent drafting, validation, and overprompting reduction. |
| [`create-commit`](skills/create-commit/SKILL.md) | Create intentional Git commits from local changes using the Conventional Commits 1.0.0 format. Use when the user asks Codex to commit work, make a git commit, stage changes, prepare a commit message, split local changes into commits, or ensure commit messages follow Conventional Commits. |
| [`flight-research`](skills/flight-research/SKILL.md) | Run two-pass flight research with supervisor-managed subagents across flight search engines, non-ATPCO carrier sites, and direct carrier validation, aligned to user constraints and written to SQLite output. Use only when origin IATA code, destination IATA code, passenger count, departure date, and return date are provided; date mode may be relative or exact and defaults to relative. |
| [`lint-spec`](skills/lint-spec/SKILL.md) | Scrutinize specification files for low-confidence, ambiguous, unclear, missing, or implicit requirements. Use when the user asks to lint, clarify, harden, or iterate on a spec and wants questions with confidence scores, proposed solutions, recommended choices, and disk updates after each clarification. |
| [`reduce-overprompting`](skills/reduce-overprompting/SKILL.md) | Evaluate and rewrite Codex skills for cognitive load, signal-to-noise ratio, and overprompting. Use when reviewing a SKILL.md file, skill folder, prompt pack, agent instruction set, or bundled workflow to decide whether it preserves useful degrees of freedom, overloads the agent with incidental constraints, or needs a tighter rewrite. |
| [`skill-lint`](skills/skill-lint/SKILL.md) | Lint Codex CLI skills with selectable actions and report or fix modes. Use when asked to review, lint, evaluate, harden, find no-op instructions, reduce overprompting, security-review, or fix issues in another skill. |
| [`spec-to-plan`](skills/spec-to-plan/SKILL.md) | Convert a specification file into a step-by-step implementation plan for agents. Use when the user asks to create a plan, implementation plan, execution plan, or agent-ready plan from a spec path, with an optional custom output path. |

## Layout

- `skills/` contains installable skill folders.
- `scripts/` contains project utilities.

## Checks

Run the TypeScript check with:

```sh
npm test
```

## Contributing

This is as personal software and as such I am not accepting contributions at this time. 

## License

Public domain under [The Unlicense](LICENSE.md).
