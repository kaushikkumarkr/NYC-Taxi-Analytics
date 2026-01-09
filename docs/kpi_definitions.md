# KPI Definitions

## 1. Daily Metrics (`mart_kpis_daily`)
| Metric | Definition | Grain |
| :--- | :--- | :--- |
| `total_trips` | Count of all valid trips for the day. | Daily |
| `total_revenue` | Sum of `total_amount` (includes fare, tax, tip, tolls). | Daily |
| `avg_fare` | Average `fare_amount` per trip. | Daily |
| `pct_cash_trips` | Percentage of trips paid via Cash (PaymentType=2). | Daily |
| `late_night_share` | Percentage of trips starting between 10 PM and 5 AM. | Daily |

## 2. Hourly Metrics (`mart_kpis_hourly`)
Used for intraday trending and hourly anomaly detection.

## 3. Zone Metrics (`mart_kpis_by_zone_daily`)
Used for root cause analysis (geographic drilldown).

## Caveats
- **Total Amount**: Can be negative in raw data (refunds/disputes), but filtered/handled in staging if strict cleaning applied (currently passed through 'as is' for visibility, usually >0).
- **Cash Trips**: Rely on `payment_type` field. Voided trips are excluded from standard counts if `payment_type` is 0, but currently included in general counts.
