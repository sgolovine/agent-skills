# Factory screenshots

Screenshots are PR evidence for changes with visible output: UI, rendered docs, CLI output, or API responses. Pure internal changes (refactors, tests, build or CI config, internal logic with no visible output) skip screenshots; the `## Screenshots` section then says why in one line.

Capture and upload with the T3 built-in browser (preview tools). It shares the user's GitHub sign-in. Tabs belong to the thread that opens them. `<r>` is `owner/repo`.

Verified on: <pending>

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
2. Find the new-comment composer from page state (`preview_snapshot`, then list `textarea` elements with `id`, `name`, `aria-label`, `placeholder`). Note a selector that matches exactly one textarea.
3. For each PNG:
   1. Encode and split locally:
      ```sh
      base64 -w0 <png> | fold -w 60000 > <png>.b64    # one chunk per line
      wc -l < <png>.b64; sha256sum <png>
      ```
   2. Send each line `k` (`sed -n '<k>p' <png>.b64`) in its own call. Reset with the first chunk:
      ```js
      (window.__factoryUpload = '<chunk 1>', window.__factoryUpload.length)
      (window.__factoryUpload += '<chunk k>', window.__factoryUpload.length)
      ```
   3. In one evaluate, build the file, check its hash against `sha256sum`, and drop it on the composer:
      ```js
      (async () => {
        const ta = document.querySelector('<composer selector>');
        const bytes = Uint8Array.from(atob(window.__factoryUpload), c => c.charCodeAt(0));
        const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))]
          .map(b => b.toString(16).padStart(2, '0')).join('');
        const file = new File([bytes], '<NN-after-scenario>.png', { type: 'image/png' });
        const dt = new DataTransfer(); dt.items.add(file);
        ta.focus();
        for (const type of ['dragenter', 'dragover', 'drop'])
          ta.dispatchEvent(new DragEvent(type, { bubbles: true, cancelable: true, dataTransfer: dt }));
        window.__factoryUpload = '';
        return { hash, size: file.size };
      })()
      ```
      If the hash differs, resend the chunks. If no upload starts, retry with a `paste` event (`new ClipboardEvent('paste', {bubbles:true, cancelable:true, clipboardData: dt})`). As a last resort, set `.files = dt.files` on the composer's `input[type=file]` and dispatch a bubbling `change` event.
   4. Wait for the upload in one evaluate that returns a Promise polling `ta.value` every 500 ms for up to 60 s. Done means the value contains an `https://github.com/user-attachments/assets/` URL (Markdown `![...](...)` or `<img ... src="...">`) and no `Uploading` placeholder. Record that image Markdown for the file.
   5. Clear the composer so React sees it, and **never submit the comment**:
      ```js
      (() => { const ta = document.querySelector('<composer selector>');
        Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(ta, '');
        ta.dispatchEvent(new Event('input', { bubbles: true })); return ta.value.length; })()
      ```
4. Write the image Markdown into the body file's `## Screenshots` section and apply it with `gh pr edit <n> --repo <r> --body-file <file>`:
   ```markdown
   ## Screenshots

   <one sentence on what reviewers should notice>

   Captured at `<short head OID>`.

   ### <scenario>

   | Before | After |
   | --- | --- |
   | <before image Markdown> | <after image Markdown> |
   ```
   Use labeled images without a table for output that has no Before. The `Captured at` line names the commit the After images show; reviewers use it to detect stale screenshots.
5. Reload the PR page. Confirm the description renders every image (count loaded `img` elements in the PR body with `naturalWidth > 0`) and take a snapshot.

Each 60 000-character chunk is one tool call. Keep images small: capture the viewport, not the full page. If `pngquant` or `oxipng` is installed, compress before encoding.

## 5. Failure and cleanup

If capture or upload fails, still open or keep the PR. Keep the captures. Write the exact blocker in `## Screenshots` (what failed, at which step, what was tried). Report it. Do not post local paths.

Close every tab you opened with `t3_preview_close {tabId}`. Stop the processes you started and remove temporary worktrees.
