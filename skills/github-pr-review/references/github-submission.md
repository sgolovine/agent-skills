# GitHub Review Submission

The authorization boundary in `../SKILL.md` applies. Use one reviewed revision and one submission mechanism per review.

## Pre-Submission Gate

1. Query `baseRefOid` and `headRefOid` again immediately before writing.
2. If the head OID differs from the reviewed head, stop without submitting and review the new head. If the base OID changed, recompute the merge base and refresh any affected coverage, findings, and CI claims first.
3. Choose the review event:
   - `COMMENT` for non-blocking feedback or when material coverage or verification is incomplete.
   - `REQUEST_CHANGES` only for a verified blocking finding.
   - `APPROVE` only when the user requested that decision, the reviewed head is current, all material files were covered, and no unresolved high-risk intent, CI, or validation gap remains.

## Summary-Only Review

Set `PR_NUMBER`, `REPOSITORY` (`[HOST/]OWNER/REPO`), and `REVIEW_BODY` to the reviewed target and temporary body-file path. Write multiline review text to that file rather than passing it through `--body`:

```sh
gh pr review "$PR_NUMBER" \
  --repo "$REPOSITORY" \
  --comment \
  --body-file "$REVIEW_BODY"
```

Replace `--comment` with `--request-changes` or `--approve` only when the event gate permits it.

## Review With Inline Findings

`gh pr review` cannot create line-anchored comments. Serialize the summary and findings with a JSON-aware tool into a payload such as:

```json
{
  "commit_id": "<reviewed-head-oid>",
  "body": "<review summary>",
  "event": "COMMENT",
  "comments": [
    {
      "path": "path/to/file.ext",
      "line": 42,
      "side": "RIGHT",
      "body": "<finding body>"
    }
  ]
}
```

Use `RIGHT` and the new-file line for additions or context, and `LEFT` with the old-file line for deletions. Anchor only to lines present in the pinned PR diff. Set `HOST`, `OWNER`, `REPO`, and `REVIEW_PAYLOAD` to the canonical target and temporary JSON-file path, then submit the payload once:

```sh
gh api --hostname "$HOST" --method POST \
  "repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews" \
  --input "$REVIEW_PAYLOAD"
```

Do not also run `gh pr review` for the same review. If a finding cannot be anchored, keep its `path:line` location in the top-level body. If GitHub rejects an anchor or reports a stale commit, stop and revalidate instead of retrying against a different revision.
