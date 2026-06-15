---
name: clean-code
description: Write small, direct, maintainable source code by resisting over-engineering. Use when writing, modifying, or reviewing code where the solution should stay simple, avoid speculative abstractions, and defer future-only capabilities.
---

# Clean Code

## Operating Principle

Solve the requirement that exists now with code that is easy to read, test, change, and delete. Treat abstraction as a cost until today's code proves otherwise.

## Workflow

1. Identify the needed behavior, the smallest observable result that satisfies it, and the existing path that should own it.
2. Choose the approach with the least new surface area: fewer concepts, files, dependencies, configuration knobs, and public APIs.
3. Implement in local style with ordinary control flow, existing helpers, and narrow changes. Add structure only when it reduces current complexity or protects a real boundary or invariant.
4. Refactor after the behavior works: remove real duplication, unused hooks, speculative options, dead exports, and comments that explain obvious code.
5. Verify with focused tests or checks, including failure behavior when relevant.

## Abstraction Gate

Before adding an abstraction, dependency, cache, queue, background job, generic option, plugin point, or new file, ask:

- Is there more than one real caller, implementation, or variant today?
- Does the current requirement or a representative test use it?
- Would inline code or an existing helper be harder to understand or change?
- Is the future need certain, expensive to add later, and cheap to carry now?

Only keep the extra structure when current use is real, the simpler local form is worse, and the carrying cost is justified.

## When More Design Is Justified

Use the smallest necessary structure when the user explicitly requests it, it simplifies current code, it protects a domain invariant, it handles an irreversible data or API boundary, it satisfies a security or reliability requirement, or measurement shows a performance limit.

## Before Finishing

Review the diff for speculative structure. In the final response, mention any intentional simplicity tradeoff when a heavier design was plausible.
