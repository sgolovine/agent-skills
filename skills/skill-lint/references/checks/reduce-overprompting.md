# Reduce Overprompting Check

## Purpose

Evaluate and fix Codex CLI skills for cognitive load, signal-to-noise ratio, degree-of-freedom fit, and progressive disclosure.

## Report Workflow

1. Read the target `SKILL.md`.
2. Inspect referenced scripts, references, or assets only when needed to judge whether material belongs in the main skill body or behind progressive disclosure.
3. Identify the skill's job, intended trigger, common user requests, and task phase:
   - `plan`: exploration, judgment, prioritization, or synthesis.
   - `execute`: exact steps, brittle APIs, formats, validation, or repeatable operations.
   - `mixed`: planning guidance plus execution guardrails.
4. Score each rubric area from `0` to `3`.
5. Report the highest-value fixes with evidence and concrete recommendations.

## Rubric

| Score | Meaning |
| --- | --- |
| `0` | Healthy; no meaningful issue. |
| `1` | Mild friction; worth improving if editing anyway. |
| `2` | Clear drag on agent performance or context efficiency. |
| `3` | Severe overprompting; likely to steer agents away from good work. |

### Cognitive Load

Look for long lists with similar intent, repeated warnings, obvious advice, many local exceptions, embedded large examples, and unprioritized requirements where critical constraints and nice-to-haves look equal.

### Signal-To-Noise Ratio

Look for generic guidance the base agent already knows, process narration that does not change behavior, trigger information hidden outside YAML, unjustified implementation preferences, and duplicated content across body, references, and scripts.

### Degree-Of-Freedom Fit

Look for planning instructions that over-specify thinking, creative tasks boxed in by arbitrary constraints, execution tasks that are under-specified despite brittle tooling, and mixed skills that do not separate judgment from exact procedures.

### Progressive Disclosure

Look for a `SKILL.md` longer than needed for first-pass behavior, conditional material loaded into the body, scripts described instead of named, and missing navigation cues for references.

## Fix Rules

Apply these transformations when they directly address reported findings:

- Make the YAML description do the triggering work.
- Start with one short operating principle and a direct workflow.
- Keep only behavior-changing instructions in `SKILL.md`.
- Convert repeated rules into one stronger rule.
- Replace prescriptive planning steps with goals, constraints, and quality bars.
- Keep exact procedures only where brittleness justifies them.
- Move rare details, long examples, policy tables, schemas, and variant-specific guidance into `references/`.
- Prefer compact checklists over prose when the agent must verify completion.
- Delete meta-commentary unless it changes the current task.

Preserve:

- Required tools and command sequences.
- Safety constraints, approval boundaries, and irreversible-operation warnings.
- Domain vocabulary, schemas, file formats, and API quirks.
- Validation commands and expected artifacts.
- User-facing behavior the skill explicitly promises.

## Clarification Triggers In Fix Mode

Ask before fixing when below `90%` confidence about:

- Whether a long section is domain-critical or can move behind progressive disclosure.
- Whether an apparent rule is a hard safety constraint or stylistic preference.
- Whether to preserve examples verbatim, summarize them, or move them.
- Whether removing a constraint would change promised user-facing behavior.

Each question must include the best attempted answer and plausible responses.

## Output Details

For check-local report findings, include:

```markdown
- [reduce-overprompting][severity] Finding title
  - Score: category N/3
  - File: path
  - Evidence: concise snippet or behavior
  - Why it matters: cognitive or operational impact
  - Recommended fix: concrete edit
```

Use severity mapping: `low` for score `1`, `medium` for score `2`, `high` for score `3`.

## Validation

After fixes, verify:

- The rewritten skill still covers its core trigger and promised behavior.
- Behavior-changing safety constraints and brittle procedures remain.
- Large or conditional material is behind progressive disclosure.
- The main `SKILL.md` is shorter or materially clearer unless the issue required adding precision.
