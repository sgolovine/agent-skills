# Flight Research Playbook

Use this playbook after the SQLite run exists and the initial Google Flights search is underway.

## Search Order

1. Search normal booked itineraries first:
   - direct flights,
   - connecting flights booked together on the same carrier, alliance, or interline itinerary,
   - other major flight-search surfaces only when Google Flights or carrier validation leaves an important gap.
2. Search separate-ticket permutations only when allowed by the user or clearly worth comparing:
   - same-airport positioning legs from the origin to candidate gateway airports,
   - same-airport onward legs from candidate arrival airports to the destination,
   - mixed-carrier connections that satisfy buffer rules.
3. For international trips, broaden the middle leg:
   - build a country-pair gateway matrix of plausible origin-country and destination-country airports,
   - compare international legs across that matrix,
   - add same-airport positioning legs on both sides to complete the requested trip.

## Candidate Rules

- Exclude airport transfers, even inside the same metro area.
- Increase connection buffers when visible airport, fare, terminal, overnight, or self-transfer evidence makes the minimum risky.
- For separate tickets, price each ticket group and make protection risk explicit.
- Record cheap discarded options when the reason matters, such as airport transfer, insufficient buffer, sold-out fare, or missing carry-on allowance.

## Baggage Checks

For separate-carrier itineraries, research each carrier's policy before recommending:

- personal item and carry-on allowance,
- dimensions, weight limits, and fees,
- checked-bag fees only when requested or needed for comparison,
- most restrictive policy across the itinerary,
- carry-on weight discrepancies greater than 10 lb.

## Carrier Validation

Validate promising Google Flights candidates on carrier sites before final ranking. Capture:

- direct-booking price, fare class, bundle, and availability,
- baggage allowance and fees,
- cancellation or change notes visible before payment,
- seat-selection fees when obvious,
- booking URL viability,
- mismatch with Google Flights, including sold-out fares, currency differences, membership or login requirements, and stale prices.

Parallelize carrier or itinerary-family checks only when the current harness supports it and the work can be merged back into the main SQLite database without losing source attribution.
