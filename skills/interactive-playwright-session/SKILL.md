---
name: interactive-playwright-session
description: Run browser automation through one reusable visible Playwright-controlled Chrome window the user can interact with. Use when browser work needs human-in-the-loop steps such as login, MFA, SSO, captchas, consent screens, or manual setup before automation continues with debugging, screenshots, or console/network collection.
---

# Interactive Playwright Session

Run browser work that needs human interaction through one visible Chrome window, driven by the bundled script at this skill's `scripts/interactive-playwright-session.mjs`. Resolve that path to an absolute path once (from this SKILL.md's location) and reuse it in every command below as `$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT`.

## Rules

- One daemon per run. Never start a second daemon, a separate Playwright process, or a raw Chrome process for the same task.
- One browser context. Open multiple tabs for parallel work; never create extra contexts or profiles.
- Headed by default so the user can interact. Pass `--headless` only if the user explicitly no longer needs to see the browser.
- Launches the Chrome channel by default. Pass `--channel chromium` only when Google Chrome is unavailable and the user accepts Chromium.
- Run all script commands from the target repo's root so Node resolves that repo's installed `playwright` dependency. Do not use `npx` to fetch a transient Playwright copy; if `playwright` is not installed in the workspace, stop and tell the user rather than installing it silently.
- The daemon binds to `127.0.0.1` and requires a bearer token stored in the state file, so the state file path is the only handle agents need. Treat it as an access handle, not durable browser storage: cookies, storage, and tabs are usable while the daemon runs but do not survive a stop or restart.
- The daemon shuts itself down after 30 minutes without commands (override with `--idle-ms <ms>` on start — consider a longer value if the user may take a while to authenticate). If a command fails because the daemon is gone, check `status`, then restart; the user will need to authenticate again.

## Start

Pick a run directory `$RUN_DIR` for this task's artifacts (an existing run/output directory if the workflow has one, otherwise create one, e.g. `.agent-runs/<task>`). The state file will be written to `$RUN_DIR/browser-session/session.json`.

Start at the login or app URL so the window opens somewhere useful:

```sh
node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" start --run-dir "$RUN_DIR" --fresh --url "$LOGIN_OR_APP_URL"
```

Notes:

- Without `--fresh`, start fails if a healthy session already exists at that state file. Reuse the existing session in that case; pass `--fresh` only when you intend to replace it.
- Optional start flags: `--headless`, `--channel <chrome|chromium>`, `--viewport <WxH>` (default 1280x720), `--idle-ms <ms>`, `--timeout <ms>` (startup wait, default 15000).
- On success, start prints JSON with `stateFile`, `logFile`, `pid`, `port`, `mode`, `browserChannel`, a ready-to-use `command` prefix, and a `stop` command. Record `stateFile` and `logFile` in the run log or handoff notes.

Set the state file variable and health-check before browser work:

```sh
BROWSER_SESSION_STATE_FILE="$RUN_DIR/browser-session/session.json"
node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" status --state-file "$BROWSER_SESSION_STATE_FILE"
```

## Human Handoff

Use this sequence for logins, SSO, MFA, captchas, or manual setup:

1. Start the session at the login or app URL and confirm the daemon is healthy.
2. Tell the user the Chrome window is ready and ask them to complete the flow in it, reporting back when done.
3. Pause all automation that depends on the authenticated state until the user confirms. Do not click or navigate while they are actively completing auth, unless they ask for help and the action is clearly non-sensitive.
4. After confirmation, verify the expected state with a cheap command on the same tab: `url`, `title`, `text`, or a screenshot.
5. Continue automation in the same browser context.

Never ask the user for passwords, one-time codes, cookies, tokens, or session storage. Do not dump cookies or storage unless the task specifically requires it; prefer screenshots, the current URL, page text, console events, and bounded network captures.

## Handoff To Subagents

Give every browser-using subagent:

- the target repo root (its working directory)
- `BROWSER_SESSION_STATE_FILE` (the script also reads this env var, so `--state-file` may be omitted when it is exported)
- the command prefix: `node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE"`
- its assigned tab id, or instructions to create its own tab with `newtab`
- the evidence directory for its screenshots and captures
- the rule that it must not start any other browser session
- a note that the user may be interacting with the visible window during handoff periods

Give each concurrent agent its own tab and have it pass `--tab <id>` on every command — commands without `--tab` target the daemon's active tab, which changes as tabs open and close (including when the user clicks around). If stable tab ownership can't be maintained, run browser-using agents serially instead.

## Commands

```sh
node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE" newtab http://localhost:8080
node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE" screenshot --tab 1 --path "$RUN_DIR/screenshots/home.png" --full-page
```

`newtab` returns the new tab's id; use it for all subsequent `--tab` arguments.

- Tabs: `newtab [url]`, `tabs`, `tab <id>` (make active), `closetab [--tab <id>]`, `status`, `clear-events`
- Navigation: `goto <url>`, `reload`, `back`, `forward` (all accept `--wait-until <state>`, default `domcontentloaded`)
- Waiting/inspection: `wait <ms>`, `wait-for <selector> [--state visible|attached|hidden|detached]`, `title`, `url`, `text [selector] [--limit <chars>]`
- Interaction: `click <selector>`, `fill <selector> <value>`, `type <selector> <text>`, `press <selector> <key>`, `hover <selector>`, `select <selector> <value>`, `scroll <x> <y>` (or `scroll bottom`), `setviewport <WxH>`
- Evidence: `screenshot --path <file> [--full-page]`, `cookies`, `storage`, `console [--limit <n>]`, `network [--limit <n>]`, `dialogs [--limit <n>]`

For multi-step sequences, batch commands in one call:

```sh
node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" batch --state-file "$BROWSER_SESSION_STATE_FILE" --file commands.json
```

where `commands.json` is `{"commands": [{"command": "goto", "args": ["http://localhost:8080"], "tabId": 1}, ...]}` — each entry takes `command`, `args` (array), optional `tabId`, and optional `options` (the `--flag` values as keys).

## Evidence Limits

- Keep console, network, and dialog captures bounded: use `--limit`, summarize, and store compact JSON/text and screenshots under the run directory.
- Do not dump raw event streams, full browser logs, cookies, storage, or unbounded console output into terminal output or run logs.
- If a page emits the same noisy message repeatedly (e.g. dev-server reload loops), record one short summary and stop collecting that message class.

## Cleanup

Before stopping, confirm the user is done with the window — stopping closes it and discards the authenticated session. Stop only the daemon this run started:

```sh
node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" stop --state-file "$RUN_DIR/browser-session/session.json"
```

Never kill the user's normal browser or another run's Playwright process by pid. If you can't confirm the daemon belongs to this run, leave it running and report that, along with the state file and daemon log paths.
