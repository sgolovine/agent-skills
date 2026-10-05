# Runtime Validation and Screenshot Evidence

Read this for screenshot capture and PR upload on every task, and runtime setup when validation needs a running application. Use installed command-line tools and repository scripts, without relying on a harness browser or another skill.

## Discover and reuse the runtime

1. **Inspect existing services first.** Check documented URLs, listening ports, and processes, for example `ss -ltnp` or `lsof -nP -iTCP -sTCP:LISTEN`, `ps`, and `docker compose ps` when relevant. Probe a known local URL with `curl`. A responding port alone does not prove which app or revision it serves: verify the process working directory, command, container mounts or image, and build provenance. Reuse a suitable running app and its dependencies; do not launch duplicates.
2. **Discover the intended startup procedure.** Prefer repository instructions, README/development docs, and CI setup. If insufficient, inspect project structure: package scripts and lockfiles, workspace configuration, `compose.yaml`/`docker-compose.yml`, Makefiles, framework manifests, and required services. A `dev` or `start` script suggests the project command; a Compose file may describe only dependencies, so inspect its services before deciding to run the whole stack. Determine the correct working directory, runtime version, configuration, and package manager.
3. **Verify suitability for each check.** The baseline must serve the recorded start SHA; final validation must serve the task worktree's final code. Reuse a server throughout when it already serves that worktree with reliable live reload. An original-checkout server can supply baseline evidence only if its source matches the baseline and has no contaminating local changes; it cannot validate a different worktree's implementation. If an existing server cannot serve the required revision, leave it intact and start the necessary instance on a free port. Reuse compatible dependency services with isolated test data.
4. **Start only what is missing.** Install dependencies according to repository guidance and lockfiles; use documented environment examples and available local test configuration. Run the discovered command from the intended worktree, such as `npm run dev`, `npm start`, or `docker compose up -d <services>`, only when supported by that project. For Compose, choose a unique project name and check for fixed container names, ports, and shared volumes before starting an isolated stack. Keep logs outside the checkout; record PIDs, ports, URLs, and Compose resources created by this task. Wait for observable readiness and inspect startup errors before testing.
5. **Handle failures without destructive guesses.** Diagnose logs, missing dependencies, configuration, and port conflicts; retry after addressing the cause. Do not kill an unknown port owner, modify an existing server, or reset shared data to make a check pass. Missing access or credentials may block some checks; continue the checks that remain possible and record the missing evidence. Stop only task-owned processes and containers, preserving shared services and screenshot artifacts.

## Capture comparable screenshots

- Capture before images at the recorded baseline before editing UI behavior. If missed, create a temporary detached baseline worktree with `git worktree add --detach <unique-path> <start-sha>` and follow the same runtime discovery rules. Never reset the development worktree to recreate the baseline.
- Use the project's existing browser/E2E tooling or a local automation script invoked from the shell, such as `node <capture-script>`. With Playwright, navigate to the discovered app URL, reach the planned state, wait for a stable relevant locator, and use `page.screenshot({ path, fullPage: true })`. Do not assume a browser package is installed; use the documented setup and keep temporary capture dependencies and scripts outside the repository unless they belong in the change.
- Match routes, interactions, viewport, color scheme, screenshot dimensions, fixture data, account state, and relevant flags between captures. Record the baseline SHA and final commit, commands, URL, and scenario for each pair. For new UI, capture the previous route or flow where the addition belongs. A loading screen or unrelated page is not a baseline.
- Inspect every saved image for complete rendering, comparable state, the intended change, and absence of secrets. Retake misleading captures. Store labeled files such as `01-before-settings.png` and `01-after-settings.png` outside the checkout.

## Capture non-UI evidence

Capture actual task-relevant output such as rendered documentation, CLI behavior, or API responses using available local rendering or screenshot tools. Record the revision, command or URL, and scenario. Inspect images for readability, correct output, and absence of secrets; preserve labeled files outside the checkout. Capture before-and-after output where it demonstrates the change. If capture is blocked, report the exact blocker and keep screenshot delivery incomplete.

## Publish the evidence

Upload every task's screenshots to one PR comment and link that comment from the PR body. Use the repository's established image upload method when it produces durable, reviewer-accessible images displayed in the comment. Otherwise use an already authenticated GitHub web session through a shell-driven browser script:

1. Open the created PR URL and verify the repository and PR. Browser authentication is separate from `gh auth status`; if no authorized unattended session is available, preserve the images and report the upload blocker.
2. Locate the conversation comment composer and its attachment/file-upload control from observed page state. Add a concise summary and scenario labels, using Before/After pairs for UI changes and descriptive labels for non-UI output.
3. Attach the local images through that control. Wait for every upload to finish and its preview or generated image Markdown to appear. Preserve the generated image URLs; never invent upload endpoints or image URLs.
4. Submit the comment once. If navigation or a transient error makes submission uncertain, inspect the PR for the comment before retrying to avoid duplicates.
5. Confirm the posted comment is visible on the requested PR and displays every image. Inspect the rendered result, obtain the comment permalink, and add it to the prepared PR body with `gh pr edit <pr> --body-file <file>`.

A compact UI comment can use:

```markdown
## Screenshots

<one-sentence summary of what reviewers should notice>

### <scenario>

| Before | After |
| --- | --- |
| <uploaded before image> | <uploaded after image> |
```

For non-UI work, use labeled images without implying a UI comparison. Include validation results when available, or standalone screenshot evidence when checks are blocked.

`gh pr comment <pr> --body-file <file>` can publish Markdown containing already uploaded image URLs, but neither it nor `gh pr edit` uploads local images. Local paths or other artifact links do not satisfy screenshot publication.

Do not require interactive login or create a new public hosting location as a workaround. If capture, upload, or posted-image verification fails, retain the captures and prepared comment, include the exact blocker in the draft PR and final report, and leave screenshot delivery marked incomplete.
