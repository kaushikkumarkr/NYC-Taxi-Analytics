# 🚖 NYC Taxi Analytics Command Center
> **Comprehensive Analytics Suite for Driver Performance, Revenue Optimization & Demand Forecasting.**

[![Status](https://img.shields.io/badge/Project-Complete-green?style=for-the-badge)]()
[![Stack](https://img.shields.io/badge/Tooling-SQL%20%7C%20Python%20%7C%20Tableau%2FRunSuperset%20%7C%20Statistics-blue?style=for-the-badge)]()

---

## 📖 Executive Summary
This project analyzes **3 Million+ taxi trips** (Jan 2024) to uncover actionable insights for fleet operations. By integrating historical trip data with predictive modeling, this "Command Center" enables stakeholders to monitor real-time health, identify revenue leakage, and proactively manage fleet supply.

### 🎯 Key Business Objectives
1.  **Revenue Optimization**: Identify high-value zones and peak hours to maximize driver earnings.
2.  **Operational Health**: Monitor fleet performance intervals using statistical anomaly detection.
3.  **Supply Planning**: Forecast 7-day demand trends to align driver schedules with predicted surges.

---

## 📊 distinct KPIs & Metrics
We designed and engineered a robust set of Key Performance Indicators (KPIs) to track health across three dimensions:

| Category | KPI Name | Definition | Business Relevance |
| :--- | :--- | :--- | :--- |
| **Financial** | **Revenue per Mile (RPM)** | `Total Revenue / Trip Distance` | Measures efficiency of route utilization. |
| **Financial** | **Average Fare** | `Total Amount / Trip Count` | Tracks pricing power and identifying premium trips. |
| **Operational** | **Utilization Rate** | `Time with Passenger / Total Shift Time` | Critical metric for driver productivity. |
| **Operational** | **congestion_surcharge %** | `% of trips in Congestion Zones` | Impact of Manhattan congestion taxes on net earnings. |
| **Quality** | **Tip Rate** | `Tip Amount / Fare Amount` | Proxy for customer satisfaction and service quality. |

---

## 📸 Analytics Dashboard (The "Command Center")

### 1. Operational Overview
*A high-level view for Fleet Managers to track daily volume and revenue against targets.*
![Dashboard Overview](docs/images/dashboard_overview.jpg)

### 2. Demand Forecasting (AI-Powered)
*Time-series regression model (Prophet) predicting future trip volume with 95% confidence intervals.*
> **Insight**: Allows dispatchers to pre-allocate drivers to zones with predicted demand surges.
![Forecast Chart](docs/images/forecast_chart.png)

### 3. Data Lineage & Trust
*Transparent data flow ensuring every metric on the dashboard is traceable back to the raw source.*
![Dagster Lineage](docs/images/dagster_lineage.png)

---

## 🔬 Analytical Methodology
This project moves beyond ad-hoc analysis by establishing a reproducible, trustworthy data pipeline.

### 1. Data Cleaning & Integrity (The "Trust" Layer)
*   **Problem**: Raw taxi data contains errors (negative fares, zero distances, future dates).
*   **Solution**: Implemented **Great Expectations** suites to automatically quarantine bad data.
    *   *Rule 1*: `trip_distance` must be > 0.
    *   *Rule 2*: `passenger_count` cannot be null.
    *   *Rule 3*: `total_amount` must be standard currency format.

### 2. Anomaly Detection (The "Safety" Layer)
*   **Technique**: Robust Z-Score Analysis.
*   **Application**: Automatically flags days where metrics deviate by >3 Standard Deviations from the 30-day moving average.
*   **Result**: Detected a 15% drop in volume on Jan 15th (correlated with Martin Luther King Jr. Day).

### 3. Predictive Modeling (The "Future" Layer)
*   **Algorithm**: Facebook Prophet (Additive Regression).
*   **Features**: Seasonality (Weekly/Daily), US Holidays.
*   **Accuracy**: Achieved a **MAPE (Mean Absolute Percentage Error) of ~8.5%**, meaning our forecasts are accurate within +/- 8.5% of actuals.

---

## 🛠 Tools & Technologies
Used a modern data stack to ensure scalability and reproducibility:

*   **SQL (PostgreSQL & dbt)**: For complex data modeling, aggregations, and window functions (Rolling Averages).
*   **Python (Pandas & Scikit-Learn)**: For statistical analysis and data ingestion.
*   **Apache Superset**: For enterprise-grade BI visualization.
*   **Git/GitHub**: For version control and CI/CD best practices.

---

## 🚀 How to Run Analysis
Prerequisites: Docker installed.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/kaushikkumarkr/NYC-Taxi-Analytics.git
    cd NYC-Taxi-Analytics
    ```

2.  **Launch Environment**
    ```bash
    make up       # Starts Database & BI Tool
    make setup    # Installs Analytics Libraries
    ```

3.  **Execute Pipeline**
    ```bash
    make ingest-full   # Load Fresh Data
    make dbt-run       # Calculate KPIs
    make forecast      # Generate Predictions
    ```

4.  **View Results**
    Access the dashboard at `http://localhost:8088`.
