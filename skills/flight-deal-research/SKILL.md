---
name: flight-deal-research
description: Research price-first airfare with Google Flights discovery, SQLite run output, and carrier-site validation. Use for finding, comparing, or optimizing flights by route and dates, including direct flights, booked connections, separate tickets, international positioning legs, baggage-aware totals, and round-trip/economy/two-passenger defaults.
---

# Flight Deal Research

## Operating Principle

Create the SQLite database first, use Google Flights for discovery, validate top fares on carrier sites, and rank by total party price before comfort.

## Defaults

- Round trip, 2 passengers, economy.
- 2 carry-ons and 2 personal items; exclude checked bags unless requested or needed for a fair comparison.
- No airport transfers. Discard itineraries that arrive at one airport and depart from another.
- Minimum connection buffers: 2 hours domestic same-airport; 3 hours for international, immigration, customs, re-checking bags, or self-transfer.
- Do not book, purchase, log in, send traveler details, or enter payment information without explicit confirmation for that exact browser action.

Ask one concise batch of questions only when missing inputs would materially change the search. Otherwise use these defaults, record assumptions in SQLite, and keep moving.

## SQLite Contract

Every run must create a fresh SQLite database before flight research starts. Treat the database as the durable output; the final response is a summary of database facts.

1. Create a run directory, defaulting to `flight-research-output/<YYYYMMDD-HHMMSS>/` in the current workspace unless the user requested another location.
2. Initialize the database from this skill folder:

   ```sh
   python3 scripts/init_flight_research_db.py --output flight-research-output/<run-id>/flight_research.sqlite
   ```

3. If the initializer cannot use Python's standard `sqlite3`, use another available SQLite client or library and apply `references/schema.sql` directly.
4. Insert one `research_runs` row with the request, defaults, clarified assumptions, and database path before browser research.
5. Record assumptions, searches, candidates, fares, baggage policies, connection buffers, discard reasons, validation checks, and final recommendations as research proceeds.
6. Before responding, query SQLite for final facts. Do not rely on notes outside the database.

Use `references/schema.sql` as the schema source of truth.

## Workflow

1. Read `$browser:browser`, then use the browser for live search.
2. Start at [Google Flights](https://www.google.com/travel/flights) with the requested route, dates, party, cabin, baggage assumptions, and allowed flexibility.
3. Load `references/research-playbook.md` before deep comparison. Use it for route expansion, separate-ticket rules, international gateway searches, baggage checks, and validation fields.
4. Record the cheapest viable direct, same-ticket connection, and any materially useful alternate-date, alternate-airport, or separate-ticket candidates.
5. Validate promising options on direct carrier sites. Capture direct-booking price, fare or bundle, availability, baggage included or fees, visible change/cancel notes, seat-selection fees when obvious, booking-link viability, and any Google Flights mismatch.
6. Price each candidate for the full party and baggage assumptions, including unavoidable fees and currency conversion notes when relevant.
7. Rank viable itineraries by total price. Also mark `best_recommended` for the option with the best balance of price, same-ticket protection, connection risk, baggage policy, and overnight avoidance.
8. Re-check Google Flights and carrier detail pages near the end. Store timestamps and uncertainty notes.
9. Set `itineraries.recommendation_type`, `research_runs.completed_at`, and final run notes before the final response.

## Output

Return a concise SQLite-derived comparison with:

- database path, assumptions, and search timestamp,
- cheapest option and best recommended option,
- viable itinerary table sorted by total price,
- route, carriers, booking method, total cost, baggage included, buffers, and risks,
- Google Flights discovery price versus direct carrier confirmation price for top options,
- important baggage warnings or discarded cheap options.
