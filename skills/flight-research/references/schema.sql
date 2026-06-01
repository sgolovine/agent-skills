PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

INSERT OR REPLACE INTO schema_meta (key, value) VALUES
  ('schema_name', 'flight_research'),
  ('schema_version', '2');

CREATE TABLE research_runs (
  id INTEGER PRIMARY KEY,
  run_id TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  completed_at TEXT,
  user_request TEXT NOT NULL,
  output_database_path TEXT NOT NULL,
  origin_airports TEXT,
  destination_airports TEXT,
  departure_date TEXT,
  return_date TEXT,
  date_flexibility TEXT,
  passenger_count INTEGER NOT NULL DEFAULT 2,
  cabin TEXT NOT NULL DEFAULT 'economy',
  baggage_assumption TEXT NOT NULL,
  airport_flexibility TEXT,
  overnight_tolerance TEXT,
  self_transfer_tolerance TEXT,
  separate_tickets_allowed TEXT,
  assumptions_json TEXT NOT NULL DEFAULT '{}',
  notes TEXT
);

CREATE TABLE search_sources (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  agent_task_id INTEGER REFERENCES agent_tasks(id) ON DELETE SET NULL,
  pass_number INTEGER CHECK (pass_number IN (1, 2)),
  source_category TEXT CHECK (source_category IN ('search_engine', 'carrier_site', 'other')),
  source_name TEXT NOT NULL,
  source_url TEXT,
  searched_at TEXT NOT NULL DEFAULT (datetime('now')),
  search_parameters_json TEXT NOT NULL DEFAULT '{}',
  notes TEXT
);

CREATE TABLE agent_tasks (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  parent_task_id INTEGER REFERENCES agent_tasks(id) ON DELETE SET NULL,
  task_key TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('supervisor', 'research', 'alignment', 'writer')),
  pass_number INTEGER CHECK (pass_number IN (1, 2)),
  source_name TEXT,
  carrier_name TEXT,
  agent_id TEXT,
  attempt INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'backoff', 'completed', 'failed', 'stuck', 'closed', 'reassigned')),
  assigned_work_json TEXT NOT NULL DEFAULT '{}',
  result_json TEXT NOT NULL DEFAULT '{}',
  progress_summary TEXT,
  error_summary TEXT,
  assigned_at TEXT NOT NULL DEFAULT (datetime('now')),
  last_update_at TEXT NOT NULL DEFAULT (datetime('now')),
  backoff_until TEXT,
  completed_at TEXT,
  UNIQUE (run_id, task_key, attempt)
);

CREATE TABLE alignment_checks (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  agent_task_id INTEGER REFERENCES agent_tasks(id) ON DELETE SET NULL,
  itinerary_id INTEGER REFERENCES itineraries(id) ON DELETE SET NULL,
  candidate_key TEXT,
  checked_at TEXT NOT NULL DEFAULT (datetime('now')),
  decision TEXT NOT NULL CHECK (decision IN ('accepted', 'rejected', 'needs_review')),
  matches_route INTEGER CHECK (matches_route IN (0, 1)),
  matches_dates INTEGER CHECK (matches_dates IN (0, 1)),
  matches_passengers INTEGER CHECK (matches_passengers IN (0, 1)),
  matches_cabin INTEGER CHECK (matches_cabin IN (0, 1)),
  matches_baggage INTEGER CHECK (matches_baggage IN (0, 1)),
  matches_connection_rules INTEGER CHECK (matches_connection_rules IN (0, 1)),
  issues_json TEXT NOT NULL DEFAULT '[]',
  notes TEXT
);

CREATE TABLE writer_outputs (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  agent_task_id INTEGER REFERENCES agent_tasks(id) ON DELETE SET NULL,
  wrote_at TEXT NOT NULL DEFAULT (datetime('now')),
  table_name TEXT NOT NULL,
  row_ids_json TEXT NOT NULL DEFAULT '[]',
  source_task_key TEXT,
  notes TEXT
);

CREATE TABLE itineraries (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  candidate_key TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('viable', 'discarded', 'pending')),
  recommendation_type TEXT CHECK (recommendation_type IN ('cheapest', 'best_recommended', 'alternate', 'none')),
  rank_by_price INTEGER,
  origin_airport TEXT NOT NULL,
  destination_airport TEXT NOT NULL,
  outbound_departure_at TEXT,
  outbound_arrival_at TEXT,
  return_departure_at TEXT,
  return_arrival_at TEXT,
  total_duration_minutes INTEGER,
  total_price_amount REAL,
  currency TEXT,
  total_price_usd REAL,
  price_checked_at TEXT,
  google_flights_price_amount REAL,
  direct_carrier_price_amount REAL,
  booking_method TEXT,
  booking_url TEXT,
  validating_source TEXT,
  same_ticket INTEGER NOT NULL DEFAULT 1 CHECK (same_ticket IN (0, 1)),
  separate_tickets INTEGER NOT NULL DEFAULT 0 CHECK (separate_tickets IN (0, 1)),
  self_transfer INTEGER NOT NULL DEFAULT 0 CHECK (self_transfer IN (0, 1)),
  airport_transfer_required INTEGER NOT NULL DEFAULT 0 CHECK (airport_transfer_required IN (0, 1)),
  overnight_layovers INTEGER NOT NULL DEFAULT 0,
  included_baggage_summary TEXT,
  risk_summary TEXT,
  notes TEXT,
  UNIQUE (run_id, candidate_key)
);

