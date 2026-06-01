---
name: flight-deal-research
description: Research price-first flight deals starting with Google Flights, write structured results to SQLite, then validate promising options on carrier sites. Use when the user asks to find, compare, or optimize airfare for specific travel dates, origin and destination airports, including direct flights, booked connections, separate-ticket connections, international positioning legs, baggage-aware pricing, SQLite output, or round-trip/economy/two-passenger defaults.
---

# Flight Deal Research

## Operating Principle

Use `$browser:browser` for live research, create the SQLite output database before searching, start every search on Google Flights, rank by total price first, and front-load ambiguity because this skill often runs unattended in `/goal` mode.

## SQLite Output Contract

Every run must create and use a new SQLite database before flight research starts. Treat the database as the durable output; the final chat response is only a concise summary of what was written.

1. Resolve paths relative to this skill folder.
2. Create an output directory for the run, defaulting to `flight-research-output/<YYYYMMDD-HHMMSS>/` in the current workspace unless the user requested another location.
3. Initialize a fresh database from the skill folder, or by using absolute paths, with:

   ```sh
   python3 scripts/init_flight_research_db.py --output flight-research-output/<run-id>/flight_research.sqlite
   ```

4. If the initializer fails because Python SQLite bindings are missing, install or select a working host SQLite binding before research continues. Prefer Python's standard `sqlite3` module; otherwise use another available SQLite client or library and apply `references/schema.sql` directly.
5. Record the database path immediately. All assumptions, searches, candidates, validation checks, fares, baggage policies, connection buffers, discard reasons, and final recommendations must be inserted or updated in SQLite as research proceeds.
6. Before the final response, query the database for the cheapest viable option, best recommended option, and sorted itinerary table. Do not rely on notes outside the database for final facts.

Use `references/schema.sql` as the source of truth for the schema.

## Defaults

- Assume round trip unless the user says otherwise.
- Assume 2 passengers, economy class, 2 carry-ons, and 2 personal items.
- Do not include checked bags unless the user asks or the cheapest fare requires a checked-bag comparison.
- Treat the run as long-running and mostly unattended. Ask all materially important questions up front before deep research begins.
- During research, do not pause for new user input unless a live browser action would book, purchase, log in, transmit traveler details, or enter payment information. Make a conservative assumption, continue, and record the assumption for the final report.

## Workflow

1. Run an up-front clarification pass before background research:
   - Confirm travel dates, departing airport, destination airport, passenger count, cabin, baggage, date flexibility, airport flexibility, overnight tolerance, self-transfer tolerance, and whether separate tickets are allowed.
   - Ask one concise batch of questions only for missing or ambiguous inputs that materially change the search.
   - If the user has supplied enough to search, use the defaults above without asking.
   - If a useful preference is still unknown after research starts, choose the lower-risk or cheaper-by-default assumption, keep moving, and disclose it later.
2. Initialize the SQLite output environment using the output contract above. Insert one `research_runs` row with the request, defaults, clarified assumptions, and output database path before opening the browser.
3. Read and follow the `$browser:browser` skill before browser work. Keep research in the background unless the user asks to watch.
4. Start the initial market scan on Google Flights at `https://www.google.com/travel/flights`:
   - use the requested route, dates, passenger count, cabin, baggage assumptions, and any flexibility the user allowed,
   - record the cheapest viable direct, same-ticket connecting, and alternate-airport or date-flexible candidates,
   - use Google Flights price calendars, filters, and route permutations where they materially affect price,
   - treat Google Flights as discovery, not final pricing.
5. After the initial Google Flights search is complete, spawn subagents to research carrier websites directly for the promising carriers or itineraries:
   - give each subagent one carrier, route/date pair, or tightly scoped itinerary family,
   - ask them to gather direct-booking price, fare class or bundle, baggage allowance and fees, cancellation/change notes visible before payment, seat-selection fees when obvious, and booking-link viability,
   - ask them to confirm whether Google Flights pricing is still available on the carrier site and note any mismatch, sold-out fare, currency difference, or required membership/login,
   - merge each subagent's findings into the main SQLite database before using them in rankings or final output,
   - keep purchase, login, traveler-detail, and payment actions in the main thread only, and only with explicit user confirmation.
6. Search normal booked itineraries first:
   - direct flights,
   - connecting flights booked together on the same carrier or alliance/interline itinerary,
   - other major flight-search surfaces only when Google Flights or carrier validation leaves an important gap.
7. Search separate-ticket permutations:
   - same-airport positioning legs from the source airport to candidate gateway airports,
   - same-airport onward positioning legs from candidate arrival airports to the destination airport,
   - mixed-carrier connections only when each connection satisfies the buffer rules below.
8. For international trips, broaden the middle leg:
   - build a country-pair gateway matrix of plausible source-country airports and destination-country airports,
   - compare international legs across that matrix, not only from the requested origin to requested destination,
   - find the cheapest viable international leg,
   - then add same-airport domestic or international positioning legs on both sides to complete the requested origin-to-destination trip.
9. Exclude any itinerary that requires an airport transfer. If a connection arrives at one airport and departs from another in the same city, discard it.
10. Apply connection buffers:
   - at least 2 hours for same-airport domestic connections,
   - at least 3 hours when the connection involves international travel, immigration, customs, or re-checking bags,
   - more time when visible airport, fare, terminal, overnight, or self-transfer evidence makes the minimum buffer risky.
11. Price each candidate for the full party and baggage assumptions. Include unavoidable fees, separate-ticket totals, and currency conversion notes when relevant.
12. For separate-carrier itineraries, research each carrier's baggage policy before recommending the option:
   - compare carry-on and personal-item allowance, dimensions, weight limits, and fees,
   - price the itinerary using the most restrictive relevant policy,
   - warn when baggage policies differ materially,
   - always flag carry-on weight discrepancies greater than 10 lb between carriers.
13. Rank final candidates by price first. Also identify a "Best Recommended" option that considers fewer connections, no overnight layovers, same-ticket protection, baggage policy, and connection risk.
14. Validate the top results by re-checking Google Flights and the direct carrier detail pages near the end of the session. Flight prices change quickly; report the timestamp and any uncertainty.
15. Mark final recommendations in `itineraries.recommendation_type`, set `research_runs.completed_at`, and insert any final run notes before responding.

## Output

Return a concise comparison derived from SQLite with:

- SQLite database path,
- search assumptions and timestamp,
- cheapest option,
- best recommended option,
- table of viable itineraries sorted by total price,
- route, carriers, booking method, total cost, baggage included, connection buffers, and risks,
- baggage-policy warnings for separate-carrier itineraries,
- Google Flights discovery price versus direct carrier confirmation price for top options,
- discarded cheap options only when the reason matters, such as airport transfer, insufficient buffer, or missing carry-on allowance.

Do not book, purchase, log in, transmit traveler details, or enter payment information unless the user explicitly asks and confirms the specific browser action at action time.
