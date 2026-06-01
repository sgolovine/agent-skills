---
name: flight-research
description: Run two-pass flight research with supervisor-managed subagents across flight search engines, non-ATPCO carrier sites, and direct carrier validation, aligned to user constraints and written to SQLite output. Use only when origin IATA code, destination IATA code, passenger count, departure date, and return date are provided; date mode may be relative or exact and defaults to relative.
---

# Flight Research

## Operating Principle

Create the SQLite database first, coordinate research through a supervisor/worker loop, validate every promising option against the user's trip constraints, and rank by total party price before comfort.

## Required Inputs

Do not run browser research or create a SQLite run unless these inputs are provided:

- origin airport as an IATA airport code,
- destination airport as an IATA airport code,
- number of passengers,
- departure date,
- return date.

`date mode` is optional; use `relative` unless the user provides `exact`.

If any required input is missing or not specific enough to search, ask one concise batch of questions and stop.

## Defaults

- Round trip unless otherwise specified.
- Economy cabin unless otherwise specified.
- One carry-on and one personal item per passenger; exclude checked bags unless requested or needed for a fair comparison.
- `relative` date mode: search the specified departure and return dates first, then compare flights with departure and return dates up to 3 calendar days before or after the specified dates.
- `exact` date mode: search only the specified departure and return dates.
- No airport transfers. Discard itineraries that arrive at one airport and depart from another.
- Minimum connection buffers: 2 hours domestic same-airport; 3 hours for international, immigration, customs, re-checking bags, or self-transfer.
- Do not book, purchase, log in, send traveler details, or enter payment information without explicit confirmation for that exact browser action.

## Agent Roles

Use the current agent as **Supervisor**. Spawn subagents for each worker role when the harness supports subagents; if it does not, tell the user and preserve the same role boundaries in a serialized run.

- **Supervisor**: creates the run database, assigns work, routes Research outputs to Alignment and Writer, monitors progress, closes stalled agents, reassigns their work to fresh agents, and keeps the user informed.
- **Research**: searches one assigned source or carrier in either Pass 1 or Pass 2, then returns structured candidate data with source URLs, timestamps, uncertainty, and screenshots or notes when useful. During rate limits, queue waits, bot checks, or slow page loads, report `backoff` status with an expected next check-in so the Supervisor does not treat the agent as stalled.
- **Alignment**: checks Research output against the user's route, dates, passengers, cabin, baggage, airport-transfer, connection-buffer, self-transfer, and date-mode constraints. Return accepted candidates, rejected candidates, and specific reasons.
- **Writer**: formats accepted data and writes it to the SQLite database. If subagents cannot safely mutate the same database, the Writer returns SQL or structured rows and the Supervisor applies them locally, recording the Writer as the source.

## Progress Updates

Whenever any task starts, enters backoff, finishes, fails, is reassigned, or begins research/alignment/writing, log a `research_events` row and show the user a compact progress table:

| Pass | Task | Agent | Status | Last Update | Notes |
| --- | --- | --- | --- | --- | --- |

Treat a Research agent as stuck when it has no update after its promised backoff/check-in time, or after a reasonable timeout for the site being searched. Close stuck agents before reassigning their task. Do not close agents that are explicitly in a current backoff period.

## SQLite Contract

Every run must create a fresh SQLite database before flight research starts. Treat the database as the durable output; the final response is a summary of database facts.

1. Create a run directory, defaulting to `flight-research-output/<YYYYMMDD-HHMMSS>/` in the current workspace unless the user requested another location.
2. Initialize the database from this skill folder:

   ```sh
   python3 scripts/init_flight_research_db.py --output flight-research-output/<run-id>/flight_research.sqlite
   ```

