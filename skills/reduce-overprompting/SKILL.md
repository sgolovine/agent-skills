---
name: reduce-overprompting
description: Evaluate and rewrite Codex skills for cognitive load, signal-to-noise ratio, and overprompting. Use when reviewing a SKILL.md file, skill folder, prompt pack, agent instruction set, or bundled workflow to decide whether it preserves useful degrees of freedom, overloads the agent with incidental constraints, or needs a tighter rewrite.
---

# Reduce Overprompting

## Operating Principle

Treat the model as already capable. Preserve high-level intent, domain facts, brittle constraints, tool requirements, and validation steps; remove incidental detail that makes the agent spend attention on obeying prose instead of solving the task.

Use more detail for execution tickets, fragile tool procedures, schemas, and irreversible operations. Use less detail for planning, creative judgment, code design, and decisions where multiple good approaches exist.

## Workflow

1. Read the target skill's `SKILL.md`; inspect referenced scripts, references, or assets only when needed to judge whether content belongs in the body or should move behind progressive disclosure.
2. Identify the skill's job, intended trigger, main user requests, and task phase:
   - `plan`: needs exploration, judgment, prioritization, or synthesis.
   - `execute`: needs exact steps, brittle APIs, formats, validation, or repeatable operations.
   - `mixed`: should separate planning guidance from execution guardrails.
3. Audit cognitive load and signal using the rubric below.
4. Rewrite the skill, keeping its useful capabilities intact while reducing avoidable instruction mass.
5. Report the diagnosis, the main cuts or moves, and any remaining risks.

## Audit Rubric

Score each area from `0` to `3`.

| Score | Meaning |
| --- | --- |
| `0` | Healthy; no meaningful issue. |
| `1` | Mild friction; worth improving if editing anyway. |
| `2` | Clear drag on agent performance or context efficiency. |
| `3` | Severe overprompting; likely to steer agents away from good work. |

### Cognitive Load

Look for:
- Long lists of rules with similar intent.
- Repeated warnings, restated principles, or obvious advice.
- Instructions that require the agent to track many local exceptions.
- Large examples embedded in `SKILL.md` when a short pattern or reference file would work.
- Unprioritized requirements where critical constraints and nice-to-haves look equally important.

### Signal-To-Noise Ratio

Look for:
- Generic guidance the base agent already knows.
- Process narration that does not change behavior.
- Trigger information hidden in the body instead of the YAML description.
- Detailed implementation preferences without a reason tied to fragility, consistency, or domain truth.
- Content duplicated across frontmatter, body, references, and scripts.

### Degree-Of-Freedom Fit

Look for:
- Planning instructions that over-specify how to think, structure, or decide.
- Creative or design tasks boxed in by arbitrary constraints.
- Execution tasks that are under-specified despite brittle tools or formats.
- Mixed skills that fail to separate open-ended planning from precise execution steps.

### Progressive Disclosure

Look for:
- `SKILL.md` longer than needed for first-pass behavior.
- Reference material loaded into the body even though it is only conditionally useful.
- Scripts described in detail when the skill can simply name when to run them.
- Missing navigation cues for references that should be loaded only on demand.

## Rewrite Rules

Apply these transformations:

- Make the YAML description do the triggering work: what the skill does, when to use it, and the relevant artifact types.
- Start with one short operating principle and a direct workflow.
- Keep only behavior-changing instructions in `SKILL.md`.
- Convert repeated rules into one stronger rule.
- Replace prescriptive planning steps with goal, intent, constraints, and quality bar.
- Keep exact procedures only where brittleness justifies them.
- Move rare details, long examples, policy tables, schemas, and variant-specific guidance into `references/`.
- Prefer compact checklists over prose when the agent must verify completion.
- Delete meta-commentary about why skills matter unless it changes the current task.

Preserve:
- Required tools and command sequences.
- Safety constraints, approval boundaries, and irreversible-operation warnings.
- Domain vocabulary, schemas, file formats, and API quirks.
- Validation commands and expected artifacts.
- User-facing behavior that the skill explicitly promises.

## Output Format

When auditing only, return:

```markdown
**Diagnosis**
- Cognitive load: N/3 - brief reason
- Signal-to-noise: N/3 - brief reason
- Degree-of-freedom fit: N/3 - brief reason
- Progressive disclosure: N/3 - brief reason

**Highest-Value Fixes**
- ...
```

When rewriting, edit the skill files directly when possible, then summarize:

```markdown
**Diagnosis**
- ...

**Changed**
- ...

**Residual Risk**
- ...
```

If editing is not possible, provide a replacement `SKILL.md` and name any references or scripts that should be added, moved, or deleted.
