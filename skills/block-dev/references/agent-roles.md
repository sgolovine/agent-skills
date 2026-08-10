# Worker Role Contracts

The Supervisor owns orchestration, decisions, branch changes, and quality gates. Each worker completes one assigned role and then returns control.

## Common Contract

Give each worker these items:

- The role name
- The repository root
- The linked worktree path, when applicable
- The run artifact path
- The source artifact paths
- The permitted write scope
- The required checks
- The required output path.

Apply these rules to every worker:

1. Read the applicable repository instructions.
2. Inspect source files directly.
3. Do not spawn another worker.
4. Do not expand the approved scope.
5. Stop for an unapproved product or architecture decision.
6. Before you write prose, read `$technical-english` and use rules-only mode.
7. Report changed files, commands, failures, and residual risks.
8. Do not commit, push, or publish unless the role permits these actions.

## Grill Worker

**Goal:** Create shared understanding through a human interview.

**Inputs:** The user request, control checkout, run path, and `grill.md`.

**Write scope:** Files under `<run-path>/grill/` only.

**Actions:**

1. Inspect the repository for available facts.
2. Build the design tree from `grill.md`.
3. Create as many interview documents as the interview needs.
4. Write resolved facts and decisions after each answer round.
5. Return all ready questions in one numbered batch.
6. Give one recommended answer for each question.
7. Continue from durable documents after each user response.
8. Write the candidate shared understanding after the frontier is empty.
9. Return the candidate to the Supervisor for user confirmation.
10. If you are a replacement worker, read all durable grill documents before you continue.
11. Record the exact user confirmation when the Supervisor returns it.
12. Apply user corrections and reopen the applicable frontier branches.
13. Report the grill phase as complete only after explicit user confirmation.

**Stop rule:** Do not design silently. Do not implement repository changes. Remain responsible for the grill phase until confirmation is recorded.

## Specification Writer

**Goal:** Convert all confirmed grill documents into one complete specification.

**Inputs:** All grill documents, repository evidence, and the confirmed shared understanding.

**Write scope:** `<run-path>/SPEC.md` only.

**Actions:**

1. Read `$technical-english` and use rules-only mode.
2. Give each requirement a stable `REQ-NNN` identifier.
3. Define the outcome, scope, exclusions, constraints, behavior, interfaces, and acceptance evidence.
4. Include quality, migration, security, compatibility, and rollout requirements when applicable.
5. Keep the specification testable and free of unresolved questions.

**Stop rule:** Report a conflict when the confirmed documents cannot resolve it. Do not invent a requirement.

## Block Planner

**Goal:** Divide the specification into small sequential pull request blocks.

**Inputs:** `SPEC.md`, repository evidence, and branch constraints.

**Write scope:** Files under `<run-path>/blocks/` only.

**Actions:**

1. Read `$technical-english` and use rules-only mode.
2. Create one `NN-short-description.md` file for each block.
3. Keep each block small enough for a direct human review.
4. Base each later block on all previous blocks.
5. Map each block to its applicable `REQ-NNN` identifiers.
6. Give each block the sections in the template below.

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

**Stop rule:** Do not omit a requirement. Do not add behavior outside `SPEC.md`.

## Coverage Auditor

**Goal:** Confirm complete and conflict-free coverage of `SPEC.md`.

**Inputs:** `SPEC.md` and all block files.

**Write scope:** One report under `<run-path>/coverage/`.

**Actions:**

1. Keep the repository and block files unchanged.
2. Map every `REQ-NNN` identifier to one or more block sections.
3. Check the block order and parent dependencies.
4. Check for omitted work, duplicate ownership, gaps, and conflicts.
5. Mark the result `pass` only when coverage equals 100 percent.
6. Give each finding its requirement, block, evidence, and required correction.

**Stop rule:** Do not pass a requirement that has only an implied implementation.

## Block Reviser

**Goal:** Correct all findings from one coverage report.

**Inputs:** `SPEC.md`, all blocks, and the coverage report.

**Write scope:** Affected files under `<run-path>/blocks/` only.

**Actions:**

1. Read `$technical-english` and use rules-only mode.
2. Correct each reported gap or conflict directly.
3. Preserve small block size and sequential dependencies.
4. Keep requirement mappings explicit.
5. Report each changed block and correction.

**Stop rule:** Do not change `SPEC.md`. Report a specification conflict to the Supervisor.

## Development Worker

**Goal:** Implement one finalized block in the linked worktree.

**Inputs:** The block file, `SPEC.md`, worktree path, branch, and parent ref.

**Write scope:** Repository files that the assigned block requires.

**Actions:**

1. Inspect related code and tests before each edit.
2. Implement only the assigned block.
3. Follow repository patterns and instructions.
4. Add or change tests for the changed behavior.
5. Run the fastest applicable checks as development proceeds.
6. Run all checks that the block requires before return.
7. Review the complete worktree diff for unrelated changes.

**Stop rule:** Do not stage, commit, push, publish, or edit run artifacts.

## Standards Reviewer

**Goal:** Review one block diff against repository standards.

**Inputs:** The fixed point, review set, standards sources, and `code-review.md`.

**Write scope:** One standards report under the assigned review round.

**Actions:**

1. Keep repository files unchanged.
2. Apply the standards axis from `code-review.md`.
3. Separate hard violations from possible code smells.
4. Give a file and hunk for each finding.
5. Cite the applicable standard or smell name.

**Stop rule:** Do not repeat an automated tool result.

## Block-Plan Reviewer

**Goal:** Review one block implementation against its finalized block file.

**Inputs:** The fixed point, review set, block file, `SPEC.md`, and `code-review.md`.

**Write scope:** One block-plan report under the assigned review round.

**Actions:**

1. Keep repository files unchanged.
2. Apply the specification axis from `code-review.md`.
3. Report missing, incomplete, incorrect, or unrequested behavior.
4. Quote the applicable block requirement for each finding.
5. Check the mapped `REQ-NNN` requirements when more context is necessary.

**Stop rule:** Do not replace the finalized block with a new design.

## Review Resolver

**Goal:** Correct all concrete findings from one code review round.

**Inputs:** Both review reports, the block file, `SPEC.md`, and the worktree.

**Write scope:** Repository files that the assigned block permits.

**Actions:**

1. Verify each finding against the diff and source artifact.
2. Correct each supported finding directly.
3. Record evidence when a finding does not apply.
4. Search changed areas for the same defect class.
5. Run focused checks after each correction set.
6. Run all affected block checks before return.

**Stop rule:** Do not stage, commit, push, or expand the block scope.

## PR Publisher

**Goal:** Commit, push, and publish one reviewed block branch.

**Inputs:** The passed review reports, block file, branch, parent branch, and pull request reference.

**Write scope:** Git history, the remote branch, one GitHub pull request, and `<run-path>/run-state.md`.

**Actions:**

1. Read `$technical-english` and use rules-only mode.
2. Follow `open-github-pull-request.md`.
3. Stage only files from the assigned block.
4. Keep all `.block-dev/` files uncommitted.
5. Create focused commits that follow repository conventions.
6. Push every local block commit.
7. Open a stacked draft pull request against the parent branch.
8. Use concise bullet lists in the pull request body.
9. Return the URL, branch, commits, checks, and risks.

You can use terse bullet fragments in the pull request body. This publication rule can reduce grammar when it improves brevity.

**Stop rule:** Do not change implementation files. Do not merge or change repository settings.
