---
name: ask-me-questions
description: Ask targeted clarification questions before acting on a provided request. Use when the user invokes this skill with instructions and wants uncertainties, missing details, ambiguities, or conflicts surfaced whenever they cannot be resolved with at least 90% confidence.
---

# Ask Me Questions

## Operating Principle

Treat uncertainty as an explicit gate: proceed only when each material question can be answered or safely resolved with at least 90% confidence.

## Workflow

1. If the skill is invoked without a concrete request or instructions, stop and reply exactly:

```text
this skill must be passed with instructions
```

2. Read the provided request and identify the material questions needed to understand or complete it. Include:
   - questions that arise while interpreting the user's intent,
   - missing information, gaps, ambiguities, and conflicts,
   - assumptions that would affect output, scope, safety, cost, timing, or implementation choices.
3. For each material question, estimate a confidence score from `0%` to `100%` for the best available answer from context.
4. If confidence is at least `90%`, proceed using the inferred answer without asking the user.
5. If confidence is below `90%`, ask the user before continuing. For each clarification:
   - state the question concisely,
   - provide your best attempted answer or default assumption,
   - give a short list of plausible responses the user can choose from or adapt.
6. Do not expose private chain-of-thought. Convert internal uncertainty into concise, actionable clarification questions.
7. After the user answers, continue the original request using the clarified information.

## Validation

Before acting, verify that every unresolved gap, ambiguity, or conflict either has at least `90%` confidence or has been sent to the user as a clarification question with a best attempted answer and possible responses.
