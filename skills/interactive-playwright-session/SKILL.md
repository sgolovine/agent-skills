---
name: interactive-playwright-session
description: Start and coordinate one reusable visible Playwright-controlled Chrome session that the user can interact with. Use when browser automation needs human-in-the-loop steps such as lengthy authentication, MFA, consent screens, captchas, SSO, or manual setup before Codex continues debugging, inspection, screenshots, console/network collection, or repeated local browser checks.
---

# Interactive Playwright Session

Use this skill when browser work should run through one reusable visible Chrome window so the user can complete human-only steps before Codex continues automation.

## Session Invariants

- Use exactly one daemon for the run.
- Use the bundled script at this skill's `scripts/interactive-playwright-session.mjs`.
- Start headed by default; do not pass `--headless` unless the user explicitly no longer needs to interact with the browser.
- Launch the Playwright Chrome channel by default. Use `--channel chromium` only when Google Chrome is unavailable and the user accepts Chromium.
- Store daemon state under `$RUN_DIR/browser-session/session.json`.
- Pass `BROWSER_SESSION_STATE_FILE="$RUN_DIR/browser-session/session.json"` to every browser-using agent.
- Use one browser context. Create multiple tabs in that context instead of multiple contexts, profiles, Browser plugin sessions, Playwright processes, or Chrome processes.
- Bind command access to `127.0.0.1`; the script stores the bearer token in the state file and protects command and shutdown endpoints with it.
- Use an installed workspace `playwright` dependency. Do not use `npx` to download a transient Playwright copy.
- Treat the state file as command access and ownership state, not as a durable browser storage snapshot. Cookies, storage, and tabs are usable while the daemon is running but should not be assumed to survive daemon stop or restart.

## Locate The Script

Set `INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT` to the absolute path of the bundled script before giving commands to other agents:

```sh
INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT="/path/to/interactive-playwright-session/scripts/interactive-playwright-session.mjs"
```

When this skill is installed from `agent-skills`, the repo copy is:

```sh
INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT="/home/sgolovine/Projects/agent-skills/skills/interactive-playwright-session/scripts/interactive-playwright-session.mjs"
```

## Start And Handoff

Run commands from the target repo root so Node resolves that repo's `playwright` dependency.

Start the visible Chrome session after the run directory exists:

```sh
node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" start --run-dir "$RUN_DIR" --fresh --url "$LOGIN_OR_APP_URL"
```

Record the JSON output in the run log or handoff notes, including:

- state file path
- daemon log path
- process id
- command string
- stop string
- mode
- browser channel
- active tabs
- cleanup ownership

Health-check the daemon before browser work:

```sh
BROWSER_SESSION_STATE_FILE="$RUN_DIR/browser-session/session.json"
node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" status --state-file "$BROWSER_SESSION_STATE_FILE"
```

When human authentication or setup is required, tell the user the visible Chrome window is ready and ask them to complete the flow in that window. Pause automation that depends on the authenticated state until the user confirms completion, then verify with a cheap command such as `url`, `title`, `text`, or a screenshot.

Do not ask the user to share passwords, one-time codes, cookies, tokens, or session storage. Do not dump authentication cookies or storage unless the task specifically requires it; prefer screenshots, current URL, page text, console events, and bounded network failures.

## Handoff Contract

Every browser-using subagent must receive:

- target repo root
- run directory path
- `BROWSER_SESSION_STATE_FILE`
- command prefix: `node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE"`
- assigned tab id or instructions to create one
- viewport assignment if a fixed viewport is required
- evidence directory
- lock expectations
- rule that no separate browser session may be created
- note that the user may be interacting with the visible Chrome window during human handoff periods

Allocate separate tabs for independent agents. Use per-tab commands for tab-scoped work and avoid sharing one tab between concurrent agents. If stable tab ownership is unavailable, run browser-using agents serially.

## Commands

Create a tab and capture a screenshot:

```sh
BROWSER_SESSION_STATE_FILE="$RUN_DIR/browser-session/session.json"
node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE" newtab http://localhost:8080
node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE" screenshot --tab 1 --path "$RUN_DIR/screenshots/home.png" --full-page
```

Common command verbs:

- Browser/global: `newtab`, `tabs`, `tab`, `closetab`, `status`, `clear-events`
- Navigation: `goto`, `reload`, `back`, `forward`
- Waiting and inspection: `wait`, `wait-for`, `title`, `url`, `text`
- Interaction: `click`, `fill`, `type`, `press`, `hover`, `select`, `scroll`, `setviewport`
- Evidence: `screenshot`, `cookies`, `storage`, `console`, `network`, `dialogs`
- Batches: `node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" batch --state-file "$BROWSER_SESSION_STATE_FILE" --file <commands.json>`

## Human Handoff Pattern

Use this sequence for apps with SSO, MFA, captchas, or long account setup:

1. Start the session at the login or app URL.
2. Confirm the daemon is healthy and the initial tab exists.
3. Ask the user to complete authentication in the visible Chrome window and report when finished.
4. After confirmation, run `url`, `title`, `text`, or `screenshot` on the same tab to confirm the expected app state.
5. Continue debugging or automation in the same browser context.

Avoid automated clicks or navigation while the user is actively completing auth unless the user asks for help and the action is clearly non-sensitive.

## Evidence Limits

- Keep console, network, and dialog evidence bounded and summarized.
- Store screenshots and compact JSON/text evidence under the run directory.
- Do not mirror raw CDP streams, WebSocket frames, full browser logs, cookies, storage, or unbounded console/event dumps into terminal output, run logs, or stack logs.
- If a browser event contains recursive Vite forwarding text, store a short summary and stop collecting that message class for the page.

## Cleanup

Stop only the daemon started for the current run:

```sh
node "$INTERACTIVE_PLAYWRIGHT_SESSION_SCRIPT" stop --state-file "$RUN_DIR/browser-session/session.json"
```

Never close the user's normal browser, an unrelated browser session, or another run's Playwright process. If cleanup cannot confirm ownership, leave the process running and report the uncertainty with the state file and daemon log path.
