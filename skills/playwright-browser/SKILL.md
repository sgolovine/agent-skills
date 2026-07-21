---
name: playwright-browser
description: Run browser automation through one reusable Playwright-controlled browser daemon, headless by default or visible when invoked with `interactive`. Use for browser testing, navigation, form interaction, screenshots, console/network inspection, shared browser state across repeated checks or subagents, and human-assisted login, MFA, SSO, captcha, consent, or manual setup flows.
---

# Playwright Browser

Run all browser work for a task through the bundled `scripts/playwright-browser.mjs`. Resolve its absolute path from this file once as `$PLAYWRIGHT_BROWSER_SCRIPT`, then run every command from the target repository root.

## Select The Mode

- Default to headless Chromium for `$playwright-browser` and implicit invocations.
- Use interactive mode only when the invocation includes `interactive`, as in `$playwright-browser interactive`, or the user otherwise asks for a visible browser. Interactive mode opens a visible Google Chrome window for user interaction.
- If Chrome is unavailable in interactive mode, use `--channel chromium` only after telling the user that the visible session will use Chromium.
- Keep the selected mode for the whole session. Stop and restart only when the user asks to change modes.

## Start

Choose a task-specific `$RUN_DIR`; use an existing run/output directory when available, otherwise create one such as `.agent-runs/<task>`. The state handle is `$RUN_DIR/browser-session/session.json`.

Start headless by default:

```sh
node "$PLAYWRIGHT_BROWSER_SCRIPT" start --run-dir "$RUN_DIR" --fresh --url about:blank
```

For an `interactive` invocation, start at the login or app URL:

```sh
node "$PLAYWRIGHT_BROWSER_SCRIPT" start --run-dir "$RUN_DIR" --fresh --interactive --url "$LOGIN_OR_APP_URL"
```

Without `--fresh`, start refuses to replace a healthy session. Optional flags are `--channel <chrome|chromium>`, `--viewport <WxH>`, `--idle-ms <ms>`, and `--timeout <ms>`. The default channel is Chromium in headless mode and Chrome in interactive mode.

On success, retain the printed `stateFile`, `logFile`, command prefix, and stop command. Health-check before browser work:

```sh
BROWSER_SESSION_STATE_FILE="$RUN_DIR/browser-session/session.json"
node "$PLAYWRIGHT_BROWSER_SCRIPT" status --state-file "$BROWSER_SESSION_STATE_FILE"
```

If Playwright is unavailable, let the script try the target project, a global installation, and `npx playwright` in that order before reporting failure.

## Session Rules

- Start one daemon and one browser context per task. Use tabs instead of additional browsers, contexts, or profiles.
- Treat the state file as the access handle. Do not expect tabs, cookies, or storage to survive a stop or restart.
- Headless sessions stop after 30 minutes without commands unless `--idle-ms` overrides it. Interactive sessions remain open for human interaction until explicitly stopped.
- Bind only to the daemon's existing `127.0.0.1` endpoint; never expose or copy the bearer token from the state file.
- If a command fails because the daemon is gone, check `status`, restart it, and re-establish tabs. Interactive authentication must be repeated after a restart.

## Human Handoff

Apply this section only in interactive mode:

1. Start at the login or app URL and confirm the daemon is healthy.
2. Tell the user the visible browser is ready and wait for them to finish login, MFA, SSO, captcha, consent, or other manual setup.
3. Do not click or navigate while the user is interacting unless they request a clearly non-sensitive action.
4. After the user confirms completion, verify the state with `url`, `title`, `text`, or a screenshot before continuing.

Never ask for passwords, one-time codes, cookies, tokens, or session storage. Do not dump cookies or storage unless the task specifically requires it.

## Commands

Create a tab, retain its returned id, and pass `--tab <id>` on later commands:

```sh
node "$PLAYWRIGHT_BROWSER_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE" newtab http://localhost:8080
node "$PLAYWRIGHT_BROWSER_SCRIPT" command --state-file "$BROWSER_SESSION_STATE_FILE" screenshot --tab 1 --path "$RUN_DIR/screenshots/home.png" --full-page
```

Available commands:

- Tabs: `newtab [url]`, `tabs`, `tab <id>`, `closetab [--tab <id>]`, `status`, `clear-events`
- Navigation: `goto <url>`, `reload`, `back`, `forward`; each accepts `--wait-until <state>`
- Inspection: `wait <ms>`, `wait-for <selector>`, `title`, `url`, `text [selector] [--limit <chars>]`
- Interaction: `click`, `fill`, `type`, `press`, `hover`, `select`, `scroll`, `setviewport`
- Evidence: `screenshot`, `cookies`, `storage`, `console [--limit <n>]`, `network [--limit <n>]`, `dialogs [--limit <n>]`

Batch multi-step sequences:

```sh
node "$PLAYWRIGHT_BROWSER_SCRIPT" batch --state-file "$BROWSER_SESSION_STATE_FILE" --file commands.json
```

Use `{"commands":[{"command":"goto","args":["http://localhost:8080"],"tabId":1}]}` as the batch shape. Each item accepts `command`, `args`, optional `tabId`, and optional `options`.

## Shared Use And Evidence

When handing the session to another agent, provide the target repo root, absolute script path, `BROWSER_SESSION_STATE_FILE`, command prefix, assigned tab id, evidence directory, and the rule not to start another browser. Give concurrent agents separate tabs and require `--tab`; run them serially if stable tab ownership is not possible. In interactive mode, also identify periods when the user controls the visible window.

Keep console, network, dialog, and text captures bounded. Store compact artifacts under `$RUN_DIR`; do not print raw event streams, full browser logs, cookies, storage, or unbounded output.

## Cleanup

In interactive mode, first confirm the user is finished because stopping closes the visible window and discards its authenticated state. Stop only the daemon identified by this run's state file:

```sh
node "$PLAYWRIGHT_BROWSER_SCRIPT" stop --state-file "$BROWSER_SESSION_STATE_FILE"
```

Never kill the user's normal browser or another run's process by pid. If ownership is uncertain, leave it running and report the state and daemon log paths.
