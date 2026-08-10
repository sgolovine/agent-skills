# Review Code Against Standards and a Block Plan

Review one block on two separate axes:

- **Standards**: Check compliance with documented repository standards.
- **Specification**: Check compliance with the finalized block plan.

The Supervisor spawns both review workers in parallel. Keep the two reports separate.

## Pin the Fixed Point

Use the parent ref that the Supervisor assigns. Record its immutable commit before review.

Run these commands from the stack worktree:

```sh
git rev-parse <fixed-point>
git log <fixed-point>..HEAD --oneline
git diff <fixed-point>...HEAD
git diff <fixed-point>
git status --short
```

The three-dot diff shows committed branch changes from the merge base. The direct diff also shows tracked worktree changes against the fixed point.

Use `git status --short` to find new untracked task files. Inspect each untracked task file directly.

Before review:

1. Confirm that `git rev-parse <fixed-point>` succeeds.
2. Confirm that the current branch descends from the fixed point.
3. Record the commit list.
4. Build the review set from the direct diff and untracked task files.
5. Stop when the fixed point is invalid.
6. Stop when the complete review set is empty.

Do not include `.block-dev/` artifacts in the review set.

## Pin the Specification Source

Use the assigned `NN-short-description.md` block file as the specification source. Use `SPEC.md` only to clarify mapped `REQ-NNN` requirements.

Stop when the block file is missing or unreadable. Do not replace the block file with an issue or an inferred requirement.

## Find the Standards Sources

Find all repository files that define contributor requirements. These files can include:

- `CODING_STANDARDS.md`
- `CONTRIBUTING.md`
- Applicable agent instruction files
- Language or framework style guides in the repository.

Also apply the smell baseline below. The baseline contains heuristics from Martin Fowler's *Refactoring*, chapter 3.

Apply these rules:

- A documented repository standard overrides the smell baseline.
- Label each smell as a possible issue, not a hard violation.
- Do not report rules that automated tools already enforce.

Check the review set for these smells:

- **Mysterious Name**: A name does not show its purpose. Rename the item or examine the design.
- **Duplicated Code**: The same logic shape occurs in multiple changed locations. Extract shared logic.
- **Feature Envy**: A method uses another object more than its own object. Move the method to the data owner.
- **Data Clumps**: The same fields or parameters frequently occur together. Put them in one type.
- **Primitive Obsession**: A primitive represents a domain concept that needs a type. Create a small domain type.
- **Repeated Switches**: Repeated conditions select behavior for the same type. Use polymorphism or one shared map.
- **Shotgun Surgery**: One logical change needs edits in many separate files. Put related behavior in one module.
- **Divergent Change**: One module changes for unrelated reasons. Divide the separate responsibilities.
- **Speculative Generality**: The block adds abstractions or hooks that no requirement needs. Remove or inline them.
- **Message Chains**: A caller uses a long chain such as `a.b().c().d()`. Hide the navigation behind a method.
- **Middle Man**: A component primarily delegates to another component. Remove the component and call the target.
- **Refused Bequest**: A subtype ignores most inherited behavior. Replace inheritance with composition.

## Run Both Review Axes

### Standards Reviewer

Give the Standards Reviewer these items:

- The fixed point and immutable commit
- The complete diff commands
- The commit list
- The untracked task files
- The standards file list
- The complete smell baseline
- The standards report path.

Use this brief:

> Report each documented standards violation. Give the file and hunk. Cite the standards file and rule. Report possible baseline smells separately. Name each smell and quote the relevant hunk. Separate hard violations from judgment calls. Repository standards override the smell baseline. Do not repeat automated tool results. Use fewer than 400 words.

### Block-Plan Reviewer

Give the Block-Plan Reviewer these items:

- The fixed point and immutable commit
- The complete diff commands
- The commit list
- The untracked task files
- The finalized block path
- The `SPEC.md` path
- The block-plan report path.

Use this brief:

> Report missing or incomplete requirements. Report unrequested behavior. Report requirements that the implementation applies incorrectly. Quote the applicable block text for each finding. Use fewer than 400 words.

## Store and Report Results

Use these headings in the applicable reports:

```md
## Standards
```

```md
## Specification
```

Give each concrete finding a severity, file, hunk, evidence, and required correction. Keep possible smells separate from hard violations.

Do not merge or rerank the two reports. The Supervisor sends all concrete findings to the Review Resolver.

End the review round with one summary line. Give the finding total and most severe issue for each axis.

A block passes only when both axes contain no concrete finding. A change can pass one axis and fail the other.
