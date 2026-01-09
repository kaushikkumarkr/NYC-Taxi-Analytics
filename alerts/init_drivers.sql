CREATE TABLE IF NOT EXISTS kpi_alert_drivers (
    driver_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID NOT NULL,
    dimension VARCHAR(50), -- e.g. zone, payment_type
    segment_value VARCHAR(100), -- e.g. JFK Airport
    baseline_value NUMERIC,
    current_value NUMERIC,
    delta NUMERIC,
    contribution_pct NUMERIC,
    rank INTEGER,
    details_json TEXT, -- extra context
    FOREIGN KEY (alert_id) REFERENCES kpi_alerts(alert_id)
);

CREATE INDEX IF NOT EXISTS idx_drivers_alert_id ON kpi_alert_drivers(alert_id);
