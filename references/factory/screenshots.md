# Factory screenshots

Screenshots are PR evidence for changes with visible output: UI, rendered docs, CLI output, or API responses. Pure internal changes (refactors, tests, build or CI config, internal logic with no visible output) skip screenshots; the `## Screenshots` section then says why in one line.

Capture and upload with the T3 built-in browser (preview tools). It shares the user's GitHub sign-in. Tabs belong to the thread that opens them. `<r>` is `owner/repo`.

Verified on: https://github.com/sgolovine/agent-skills/pull/4 (public repo)

## 1. Plan scenarios

For each scenario record the route or command, state, viewport, and color scheme. UI changes get comparable Before/After pairs. Docs, CLI, and API changes get the rendered output, with a Before when it shows the change. Choose the smallest set that shows every visible change.

Keep all captures in a run directory outside every checkout, such as `${TMPDIR:-/tmp}/factory/<repo>/<slug-or-pr-n>/`. Name files `NN-before-<scenario>.png` and `NN-after-<scenario>.png`.

## 2. Runtime

- Reuse a running app only after proving it serves the right revision: check the process working directory, command, and build provenance, not just a responding port (`ss -ltnp`, `ps`, `docker compose ps`).
- Otherwise start it from the worktree with the repository's documented command and lockfile-aware install. Start only what is missing. Use a free port. Keep logs outside the checkout. Record the PIDs, ports, and containers you start.
- Before images come from the base revision. If you capture them before editing, the Dev thread's own worktree at the start SHA serves. Otherwise create a temporary detached worktree at the start or base SHA on another port; never reset the dev worktree:
  ```sh
  git -C <worktree> worktree add --detach <run-dir>/base <base-sha>
  ```
- Do not kill unknown processes, change shared services, or reset shared data. Stop only processes you started. Remove the base worktree with `git worktree remove <path>` when done.

## 3. Capture

1. `preview_open {open:false}` → `tabId`. Use that `tabId` in every later call.
2. `preview_resize {tabId, mode:"freeform", width:1280, height:800}` (same viewport for every pair). `preview_set_appearance` when the scenario fixes a color scheme.
3. `preview_navigate {tabId, target:{kind:"environment-port", port:<port>, path:"<route>"}}` for a dev server, or `{tabId, url}` for a public page.
4. Reach the state, then `preview_wait_for {tabId, locator:"<stable element>"}`.
5. `preview_snapshot {tabId, save:true, includeImage:true}` → copy `screenshotPath` into the run directory under its scenario name.
6. Inspect each image: fully rendered, right state and revision, comparable to its pair, no secrets or personal data. Retake bad captures.

Docs, CLI, and API output:
- Pushed Markdown docs: open GitHub's rendered file view `https://github.com/<r>/blob/<sha>/<path>`.
- CLI or API output: write it, HTML-escaped, into a `<pre>` in an HTML file in the run directory. Serve it with `python3 -m http.server <port> --bind 127.0.0.1 --directory <run-dir>` and navigate with an `environment-port` target. The browser does not open `file://` URLs.

## 4. Upload into the PR body

GitHub has no image-upload API. Use GitHub's own uploader in the signed-in T3 browser. Never invent upload endpoints or image URLs.

