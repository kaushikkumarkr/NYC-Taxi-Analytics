CREATE TABLE IF NOT EXISTS kpi_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_date DATE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    grain VARCHAR(50) NOT NULL, -- daily, hourly
    metric_value NUMERIC,
    expected_value NUMERIC,
    deviation_pct NUMERIC,
    severity VARCHAR(20), -- info, warning, critical
    method VARCHAR(50),
    explanation TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kpi_alerts_date ON kpi_alerts(alert_date);
