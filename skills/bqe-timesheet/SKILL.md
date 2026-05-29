---
name: bqe-timesheet
description: Fill, verify, save, and submit BQE Core weekly timesheets using the user's authenticated Chrome session. Use when the user asks for help with BQE Core, BQE time cards, weekly timecards, or gives project/task/hour instructions for BQE.
---

# BQE Timesheet

Use Chrome for BQE because login and account state require the user's authenticated browser session. Never handle credentials; open BQE Core and wait for the user to sign in if needed.

## Workflow

1. Open `https://www.bqecore.com/webapp/` in Chrome and wait until the authenticated BQE page is visible.
2. Navigate to `Weekly Time Card`. Keep the BQE tab open during pauses and after handoff.
3. Verify the weekly period before editing. If the user asks for the current week, reconcile the environment date with BQE's visible period; one observed account used Saturday-Friday weeks.
4. For each user-specified entry:
   - Select the project by the user's exact project name.
   - Select the requested task, or the only available task when the user says to use it.
   - Map daily hour inputs from the visible week headers before typing. In one Saturday-Friday BQE grid, the first two hour boxes were Saturday/Sunday and Monday-Friday were indexes 2-6.
   - Enter only the requested hours on the requested days, then save.
5. After each save, validate from the grid text/status. If the grid briefly still shows old values, wait and re-read before treating the save as failed.
6. Before submitting, verify the period, each row total, daily totals, weekly total, and workflow status match the user's instructions.
7. Click the actual submit control for the visible timesheet, not generic matching text. In one observed build, `.jsSubmitAllTimeEntries` in the header submitted all visible time entries.
8. Confirm final submission from BQE page evidence, especially submitted status. The success notification may report any number of updated records, such as `<n> record(s) updated successfully`; verify the submitted-hour total using the actual number of hours entered for the session, not a fixed example value.

## Safety Checks

- Do not submit until saved totals match the user's instructions.
- Trust explicit page validation over button clicks.
- If project names, task names, selectors, week layout, or status text differ, adapt to the current account UI and re-validate from visible BQE state.
