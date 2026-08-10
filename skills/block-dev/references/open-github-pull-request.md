# Open a Stacked GitHub Pull Request

Publish one reviewed block branch against its established parent branch.

## Prepare the Commit

1. Confirm that both review axes pass.
2. Confirm that the current branch is the assigned block branch.
3. Inspect `git status --short`.
4. Stage only files that belong to the assigned block.
5. Do not stage a file under `.block-dev/`.
6. Inspect `git diff --cached --name-only`.
7. Inspect the complete staged diff.
8. Remove an unrelated file from the index before commit.
9. Follow the repository commit convention.
10. Commit all task changes before publication.
11. Do not create an empty commit.

## Push the Branch

1. Push every local block commit.
2. Set the upstream when the branch has no upstream.
3. Confirm that the local branch and upstream contain the same commits.
4. Stop when the push fails.
5. Keep the local branch and commits when the push fails.

## Write the Pull Request Text

Read `$technical-english`. Use it in rules-only mode. Do not claim a full-dictionary result.

Use concise bullet lists instead of paragraphs. You can use terse bullet fragments when they make the description shorter.

Include only applicable information under these headings:

```md
## Summary

- <Change for users or developers>

## Implementation

- <Important review fact>

## Validation

- `<command>` — <result>

## Gaps

- <Known gap, skipped check, or follow-up>

## Visual Evidence

- <Screenshot or artifact link>
```

Remove an empty section. Protect commands, paths, identifiers, labels, and quoted text from editorial changes.

## Open the Pull Request

Open a draft pull request by default:

```sh
gh pr create --draft --base <parent>
```

Use the established parent branch for `<parent>`. This parent makes the pull request part of the stack.

Create a ready pull request only when the user explicitly requests that state. Do not mark a draft ready without explicit authority.

Do not merge the pull request. Request reviewers only when the user requests them.

Change remote repository settings only when the user requests the exact change.

## Handle GitHub CLI Failure

If `gh` is unavailable or unauthenticated, keep the pushed branch available. Report the repository compare URL and the exact blocker.

Do not retry publication through another tool. Stop the block workflow after the report.

If another `gh pr create` error occurs, report the exact command failure. Keep the pushed branch available for review.

## Return Publication Evidence

Return these results:

- The pull request URL
- The branch name
- The parent branch
- The pushed commits
- The validation results
- The skipped checks
- The unresolved risks.

Record the same evidence in `<run-path>/run-state.md`. Do not record credentials. Do not record tokens. Do not record secret values.