1. Open the PR page in the tab. Confirm sign-in: `preview_evaluate {tabId, expression:"document.querySelector('meta[name=\"user-login\"]')?.content"}` returns the user's login.
2. Find the new-comment composer from page state (`preview_snapshot`, then list `textarea` elements with `id`, `name`, `aria-label`, `placeholder`). Note a selector that matches exactly one textarea (`#new_comment_field` on PR pages). Do not type into it.
3. For each PNG:
   1. Store the bytes in the repository as an unreferenced blob. Its SHA equals `git hash-object <png>`:
      ```sh
      base64 -w0 <png> | jq -Rs '{encoding:"base64",content:.}' > <png>.json
      gh api repos/<r>/git/blobs --input <png>.json --jq .sha    # <blob sha>
      sha256sum <png>
      ```
      Private repository: also wrap the blob in a parentless commit. Never create or update a ref:
      ```sh
      tree=$(jq -n --arg s '<blob sha>' '{tree:[{path:"<name>.png",mode:"100644",type:"blob",sha:$s}]}' \
        | gh api repos/<r>/git/trees --input - --jq .sha)
      jq -n --arg t "$tree" '{message:"screenshot transfer",tree:$t,parents:[]}' \
        | gh api repos/<r>/git/commits --input - --jq .sha    # <commit sha>
      ```
   2. In one evaluate, fetch the bytes, check the hash, drop the file on the composer, wait for the upload, and clear the composer. **Never submit the comment.** `<bytes>` is one of:
      - Public repository: `Uint8Array.from(atob((await (await fetch('https://api.github.com/repos/<r>/git/blobs/<blob sha>')).json()).content.replace(/\n/g, '')), c => c.charCodeAt(0))`. Unauthenticated; 60 requests an hour.
      - Private repository: `new Uint8Array(await (await fetch('/<r>/raw/<commit sha>/<name>.png')).arrayBuffer())`. Keep the default credentials; `credentials:'include'` fails on the redirect to `raw.githubusercontent.com`. Verified on a public repository only; private-repository behavior is unconfirmed.
      ```js
      (async () => {
        const ta = document.querySelector('<composer selector>');
        const bytes = <bytes>;
        const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))]
          .map(b => b.toString(16).padStart(2, '0')).join('');
        if (hash !== '<sha256>') return { error: 'hash mismatch', hash, size: bytes.length };
        const dt = new DataTransfer();
        dt.items.add(new File([bytes], '<NN-after-scenario>.png', { type: 'image/png' }));
        ta.focus();
        for (const type of ['dragenter', 'dragover', 'drop'])
          ta.dispatchEvent(new DragEvent(type, { bubbles: true, cancelable: true, dataTransfer: dt }));
        let tag;
        for (let i = 0; i < 120 && !tag; i++) {
          await new Promise(r => setTimeout(r, 500));
          tag = ta.value.match(/<img [^>]*src="https:\/\/github\.com\/user-attachments\/assets\/[^"]+"[^>]*>|!\[[^\]]*\]\(https:\/\/github\.com\/user-attachments\/assets\/[^)]+\)/)?.[0];
        }
        Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(ta, '');
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        return { tag, cleared: ta.value === '' };
      })()
      ```
      Uploads take about 1–2 s. An `Uploading` placeholder may never appear, so wait for the `user-attachments` URL. GitHub inserts an `<img width=".." height=".." alt=".." src="https://github.com/user-attachments/assets/<uuid>" />` tag; record it as returned. If `tag` is empty, retry with a `paste` event (`new ClipboardEvent('paste', {bubbles:true, cancelable:true, clipboardData: dt})`), then by setting `.files = dt.files` on the composer's `input[type=file]` and dispatching a bubbling `change` event. If the fetch fails or the hash differs, the upload is a blocker (§5).
4. Write the image tags into the body file's `## Screenshots` section and apply it with `gh pr edit <n> --repo <r> --body-file <file>`:
   ```markdown
   ## Screenshots

   <one sentence on what reviewers should notice>

   Captured at `<short head OID>`.

   ### <scenario>

   | Before | After |
   | --- | --- |
   | <before img tag> | <after img tag> |
   ```
   Use labeled images without a table for output that has no Before. The `Captured at` line names the commit the After images show; reviewers use it to detect stale screenshots.
5. Reload the PR page. Confirm the description renders every image (count loaded `img` elements in the PR body with `naturalWidth > 0`) and take a snapshot.

## 5. Failure and cleanup

If capture or upload fails, still open or keep the PR. Keep the captures. Write the exact blocker in `## Screenshots` (what failed, at which step, what was tried). Report it. Do not post local paths.

Close every tab you opened with `t3_preview_close {tabId}`. Stop the processes you started and remove temporary worktrees.
