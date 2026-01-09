# Superset Dashboard Recipe: Analytics Command Center

This guide walks you through building the "Analytics Command Center" dashboard in Superset manually.

## Prerequisites
Ensure Superset is running (`make up`) and you are logged in (admin/admin).

## 1. Connect Database
1.  Go to **Settings** -> **Database Connections**.
2.  Click **+ Database**.
3.  Select **PostgreSQL**.
4.  **Recommended Method**: Click **Advanced** tab -> **SQLAlchemy URI**.
    -   Enter: `postgresql://admin:adminparams@postgres:5432/analytics`
    -   Click **Test Connection**. It should say "Connection looks good!".

    **Alternative (Basic Form)**:
    -   **Host**: `postgres` (Not localhost!)
    -   **Port**: `5432`
    -   **Database**: `analytics`
    -   **Username**: `admin`
    -   **Password**: `adminparams`
    -   **Display Name**: `Analytics Warehouse`
5.  Click **Connect** -> **Finish**.

## 2. Create Datasets
Go to **Datasets** -> **+ Dataset**. Add the following tables from `dbt_dev_marts` schema:
1.  `mart_kpis_daily`
2.  `mart_kpis_hourly`
3.  `mart_kpis_by_zone_daily`
4.  `kpi_alerts` (from public schema)

## 3. Build Charts

### Chart A: Total Revenue (Big Number)
-   **Dataset**: `mart_kpis_daily`
-   **Chart Type**: Big Number
-   **Metric**: `SUM(total_revenue)`
-   **Time Range**: Last 24 hours (or "No Filter" for total)
-   **Subheader**: "Total Revenue"

### Chart B: Total Trips (Big Number)
-   **Dataset**: `mart_kpis_daily`
-   **Chart Type**: Big Number
-   **Metric**: `SUM(total_trips)`

### Chart C: Revenue Trend (Line Chart) 📈
**Goal**: Show a 7-day rolling average of daily revenue.

1.  **Create Chart**: Select Dataset `mart_kpis_daily` -> Select Chart Type **Line Chart**.
2.  **Configuration (Data Tab)**:
    -   **Time Column**: `pickup_date`
    -   **Time Grain**: `Day`
    -   **Time Range**: Last 30 days
    -   **Metrics**: `SUM(total_revenue)`
    -   **Dimensions**: *Leave Empty* (We want a single total line)
    -   **Contribution Mode**: None
    -   **Series limit**: 0 (No limit)
    -   **Sort query by**: `SUM(total_revenue)` (Descending)
    -   **Row limit**: 10000

3.  **Configuration (Advanced Analytics Tab)**:
    -   **Rolling window**:
        -   **Rolling function**: Mean
        -   **Periods**: 7
        -   **Min periods**: 7
    -   **Time comparison**: *Leave Default*

4.  **Save as**: `Revenue Trend (7-Day Rolling)`

### Chart D: Top 10 Zones (Bar Chart) 📊
**Goal**: Identify the busiest pickup zones.

1.  **Create Chart**: Select Dataset `mart_kpis_by_zone_daily` -> Select Chart Type **Bar Chart**.
2.  **Configuration (Data Tab)**:
    -   **X-Axis**: `zone`
    -   **Metrics**: `SUM(total_trips)`
    -   **Sort query by**: `SUM(total_trips)` (Descending)
    -   **Row limit**: 10 (Change to 50 or 100 to see more zones)
    -   **Filters**: Add Filter -> `zone` -> **Is not null** (To hide unknown zones)
3.  **Save as**: `Top 10 Zones by Trips`

### Chart E: Recent Anomalies (Table) 🚨
**Goal**: List recent alerts and highlight severe ones.

1.  **Create Chart**: Select Dataset `kpi_alerts` -> Select Chart Type **Table**.
2.  **Configuration (Data Tab)**:
    -   **Time Column**: `alert_date`
    -   **Query Mode**: **Aggregate** (Default)
    -   **Dimensions**: Add `alert_date`, `metric_name`, `explanation`
    -   **Metrics**: Add new metric -> Simple -> Column: `deviation_pct`, Aggregate: `MAX` -> Label: `Deviation %`
    -   **Sort query by**: `Deviation %` (Descending) or `alert_date` (if available in sort)
    -   **Row limit**: 50
3.  **Configuration (Customize Tab)**:
    -   **Conditional Formatting**:
        -   Click **+ Add**.
        -   **Target Column**: `Deviation %`
        -   **Operator**: `>` (Greater than)
        -   **Target Value**: `0.5`
        -   **Color Scheme**: Select a Red/Orange gradient.
        -   Click **Apply**.
        -   *Optional*: Add another rule for **Drop** (Operator `<` -0.5) to highlight crashes.
4.  **Save as**: `Recent Anomalies`

### Chart F: Future Forecast (Predictive Analytics) 🔮
**Goal**: Compare what *should* have happened (Forecast) vs Reality.

1.  **Create Chart**: Select Dataset `forecast_trips` (Note: You may need to Add Dataset first).
2.  **Configuration (Data Tab)**:
    -   **Chart Type**: Line Chart
    -   **Time Column**: `ds`
    -   **Metrics**: `SUM(yhat)` (Rename to "Predicted Trips")
    -   **Time Range**: Next 7 days
3.  **Advanced Overlay (Optional)**:
    -   To see "Actual" vs "Predicted", use a **Mixed Time Series** chart.
    -   Query A: `mart_kpis_daily` (Actual Trips)
    -   Query B: `forecast_trips` (Predicted Trips)
4.  **Save as**: `Trip Forecast vs Actual`

### Chart Group G: The Analyst KPI Grid 📉
**Goal**: Visualizing the specific "Business Value" metrics defined in the README.

#### G1. Revenue Per Mile (Efficiency)
-   **Dataset**: `mart_kpis_daily`
-   **metric**: `SUM(revenue_per_mile)` -> Aggregate: `AVG`
-   **Label**: "Rev Per Mile ($)"

#### G2. Demand Intensity (Pressure)
-   **Dataset**: `mart_kpis_hourly`
-   **Metric**: `SUM(trips_per_hour_avg)` -> Aggregate: `AVG`
-   **Time Range**: Last 24 Hours
-   **Label**: "Trips/Hour (Intensity)"

#### G3. Congestion Exposure (Tax Impact)
-   **Dataset**: `mart_kpis_daily`
-   **Metric**: `AVG(pct_congestion_trips)`
-   **Format**: Percentage (%)
-   **Label**: "% Congestion Routes"

#### G4. Tip Rate (Satisfaction)
-   **Dataset**: `mart_kpis_daily`
-   **Metric**: `AVG(tip_rate)`
-   **Format**: Percentage (%)
-   **Label**: "Avg Tip Rate"

## 4. Assemble Dashboard
1.  Go to **Dashboards** -> **+ Dashboard**.
2.  Title: "Analytics Command Center".
3.  Drag and Drop your charts.
4.  Add a **Filter Box** (Date Range) to control all charts.
5.  **Save**.
