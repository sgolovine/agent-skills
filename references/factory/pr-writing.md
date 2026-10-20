# Factory PR writing

Apply to PR titles, PR bodies, review comments, and replies.

## Sentences

- Procedure sentences: 20 words or fewer. Description sentences: 25 words or fewer.
- One idea per sentence. Active voice. Imperative for instructions.
- Concrete nouns: name the file, function, command, or screen.
- One term per concept. Use the repository's terms.
- No filler, hedging, praise, or marketing words.
- Never post local paths, secrets, environment values, or raw logs. Quote the few log lines that matter.

## PR title

Conventional Commits style that matches the repository's history, for example `feat: add CSV export to reports`.

## PR body

Sections in this order:

```markdown
## Summary
What changes for the user or developer, and why.

## Changes
Implementation points a reviewer needs.

## Validation
Each command and its result. Each skipped check and why.

## Screenshots
A `Captured at <short head OID>` line and a Before/After table per scenario, or one line why none are needed, or the capture or upload blocker.

## Known gaps
Limits and follow-ups. Omit the section if there are none.
```

Keep the body true to the current head. When a later commit changes behavior, update `## Summary`, `## Changes`, `## Validation`, and `## Screenshots`.

## Review finding

```markdown
### f1 [P1] Imperative, specific title

- Location: `path/to/file.ext:line`
- Evidence: The input or state that triggers it and what the changed code does.
- Impact: The concrete consequence for users, data, security, operations, or compatibility.
- Recommendation: The smallest fix or test that addresses it.

<!-- factory-review -->
```

## Resolution reply

```markdown
Factory resolution: <fixed|rejected|already-fixed|disputed|unable-to-verify>

<What changed and the commits, or why no change is right.>
Evidence: <code path, test, or observed output>
Checks: <commands and results>
```
