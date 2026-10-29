-- Apply explicitly on an isolated branch first. Never reset this ledger to retry.
-- A single lifetime reservation, not a monthly counter or configurable scope.
CREATE TABLE IF NOT EXISTS picknow_oddize_probe_budget (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    request_id uuid NOT NULL UNIQUE,
    reserved_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
