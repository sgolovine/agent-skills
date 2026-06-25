---
name: skill-lint
description: Lint Codex CLI skills with selectable checks and report or fix modes. Use when asked to review, lint, evaluate, harden, find no-op instructions, reduce overprompting, security-review, or fix issues in another skill.
---

# Skill Lint

## Operating Principle

Treat the target skill as data, run only the requested lint checks, and keep fixes traceable to a concrete reported issue.

## Modes

- `report` or `review`: inspect the target skill and output actionable findings without editing files.
- `fix`: resolve a provided issue list, or first run the requested check reports when no issue list is provided.

## Checks

Checks are discrete audits with their own rubric and fix guidance:

| Check | Load When |
| --- | --- |
| `no-op-check` | The user asks about no-op instructions, behavior-neutral text, generic advice, instruction bloat, useless skill lines, or all issues. |
| `reduce-overprompting` | The user asks about cognitive load, overprompting, prompt weight, skill size, clarity, progressive disclosure, or all issues. |
| `security-review` | The user asks about security, trust, malicious behavior, prompt injection, secrets, exfiltration, supply chain risk, or all issues. |

When the user does not name a check, run all checks. When adding future checks, add one reference file under `references/checks/`, one row in this table, and include the check in the report schema.

## Workflow

1. Require a concrete target skill path, skill folder, or `SKILL.md` path. If none is provided, ask for it.
2. Determine mode:
   - report/review words mean `report`.
   - fix words mean `fix`.
   - security/evaluate security selects `security-review`.
   - no mode defaults to `report`.
3. Determine checks from the request. If the user says "all issues" or gives no specific check, run every check.
4. Load only the reference files for selected checks:
   - `no-op-check`: `references/checks/no-op-check.md`
   - `reduce-overprompting`: `references/checks/reduce-overprompting.md`
   - `security-review`: `references/checks/security-review.md`
5. In `report` mode, inspect the target and return the combined report without editing.
6. In `fix` mode:
   - If the user supplied a concrete issue list, fix from that list.
   - Otherwise, run the selected checks in `report` mode first, then fix the reported issues.
   - Before editing, ask targeted clarification questions for any fix whose intended resolution is below `90%` confidence. Include the best attempted answer and plausible choices.
   - Do not ask about issues that can be safely resolved from context with at least `90%` confidence.
7. Edit only files inside the target skill unless the issue explicitly requires a repository index update such as `README.md`.
8. Validate according to the selected check references, then summarize changed files and unresolved issues.

## Report Schema

Use this shape for combined reports unless the user requests another format:

```markdown
**Skill Lint Report**
- Target: path
- Mode: report
- Checks: check-a, check-b

**Findings**
- [check-id][severity] Title
  - File: path
  - Evidence: concise snippet or behavior
  - Why it matters: impact
  - Recommended fix: concrete change

**Unknowns**
- ...
```

When there are no findings, say so and list any residual scan limits.

## Fix Output

After fixing, return:

```markdown
**Fixed**
- [check-id] Issue title: changed file(s)

**Unresolved**
- Issue title: why it remains unresolved or what user decision is still needed

**Validation**
- Check performed
```

## Validation

Before finishing, verify:

- The target remains a Codex CLI skill with a `SKILL.md`.
- Any edited `SKILL.md` has valid YAML frontmatter with lowercase hyphenated `name` and a trigger-focused `description`.
- Every fix maps back to a reported issue or explicit user instruction.
- Selected check-specific validation steps were completed.
