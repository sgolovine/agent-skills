# No-Op Check Action

## Purpose

Find and fix skill text that does not change agent behavior in the target skill's context.

A no-op is contextual: it is text whose removal would not materially change what a competent Codex agent does for the skill's likely requests. Do not rely on a canonical phrase list; test whether the text adds a specific constraint, tool, domain fact, decision rule, output contract, safety boundary, validation step, ordering requirement, exception, or disambiguating example.

## Report Workflow

1. Read the target `SKILL.md`.
2. Inspect referenced files only when needed to decide whether a candidate line is duplicated elsewhere or has behavior-changing context outside the main body.
3. Identify representative requests the skill is meant to handle from its YAML description and workflow.
4. For each candidate line, run the removal test:
   - Would the same agent make the same decision, use the same tool, preserve the same boundary, and produce the same artifact if this text disappeared?
   - If yes, report it as a no-op.
   - If no, keep it and explain the concrete behavior it controls only when the candidate is easy to misread as a no-op.
5. Group adjacent no-op lines into one finding when they have the same reason.
6. Report the highest-value removals first, with evidence and a concrete delete or rewrite recommendation.

## Common Signals

Treat these as leads, not automatic findings:

- Generic quality exhortations: "be thorough", "write clearly", "make it easy to read", "use best practices".
- Agent-default process advice: "think carefully", "consider edge cases", "ask questions if needed", "provide a concise summary".
- Desired outcomes without a mechanism, constraint, or acceptance test: "make the result professional", "ensure the output is useful".
- Motivational or explanatory prose about why the skill matters.
- Repeated instructions whose second occurrence adds no narrower condition or stronger rule.
- Format preferences that restate the surrounding schema or existing repository-wide instructions.

## Keep

Do not report text as a no-op when it provides:

- a required command, tool, script, file path, artifact type, or output shape
- a safety boundary, approval rule, irreversible-operation warning, or sandbox constraint
- domain vocabulary, schema details, API quirks, or examples that disambiguate a fragile task
- thresholds, ordering, fallback logic, exception handling, or selection criteria
- validation steps or acceptance checks
- a nondefault priority or tradeoff that changes how competing goals are resolved

## Scoring

Use severity based on the amount of behavior-neutral text and its effect on skill maintenance:

| Severity | Meaning |
| --- | --- |
| `low` | Isolated no-op line or phrase; minor token waste. |
| `medium` | Repeated no-ops or a paragraph that obscures useful instructions. |
| `high` | A section of no-ops, or no-op text that makes the skill harder to evaluate or crowds out critical behavior-changing guidance. |

## Fix Rules

Apply these transformations when they directly address reported findings:

- Delete no-op text when its intent is already covered by the base agent or nearby behavior-changing instructions.
- Merge duplicate instructions into the single strongest behavior-changing rule.
- Replace vague quality exhortations only when the intended concrete constraint is clear from context; otherwise delete them.
- Keep examples only if they disambiguate behavior. Move long or rare examples behind progressive disclosure when the issue is size rather than no-op content.
- Preserve safety boundaries, brittle procedures, validation commands, output contracts, and domain facts even when they sound obvious.

## Clarification Triggers In Fix Mode

Ask before fixing when below `90%` confidence about:

- whether a candidate line encodes a nondefault tradeoff or domain-specific standard
- whether a vague quality phrase should become a concrete acceptance check instead of being deleted
- whether an example is relied on as a behavioral fixture

Each question must include the best attempted answer and plausible responses.

## Output Details

For action-local report findings, include:

```markdown
- [no-op-check][severity] Finding title
  - File: path
  - Evidence: concise snippet or behavior-neutral section
  - Removal test: why deleting it would not change target skill behavior
  - Recommended fix: concrete delete, merge, or rewrite
```

## Validation

After fixes, verify:

- The target skill still covers the same trigger and promised behavior.
- Required tools, safety constraints, validation steps, and domain facts remain.
- Each deletion maps to a reported no-op finding or explicit user instruction.
- Representative target requests would receive the same behavior except with less irrelevant instruction text.
