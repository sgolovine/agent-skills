# Planning Worker Contracts

## Specification Writer

**Goal:** Convert all confirmed grill documents into one complete specification.

**Inputs:** All grill documents, repository evidence, and the confirmed shared understanding.

**Write scope:** `<run-path>/SPEC.md` only.

**Actions:**

1. Give each requirement a stable `REQ-NNN` identifier.
2. Define the outcome, scope, exclusions, constraints, behavior, interfaces, and acceptance evidence.
3. Include quality, migration, security, compatibility, and rollout requirements when applicable.
4. Keep the specification testable.
5. Resolve each question before completion.

**Stop rules:**

- Report a conflict when the confirmed documents cannot resolve it.
- Do not invent a requirement.

## Block Planner

**Goal:** Divide the specification into small sequential pull request blocks.

**Inputs:** `SPEC.md`, repository evidence, and branch constraints.

**Write scope:** Files under `<run-path>/blocks/` only.

**Actions:**

1. Create one `NN-short-description.md` file for each block.
2. Keep each block small enough for a direct human review.
3. Base each later block on all previous blocks.
4. Map each block to its applicable `REQ-NNN` identifiers.
5. Give each block the sections in the template below.

```md
# <Block number>: <Short description>

## Objective

## Parent

## Requirement Coverage

## In Scope

## Out of Scope

## Implementation Requirements

## Validation

## Completion Criteria
```

**Stop rules:**

- Do not omit a requirement.
- Do not add behavior outside `SPEC.md`.

## Coverage Auditor

**Goal:** Confirm complete and conflict-free coverage of `SPEC.md`.

**Inputs:** `SPEC.md` and all block files.

**Write scope:** One report under `<run-path>/coverage/`.

**Actions:**

1. Keep the repository unchanged.
2. Keep the block files unchanged.
3. Map every `REQ-NNN` identifier to one or more block sections.
4. Check the block order and parent dependencies.
5. Check for omitted work, duplicate ownership, gaps, and conflicts.
6. Mark the result `pass` only when coverage equals 100 percent.
7. Give each finding its requirement, block, evidence, and required correction.

**Stop rule:** Do not pass a requirement that has only an implied implementation.

## Block Reviser

**Goal:** Correct all findings from one coverage report.

**Inputs:** `SPEC.md`, all blocks, and the coverage report.

**Write scope:** Affected files under `<run-path>/blocks/` only.

**Actions:**

1. Correct each reported gap or conflict directly.
2. Preserve small block size.
3. Preserve sequential dependencies.
4. Keep requirement mappings explicit.
5. Report each changed block and correction.

**Stop rules:**

- Do not change `SPEC.md`.
- Report a specification conflict to the Supervisor.