CREATE TABLE flight_segments (
  id INTEGER PRIMARY KEY,
  itinerary_id INTEGER NOT NULL REFERENCES itineraries(id) ON DELETE CASCADE,
  direction TEXT NOT NULL CHECK (direction IN ('outbound', 'return', 'positioning', 'other')),
  segment_order INTEGER NOT NULL,
  ticket_group INTEGER NOT NULL DEFAULT 1,
  marketing_carrier TEXT,
  operating_carrier TEXT,
  flight_number TEXT,
  origin_airport TEXT NOT NULL,
  destination_airport TEXT NOT NULL,
  departure_at TEXT,
  arrival_at TEXT,
  duration_minutes INTEGER,
  cabin TEXT,
  fare_class TEXT,
  aircraft TEXT,
  notes TEXT,
  UNIQUE (itinerary_id, direction, segment_order)
);

CREATE TABLE fare_quotes (
  id INTEGER PRIMARY KEY,
  itinerary_id INTEGER NOT NULL REFERENCES itineraries(id) ON DELETE CASCADE,
  source_name TEXT NOT NULL,
  source_url TEXT,
  checked_at TEXT NOT NULL DEFAULT (datetime('now')),
  fare_name TEXT,
  available INTEGER CHECK (available IN (0, 1)),
  base_price_amount REAL,
  taxes_fees_amount REAL,
  total_price_amount REAL,
  currency TEXT,
  total_price_usd REAL,
  included_bags_json TEXT NOT NULL DEFAULT '{}',
  seat_selection_fee_notes TEXT,
  change_cancel_notes TEXT,
  membership_or_login_required INTEGER NOT NULL DEFAULT 0 CHECK (membership_or_login_required IN (0, 1)),
  mismatch_notes TEXT,
  notes TEXT
);

CREATE TABLE connection_buffers (
  id INTEGER PRIMARY KEY,
  itinerary_id INTEGER NOT NULL REFERENCES itineraries(id) ON DELETE CASCADE,
  inbound_segment_id INTEGER REFERENCES flight_segments(id) ON DELETE SET NULL,
  outbound_segment_id INTEGER REFERENCES flight_segments(id) ON DELETE SET NULL,
  airport TEXT NOT NULL,
  scheduled_buffer_minutes INTEGER,
  required_buffer_minutes INTEGER NOT NULL,
  buffer_basis TEXT NOT NULL,
  is_viable INTEGER NOT NULL CHECK (is_viable IN (0, 1)),
  notes TEXT
);

CREATE TABLE baggage_policies (
  id INTEGER PRIMARY KEY,
  itinerary_id INTEGER REFERENCES itineraries(id) ON DELETE CASCADE,
  carrier TEXT NOT NULL,
  source_url TEXT,
  checked_at TEXT NOT NULL DEFAULT (datetime('now')),
  personal_item_summary TEXT,
  carry_on_summary TEXT,
  carry_on_weight_lbs REAL,
  carry_on_fee_amount REAL,
  checked_bag_fee_amount REAL,
  currency TEXT,
  most_restrictive_for_itinerary INTEGER NOT NULL DEFAULT 0 CHECK (most_restrictive_for_itinerary IN (0, 1)),
  notes TEXT
);

CREATE TABLE discard_reasons (
  id INTEGER PRIMARY KEY,
  itinerary_id INTEGER NOT NULL REFERENCES itineraries(id) ON DELETE CASCADE,
  reason_code TEXT NOT NULL,
  reason_detail TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE research_events (
  id INTEGER PRIMARY KEY,
  run_id INTEGER NOT NULL REFERENCES research_runs(id) ON DELETE CASCADE,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  event_type TEXT NOT NULL,
  summary TEXT NOT NULL,
  details_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_itineraries_run_price ON itineraries (run_id, status, total_price_usd, total_price_amount);
CREATE INDEX idx_segments_itinerary ON flight_segments (itinerary_id, direction, segment_order);
CREATE INDEX idx_fares_itinerary ON fare_quotes (itinerary_id, checked_at);
CREATE INDEX idx_baggage_itinerary ON baggage_policies (itinerary_id, carrier);
CREATE INDEX idx_agent_tasks_run_status ON agent_tasks (run_id, status, pass_number, role);
CREATE INDEX idx_alignment_run_decision ON alignment_checks (run_id, decision);

CREATE VIEW viable_itinerary_summary AS
SELECT
  r.run_id,
  i.id AS itinerary_id,
  i.rank_by_price,
  i.recommendation_type,
  i.origin_airport,
  i.destination_airport,
  i.total_price_amount,
  i.currency,
  i.total_price_usd,
  i.booking_method,
  i.validating_source,
  i.included_baggage_summary,
  i.risk_summary,
  i.price_checked_at
FROM itineraries i
JOIN research_runs r ON r.id = i.run_id
WHERE i.status = 'viable'
ORDER BY i.total_price_usd IS NULL, i.total_price_usd, i.total_price_amount;

CREATE VIEW final_recommendations AS
SELECT *
FROM viable_itinerary_summary
WHERE recommendation_type IN ('cheapest', 'best_recommended')
ORDER BY
  CASE recommendation_type
    WHEN 'cheapest' THEN 1
    WHEN 'best_recommended' THEN 2
    ELSE 3
  END;

CREATE VIEW agent_progress_summary AS
SELECT
  r.run_id,
  t.pass_number,
  t.task_key,
  t.role,
  COALESCE(t.source_name, t.carrier_name, '') AS assignment,
  t.agent_id,
  t.attempt,
  t.status,
  t.last_update_at,
  t.backoff_until,
  t.progress_summary
FROM agent_tasks t
JOIN research_runs r ON r.id = t.run_id
ORDER BY
  t.pass_number IS NULL,
  t.pass_number,
  t.role,
  t.task_key,
  t.attempt;
