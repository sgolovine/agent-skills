# BetterWright Browser Findings

## Task

Open `http://localhost:3000` in a visible browser and leave it open so the user can complete login manually.

## What happened

### 1. The documented `note` requirement has no documented implementation

The skill says:

> Put a short present-tense `note` on every call.

I interpreted that as a JavaScript helper and tried:

```js
note("Opening the local app so you can sign in");
```

BetterWright failed with:

```text
note is not defined
```

The examples in the skill do not show a `note` argument, helper, CLI flag, or supported syntax. I subsequently used a JavaScript comment as the note:

```js
/* note: Opening the local app so you can sign in. */
```

That avoids an execution error, but it is unclear whether comments satisfy the intended observability requirement.

### 2. Separate `betterwright run` calls do not retain the open page

The first successful command navigated to the app and returned while it was still showing `Checking session...`.

I then issued another `betterwright run --headed` call to wait and inspect the page. That invocation opened on `about:blank`, because page/tab state does not persist between separate `run` invocations.

This behavior is consistent with the skill's statement that cookies persist across invocations while open tabs and in-memory state persist only within one `repl` session. However, the consequence for human handoff tasks is not explicit enough: a successful one-shot `run` is not sufficient evidence that a headed window will remain on the requested page for the user.

### 3. The initial screenshot was taken before the application finished redirecting

Immediately after `page.goto("http://localhost:3000")`, the app displayed `Checking session...` and had no interactive elements. A later wait inside a persistent REPL session showed that the app redirected to:

```text
http://localhost:3000/login?returnTo=%2F
```

The visible login page contained:

- `Continue with BQE`
- `Sign in as Mock User`

For client-rendered authentication gates, navigation completion alone does not mean the login page is ready. The browser workflow should wait for a stable, task-relevant element or URL rather than immediately handing control to the user.

### 4. A persistent human-handoff session required an undocumented shell workaround

To keep the headed browser and page alive, I started `betterwright repl --headed` in the background and kept its stdin open:

```bash
mkdir -p /tmp/betterwright-user-login
nohup bash -c '{
  printf "%s\n\n" \
    "/* note: Keeping the local sign-in page open for the user. */ await page.goto(\"http://localhost:3000\"); await page.waitForTimeout(2500); return { url: page.url(), title: await page.title(), view: await snapshot({interactive: true}), shot: await screenshot({kind: \"question\"}) };"
  tail -f /dev/null
} | betterwright repl --headed' \
  >/tmp/betterwright-user-login/session.log 2>&1 &
```

This worked, but it is awkward and has drawbacks:

- It relies on `tail -f /dev/null` solely to keep stdin open.
- It leaves a background shell/REPL process running.
- The skill does not explain lifecycle management or cleanup.
- The user cannot easily tell which process owns the browser session.
- A future agent may accidentally start another invocation and get an unrelated blank page.

## Recommended skill-file improvements

### Clarify exactly how to provide a call note

Replace the ambiguous requirement with supported syntax. For example, if comments are accepted:

```md
Put a short present-tense JavaScript comment at the start of every snippet:

    /* note: Opening the sign-in page for the user. */

BetterWright does not expose a global `note()` helper; do not call `note(...)`.
```

If BetterWright has a real note option or API, document its exact invocation and add it to every example instead.

### Add a dedicated section for manual user handoff

Suggested text:

```md
## Leaving a headed browser open for the user

A one-shot `betterwright run --headed` invocation is not suitable when the user
must manually interact after the command returns. Each `run` invocation starts
with a new page, and open tabs persist only for the lifetime of one `repl`
session.

For manual login, MFA, CAPTCHA handoff, or visual inspection:

1. Start one long-lived `betterwright repl --headed` process.
2. Navigate and wait until the task-relevant page is visibly ready.
3. Keep the REPL process and its stdin alive while the user interacts.
4. Do not issue a separate `run` command to inspect that session.
5. Record the process ID and log path.
6. After the user says they are finished, resume through the same REPL if the
   harness supports it, or stop the background process explicitly.

If the CLI provides a supported detach/session-name/resume mechanism, prefer it
over shell keepalive workarounds and document the exact commands here.
```

### Provide a supported persistence example

The best fix would be a first-class BetterWright command, such as a documented detached/session mode:

```bash
betterwright repl --headed --detach --session user-login
betterwright exec --session user-login -c \
  'await page.goto("http://localhost:3000"); await page.getByRole("button", {name: "Continue with BQE"}).waitFor()'
```

That syntax is illustrative, not currently verified. The skill should only include it if the CLI actually supports those options.

If no first-class feature exists, document a vetted shell recipe and its cleanup command. For example:

```bash
kill "$BETTERWRIGHT_REPL_PID"
```

The recipe should use a named FIFO or another controllable stdin channel if the agent may need to send follow-up snippets to the same session. `tail -f /dev/null` keeps the process alive but does not provide a practical resume channel.

### Explain readiness checks for client-rendered login pages

Add guidance like:

```md
After navigating to an application with an authentication/session gate, do not
hand control to the user while a loading state such as "Checking session..." is
visible. Wait for a task-relevant URL or element, then take the question
screenshot. Prefer an exact locator or URL condition over a fixed timeout.
```

Example:

```js
await page.goto("http://localhost:3000");
await page.waitForURL(/\/login(?:\?|$)/);
await page.getByRole("button", { name: "Continue with BQE" }).waitFor();
return {
  view: await snapshot({ interactive: true }),
  shot: await screenshot({ kind: "question" }),
};
```

### Warn against inspecting a handoff session with a new `run`

Suggested warning:

```md
Do not use a second `betterwright run` to verify a page opened by an earlier
`run` or `repl`; it will not attach to that page. Verification and screenshots
must occur in the same long-lived REPL session that owns the page.
```

### Document lifecycle and cleanup

The skill should state:

- Whether the browser daemon remains after the CLI process exits.
- Whether the visible window closes when REPL stdin closes.
- How to list active BetterWright sessions/processes.
- How to resume or send commands to a detached session.
- How to close only the handoff session without killing unrelated browser work.
- Whether browser profile locking prevents concurrent invocations.

## Suggested concise replacement workflow

A future agent handling “open this page and let me log in” should:

1. Start a visible, long-lived REPL session rather than a one-shot run.
2. Navigate to the requested URL in that same session.
3. Wait for the actual login control or login URL.
4. Capture and inspect a `question` screenshot.
5. Leave that exact session running and tell the user the page is ready.
6. Keep the session identifier/PID and log path for later verification or cleanup.
7. After the user completes login, verify success in the same session and capture a `proof` screenshot when appropriate.

## Result of this task

The persistent REPL reached the expected login page at:

```text
http://localhost:3000/login?returnTo=%2F
```

The successful session log was written to:

```text
/tmp/betterwright-user-login/session.log
```

The question screenshot was written under the BetterWright artifact directory. The browser was kept open by the background REPL process, but the process lifecycle should be handled through a documented first-class BetterWright session mechanism rather than the workaround used here.
