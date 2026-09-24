---
name: clean-code
description: Write small, direct, maintainable source code by resisting over-engineering. Use when writing, modifying, or reviewing code where the solution should stay simple, avoid speculative abstractions, and defer future-only capabilities.
---

# Clean Code

## Operating Principle

Solve the requirement that exists now with code that is easy to read, test, change, and delete. Treat abstraction as a cost until today's code proves otherwise.

## Workflow

For review-only requests, report concrete complexity costs and suggested simplifications with evidence. Do not edit unless requested.

1. Identify the needed behavior, the smallest observable result that satisfies it, and the existing path that should own it.
2. Prefer fewer concepts, less coupling, and fewer dependencies, configuration knobs, and public APIs. Use file boundaries that improve cohesion or navigation; file count is secondary.
3. Implement in local style with ordinary control flow, existing helpers, and narrow changes.
4. Refactor within the affected behavior after it works. Share code when instances represent the same rule and should change together; keep similar code separate when its responsibilities evolve independently.
5. Remove unused hooks, options, exports, and other dead code only after checking relevant consumers and compatibility obligations. Missing local callers alone do not establish that something is unused. Keep cleanup, including removal of obvious comments, within the affected behavior.
6. Verify with focused tests or checks, including failure behavior when relevant.

## Abstraction Gate

Add an abstraction, dependency, cache, queue, background job, generic option, or plugin point only when a concrete benefit justifies its maintenance cost. Prefer inline code or existing helpers when they are equally clear and meet the requirement.

Valid reasons include an explicit user requirement, simpler current code, protection of a domain invariant or an irreversible data or API boundary, a security or reliability requirement, or a measured performance limit. Use the smallest structure that meets the need.

Multiple callers are supporting evidence, not a prerequisite. A single caller can justify structure that protects an invariant or clarifies complex logic. Defer capabilities supported only by speculative future needs.

## Before Finishing

Review the diff for speculative structure. Explain a simplicity tradeoff in the final response only when it creates a meaningful limitation, maintenance cost, or deferred requirement.
