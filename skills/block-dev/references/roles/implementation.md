# Implementation Worker Contracts

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

**Stop rules:**

- Do not edit run artifacts.
- Do not perform a publication action from [open-github-pull-request.md](../open-github-pull-request.md).

## Standards Reviewer

**Goal:** Review one block diff against repository standards.

**Inputs:** The fixed point, review set, standards sources, and [code-review.md](../code-review.md).

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

**Inputs:** The fixed point, review set, block file, `SPEC.md`, and [code-review.md](../code-review.md).

**Write scope:** One block-plan report under the assigned review round.

**Actions:**

1. Keep repository files unchanged.
2. Apply the specification axis from `code-review.md`.
3. Report missing behavior.
4. Report incomplete behavior.
5. Report incorrect behavior.
6. Report unrequested behavior.
7. Quote the applicable block requirement for each finding.
8. Check mapped `REQ-NNN` requirements when more context is necessary.

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

**Stop rules:**

- Do not expand the block scope.
- Do not perform a publication action from [open-github-pull-request.md](../open-github-pull-request.md).
