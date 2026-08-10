# Review Code Against Standards and a Specification

Review the diff between `HEAD` and a fixed point on two separate axes:

- **Standards**: Does the code comply with the documented coding standards in the repository?
- **Specification**: Does the code implement the source issue or specification correctly?

Run the two reviews with parallel subagents. Then, report their findings separately.

## 1. Pin the Fixed Point

Use the commit, branch, tag, or other reference that the user gives as the fixed point. If the user does not give one, ask for it.

Use this three-dot diff so that the comparison starts at the merge base:

```sh
git diff <fixed-point>...HEAD
```

Also record the commits:

```sh
git log <fixed-point>..HEAD --oneline
```

Before you continue:

1. Confirm that the fixed point resolves with `git rev-parse <fixed-point>`.
2. Confirm that the diff is not empty.
3. Stop if the reference is not valid or the diff is empty.

## 2. Find the Specification Source

Search for the source in this order:

1. Issue references in commit messages, such as `#123`, `Closes #45`, or GitLab `!67`. Use the issue-tracker instructions in the repository if they exist.
2. A specification path that the user gives.
3. A file under `docs/`, `specs/`, or `.scratch/` that matches the branch name or feature.
4. If you cannot find a source, ask the user for it.

If the user confirms that there is no specification, skip the Specification review and report `No specification available`.

## 3. Find the Standards Sources

Find repository files that define how contributors must write code. Examples include `CODING_STANDARDS.md`, `CONTRIBUTING.md`, and applicable agent instruction files.

Also apply the smell baseline below. The baseline contains heuristics from Martin Fowler's *Refactoring*, chapter 3.

Apply these rules:

- **The repository overrides the baseline.** If a documented repository standard permits a pattern, do not report that pattern as a smell.
- **Smells are judgment calls.** Label each smell as a possible issue, not as a hard violation.
- **Do not duplicate tool results.** Do not report rules that automated tools already enforce.

Check the diff for these smells:

- **Mysterious Name**: A function, variable, or type name does not show its purpose. Rename it. If no accurate name is available, examine the design.
- **Duplicated Code**: The same logic shape occurs in more than one changed location. Extract the shared logic.
- **Feature Envy**: A method uses another object's data more than its own data. Move the method to the object that owns the data.
- **Data Clumps**: The same fields or parameters frequently occur together. Put them in one type.
- **Primitive Obsession**: A primitive or string represents a domain concept that needs its own type. Create a small domain type.
- **Repeated Switches**: The same `switch` statement or `if` cascade on the same type occurs in multiple locations. Use polymorphism or one shared map.
- **Shotgun Surgery**: One logical change requires edits in many separate files. Put related behavior in one module.
- **Divergent Change**: One file or module changes for several unrelated reasons. Split the separate responsibilities.
- **Speculative Generality**: The change adds abstractions, parameters, or hooks that the specification does not require. Remove or inline them until there is a real need.
- **Message Chains**: A caller uses a long chain such as `a.b().c().d()`. Hide the navigation behind a method on the first object.
- **Middle Man**: A class or function primarily delegates to another component. Remove it and call the target directly.
- **Refused Bequest**: A subclass or implementer ignores or overrides most inherited behavior. Replace inheritance with composition.

## 4. Run the Reviews in Parallel

### Standards Subagent

Give the subagent:

- The complete diff command.
- The commit list.
- The list of standards files.
- The complete smell baseline from this fragment.
- This brief:

> Report each place where the diff violates a documented standard. Give the file and hunk, and cite the standards file and rule. Also report possible baseline smells. Name each smell and quote the relevant hunk. Separate hard violations from judgment calls. A documented repository standard overrides the smell baseline. Do not report rules that automated tools enforce. Use fewer than 400 words.

### Specification Subagent

Give the subagent:

- The complete diff command.
- The commit list.
- The path or fetched content of the specification.
- This brief:

> Report requirements that are missing or incomplete, behavior that the specification did not request, and implemented requirements that appear incorrect. Quote the applicable specification text for each finding. Use fewer than 400 words.

If no specification is available, do not run this subagent.

## 5. Report the Results

Use these headings:

```md
## Standards

## Specification
```

Keep the two reports separate. Do not merge or rerank their findings. You can make small edits for clarity.

End with one summary line that contains:

- The total number of findings for each axis.
- The most severe issue in each axis, if one exists.

Do not select one issue as the overall winner.

## Why the Axes Are Separate

A change can pass one review and fail the other:

- Code can comply with all standards but implement the wrong behavior.
- Code can implement the specification correctly but violate repository standards.

Separate reports prevent one axis from hiding problems in the other.
