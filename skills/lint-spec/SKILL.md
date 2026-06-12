---
name: lint-spec
description: Scrutinize specification files for low-confidence, ambiguous, unclear, missing, or implicit requirements. Use when the user asks to lint, clarify, harden, or iterate on a spec and wants questions with confidence scores, proposed solutions, recommended choices, and disk updates after each clarification.
---

# Lint Spec

## Operating Principle

Treat a spec as unfinished until every material requirement is explicit or accepted by the user.

## Workflow

1. Require a spec file path before linting. If the user provides pasted spec text without a path, ask for the path and do not proceed in chat-only mode.
2. Read the spec file and identify material areas that are low-confidence, ambiguous, unclear, underspecified, internally inconsistent, or dependent on unstated assumptions.
3. Assign each area a confidence score from `0%` to `100%`, where the score means confidence that the current spec is clear and actionable for that area.
4. Ask questions for every area below `100%`. For each question:
   - name the affected spec area,
   - state the current confidence score,
   - explain the uncertainty briefly,
   - provide `2-4` proposed solutions,
   - mark one solution as `Recommended` based on the user's apparent intent.
5. When the user answers, update the working understanding and patch the spec file on disk before asking more questions. Rewrite the affected section for maximum clarity while keeping the edit targeted and preserving unrelated content.
6. After each clarification update, print only the next unresolved questions unless the user asks to see the updated spec, diff, or change summary.
7. Stop when every material area is at `100%`. An area may reach `100%` when the spec already states it clearly, the user answers directly, or the user accepts a proposed solution.

## Validation

Before finishing, verify:

- the spec file on disk includes every accepted clarification,
- each material area is scored at `100%`,
- no unresolved ambiguity, missing requirement, conflict, or implicit assumption remains,
- the final response names the updated file and states that no further clarification questions remain.