3. If the initializer cannot use Python's standard `sqlite3`, use another available SQLite client or library and apply `references/schema.sql` directly.
4. Insert one `research_runs` row with the request, defaults, clarified assumptions, and database path before browser research.
5. Record assumptions, agent tasks, progress events, searches, candidates, alignment checks, fares, baggage policies, connection buffers, discard reasons, writer outputs, and final recommendations as research proceeds.
6. Before responding, query SQLite for final facts. Do not rely on notes outside the database.

Use `references/schema.sql` as the schema source of truth.

## Workflow

1. Read `$browser:browser`, then use the browser for live search.
2. Confirm the request has origin IATA, destination IATA, passenger count, departure date, and return date. Default missing date mode to `relative`. If required inputs are missing, ask and stop before creating the SQLite run.
3. Spawn Pass 1 Research agents, one per source: [Google Flights](https://www.google.com/travel/flights), [ITA Matrix Airfare Search](https://matrix.itasoftware.com), [Expedia](https://www.expedia.com/), [Booking.com](https://www.booking.com/), [Skyscanner](https://www.skyscanner.com/), [Cheap Flights](https://www.cheapflights.com/), [Kayak](https://www.kayak.com/flights), [Southwest Airlines](https://www.southwest.com/), [Ryanair](https://www.ryanair.com/), and [easyJet](https://www.easyjet.com/). Include Southwest, Ryanair, and easyJet in Pass 1 because they do not use ATPCO and may be absent or incomplete in aggregator results. Each agent searches the requested route, dates, party, cabin, baggage assumptions, and date mode.
4. For `relative` date mode, each Pass 1 agent records the exact-date search first, then alternate-date searches up to 3 calendar days before or after the departure and return dates. For `exact` date mode, do not search alternate dates.
5. Route every Pass 1 result batch to Alignment. Send aligned candidates to Writer. Store rejected or uncertain candidates with reasons when they explain a price gap or risk.
6. From aligned Pass 1 results, identify carriers and materially promising itinerary families. Spawn Pass 2 Research agents for individual carrier websites that need direct validation or were not already covered as non-ATPCO Pass 1 sources. Assign by carrier or carrier-family, not by search engine.
7. Route every Pass 2 result batch to Alignment. Send aligned direct-carrier validation data to Writer. Capture direct-booking price, fare or bundle, availability, baggage included or fees, visible change/cancel notes, seat-selection fees when obvious, booking-link viability, and any search-engine mismatch.
8. Load `references/research-playbook.md` before deep comparison. Use it for route expansion, separate-ticket rules, international gateway searches, baggage checks, and validation fields.
9. Price each candidate for the full party and baggage assumptions, including unavoidable fees and currency conversion notes when relevant. Record the cheapest viable direct, same-ticket connection, and any materially useful alternate-date, alternate-airport, or separate-ticket candidates allowed by the request.
10. Rank viable itineraries by total price. Also mark `best_recommended` for the option with the best balance of price, same-ticket protection, connection risk, baggage policy, and overnight avoidance.
11. Re-check the leading search-engine and carrier pages near the end. Store timestamps and uncertainty notes.
12. Set `itineraries.recommendation_type`, `research_runs.completed_at`, and final run notes before the final response.

## Worker Return Shape

Research agents should return compact structured data:

- task key, pass number, source or carrier, status, searched URL, searched timestamp,
- search parameters, passenger count, cabin, baggage assumptions, and date mode used,
- candidate itineraries with segment details, total party price, currency, booking method, baggage notes, connection buffers, and risk notes,
- discarded options with reasons,
- backoff details when applicable.

Alignment agents return `accepted`, `rejected`, and `needs_review` lists with constraint-specific reasons. Writer agents return the inserted or updated table names and row identifiers.

## Output

Return a concise SQLite-derived comparison with:

- database path, assumptions, and search timestamp,
- cheapest option and best recommended option,
- viable itinerary table sorted by total price,
- route, carriers, booking method, total cost, baggage included, buffers, and risks,
- Google Flights discovery price versus direct carrier confirmation price for top options,
- important baggage warnings or discarded cheap options.
