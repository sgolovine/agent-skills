---
name: conversation-to-skill
description: Create a Codex CLI skill from an existing conversation or thread. Use when the user asks to turn a completed discussion, workflow, debugging session, prompt, procedure, or discovered domain knowledge into an installable skill, especially when the result must be created through subagent drafting, validation, and overprompting reduction.
---

# Conversation To Skill

## Operating Principle

Convert the conversation into a reusable Codex CLI skill, but create no skill files until the user explicitly states the destination directory.

## Workflow

1. Confirm the save location.
   - Ask and stop if the destination directory is missing or ambiguous, including when the user provides only a skill name.
   - Never default to the current repo, `$CODEX_HOME/skills`, or `~/.codex/skills`.
2. Summarize the source conversation before delegating. Capture:
   - the intended skill job and likely triggers,
   - concrete user requests or examples that should activate the skill,
   - decisions, constraints, brittle procedures, required tools, and validation steps,
   - unresolved questions or low-confidence details,
   - the explicit save location and any requested skill name.
3. Spawn a creator subagent. Pass the full available conversation when possible, or a complete summary plus necessary raw excerpts when the full conversation is too large. Include the explicit save location and this instruction:

```text
Use the skill-creator skill at /home/sgolovine/.codex/skills/.system/skill-creator/SKILL.md to create a Codex CLI skill from the provided conversation. Create or edit the skill directly at the explicit save location. Keep SKILL.md concise, use valid name/description frontmatter, and include only resources that are genuinely reusable.
```

4. Review the created skill path and basic structure. If the creator subagent reports uncertainty that blocks correctness, ask the user the needed clarification before continuing.
5. Spawn a validation subagent. Pass the created skill path and the source conversation summary, not the creator subagent's reasoning, and instruct it to:
   - validate the skill against the conversation,
   - identify inconsistencies, missing requirements, unclear triggers, brittle assumptions, and low-confidence areas,
   - return concrete fixes and any clarifying questions that must go to the user.
6. Resolve validation findings.
   - If validation finds issues that cannot be resolved from the conversation, ask the user and apply the answers before continuing.
   - Route revisions back through the creator subagent when possible; make only small mechanical edits directly.
   - Repeat validation until there are no blocking inconsistencies, gaps, or low-confidence areas.
7. Spawn an overprompting-review subagent. Pass the validated skill path and instruct it:

```text
Use the reduce-overprompting skill at /home/sgolovine/Projects/agent-skills/skills/reduce-overprompting/SKILL.md to audit and, if useful, rewrite the validated skill. Preserve required behavior, especially the explicit save-location gate, subagent drafting, validation, user clarification, and final validation requirements. Report whether you changed the skill or left it as-is.
```

8. Run final validation for the skill format. Use the local validation command required by the skill-creator workflow when available:

```sh
python3 /home/sgolovine/.codex/skills/.system/skill-creator/scripts/quick_validate.py <path-to-skill-folder>
```

9. Report the final skill path, subagent passes performed, validation result, and any remaining risks or user follow-ups.
