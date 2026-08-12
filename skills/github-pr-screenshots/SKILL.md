---
name: github-pr-screenshots
description: Capture comparable before-and-after screenshots for a GitHub pull request that contains user-interface changes, then upload the images to that PR. Use when the user provides a concrete PR URL or number and asks for UI screenshots, visual evidence, or a before/after comparison; require an actual UI change and do not use for backend-only or non-visual PRs.
---

# GitHub PR Screenshots

Produce trustworthy visual evidence from the PR's exact base and head commits, then publish it to the requested PR through GitHub's web UI.

## Required browser workflow

Read and follow the sibling `bw-browser` skill completely before browser work. Use BetterWright in headed mode for every browser command. Keep one visible `betterwright repl --headed` session alive with the private-FIFO handoff pattern from that skill so the user can log in to GitHub and the same session can perform the upload. Never replace it with a headless browser.

## Workflow

1. **Resolve and qualify the PR.** Require a concrete GitHub PR URL or an unambiguous PR number plus repository. Use `gh pr view` to obtain the PR URL, base ref, base SHA, head ref, and head SHA. Inspect the changed-file list and relevant diff. Summarize the visible behavior that changed. If the PR has no UI change, stop and explain that this skill's invocation gate is not met.

2. **Determine the comparison scenarios.** Read the repository instructions and any required app/browser skills. Map the diff to the affected route, component, state, and viewport. Choose the smallest set of screenshots that demonstrates every material UI change. Record any interactions needed to reach each state. Do not infer the page solely from filenames when routes or call sites can be inspected.

3. **Prepare exact, isolated revisions.** Fetch the PR refs, then create temporary detached Git worktrees at the base SHA (the target branch's PR baseline) and head SHA. Do not switch or modify the user's active checkout. Record every temporary path and process that this run creates. Install or build only what the repository requires.

4. **Run comparable app instances.** Start the base and head revisions on distinct ports when the app supports it; otherwise run them sequentially. Use the same environment, backend, fixture data, account, feature flags, viewport, color scheme, zoom, and application state. Follow repository startup instructions. Do not include unrelated personal or secret data in a screenshot.

5. **Capture the before images.** In the persistent headed BetterWright session, open the base instance, reach the first chosen state, wait for a stable task-relevant locator, and capture a PNG with `page.screenshot({ path, fullPage: true })`. Use a stable filename such as `01-before-<scenario>.png`. Repeat only for materially distinct scenarios.

6. **Capture the after images.** Open the head instance in the same browser session and reproduce each scenario exactly. Capture corresponding files such as `01-after-<scenario>.png` with identical viewport and full-page settings. If shared state changed during the before pass, reset it before capturing the after state.

7. **Verify the evidence.** Inspect every saved image. Confirm that each pair shows the intended screen, is fully rendered, has comparable state and dimensions, and clearly exposes the PR change. Retake blank, loading, clipped, obscured, or mismatched images. Do not publish misleading pairs.

8. **Open GitHub and hand off login when needed.** Navigate the same headed REPL to the PR URL. If GitHub is signed out or requests MFA, keep the browser open, capture the required question screenshot, tell the user the visible browser is ready, and wait for them to finish. After they respond, verify the authenticated PR page in that same REPL. Do not start a second BetterWright process while the handoff owns the profile.

9. **Upload one PR comment.** Locate the PR conversation comment composer from observed page state. Add a concise summary of the UI changes and label each scenario `Before` and `After`. Attach the local PNGs through the composer's observed file-upload control, wait until every upload finishes and its preview or generated Markdown is present, then submit the comment once. The user's request to run this skill authorizes this PR comment; do not ask for another confirmation. Avoid duplicate submission after navigation or transient errors.

10. **Verify and clean up.** Confirm the posted comment is visible on the requested PR and contains every image; capture and inspect a proof screenshot. Then stop only the recorded servers and BetterWright PID, remove the temporary worktrees, and delete temporary artifacts. If posting cannot be verified, preserve the screenshots, report their paths and the blocker, and do not claim success.

## Comment format

Use a compact comment that explains what reviewers should notice:

```markdown
## UI screenshots

<one-sentence summary of the visible PR change>

### <scenario>

| Before | After |
| --- | --- |
| <uploaded before image> | <uploaded after image> |
```

Use separate scenario sections when one pair cannot show all material UI changes. Never publish screenshots from approximate branches, stale builds, or unequal states.
