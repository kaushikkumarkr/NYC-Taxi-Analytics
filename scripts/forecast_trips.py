import os
import pandas as pd
import logging
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# Usage:
# python scripts/forecast_trips.py

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database Connection
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "adminparams")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "analytics")

DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def fetch_history(engine):
    """Fetch daily trip counts from the KPI Mart."""
    logger.info("⏳ Fetching historical data...")
    query = """
    SELECT pickup_date as ds, total_trips as y
    FROM dbt_dev_marts.mart_kpis_daily
    WHERE pickup_date BETWEEN '2024-01-01' AND '2024-01-31'
    ORDER BY pickup_date ASC;
    """
    try:
        df = pd.read_sql(query, engine)
        df['ds'] = pd.to_datetime(df['ds'])
        logger.info(f"✅ Loaded {len(df)} days of history. Range: {df['ds'].min()} to {df['ds'].max()}")
        return df
    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        raise

def evaluate_model(model):
    """Run cross-validation and return performance metrics."""
    logger.info("📐 Running Cross-Validation (Backtesting)...")
    try:
        # We only have 31 days.
        # Train on first 21 days (Jan 1-21)
        # Test on next 3 days. Move forward by 3 days.
        # This gives us adequate folds within a single month.
        df_cv = cross_validation(model, initial='21 days', period='3 days', horizon='3 days')
        df_p = performance_metrics(df_cv)
        
        # Log average metrics
        avg_rmse = df_p['rmse'].mean()
        avg_mape = df_p['mape'].mean()
        
        logger.info(f"📊 Model Performance -> RMSE: {avg_rmse:.2f}, MAPE: {avg_mape:.2%}")
        return df_p
    except ValueError as e:
        logger.warning(f"⚠️ Could not run cross-validation (likely too little data): {e}")
        return None

def generate_forecast(df, days=7):
    """Train Prophet model and forecast future days."""
    logger.info(f"🔮 Training Prophet model (Forecast Horizon: {days} days)...")
    
    # Initialize with specialized settings
    m = Prophet(
        daily_seasonality=False, 
        yearly_seasonality=False,
        seasonality_mode='multiplicative' # Traffic swings are percentage-based usually
    )
    m.add_seasonality(name='weekly', period=7, fourier_order=3)
    
    # Feature 1: US Holidays
    m.add_country_holidays(country_name='US')
    
    m.fit(df)
    
    # Validate
    evaluate_model(m)
    
    # Future Dataframe
    future = m.make_future_dataframe(periods=days)
    forecast = m.predict(future)
    
    # Keep key columns
    result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)
    logger.info("✅ Forecast generated.")
    return result

def save_forecast(engine, forecast_df):
    """Save forecast results to Postgres."""
    logger.info("💾 Saving forecast to DB...")
    # Add metadata
    forecast_df['forecast_run_date'] = datetime.now()
    
    forecast_df.to_sql('forecast_trips', engine, if_exists='replace', index=False)
    logger.info("✅ Forecast saved to table 'forecast_trips'.")

def main():
    try:
        engine = create_engine(DATABASE_URI)
        
        # 1. Get Data
        history_df = fetch_history(engine)
        
        if len(history_df) < 14:
            logger.warning("⚠️ Not enough data to forecast reliably (need 2+ weeks). Running anyway for demo.")
        
        # 2. Forecast
        forecast_df = generate_forecast(history_df, days=7)
        print(forecast_df)
        
        # 3. Save
        save_forecast(engine, forecast_df)
        
    except Exception as e:
        logger.error(f"❌ Forecasting failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
