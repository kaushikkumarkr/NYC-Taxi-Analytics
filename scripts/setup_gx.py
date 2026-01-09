import great_expectations as gx
from great_expectations.core.batch import BatchRequest
from great_expectations.core.expectation_configuration import ExpectationConfiguration
import os

# Database Connection String
DB_CONNECTION_STRING = "postgresql+psycopg2://admin:adminparams@localhost:5432/analytics"

def setup_gx():
    print("🚀 Initializing Great Expectations...")
    context = gx.get_context(context_root_dir=os.path.join(os.getcwd(), "gx"))
    
    # 1. Add/Get Datasource
    datasource_name = "postgres_analytics"
    
    # Check if exists by name
    ds_names = [ds["name"] for ds in context.list_datasources()]
    if datasource_name in ds_names:
        print(f"Datasource {datasource_name} exists. Retrieving...")
        datasource = context.get_datasource(datasource_name)
    else:
        print(f"Adding Datasource: {datasource_name}")
        datasource = context.sources.add_sql(
            name=datasource_name,
            connection_string=DB_CONNECTION_STRING,
        )

    # 2. Add Assets (Tables)
    asset_name = "mart_kpis_daily"
    table_name = "mart_kpis_daily"
    schema_name = "dbt_dev_marts"
    
    # Check if asset exists
    existing_asset_names = [a.name for a in datasource.assets]
    if asset_name not in existing_asset_names:
        print(f"Adding Asset: {asset_name}")
        datasource.add_table_asset(
            name=asset_name,
            table_name=table_name,
            schema_name=schema_name
        )
        # Force save? context.sources.add_sql saves, but updating an asset might not?
        # In fluent API, adding an asset to a datasource should persist it if the datasource is persisted.
        # Let's try to explicit save if possible, or trigger context save.
        context._save_project_config()
    else:
        print(f"Asset {asset_name} already exists.")

    # 3. Create Expectation Suite: Critical Integrity
    suite_name = "suite_critical_integrity"
    print(f"Creating/Updating Suite: {suite_name}")
    
    suite = context.add_or_update_expectation_suite(expectation_suite_name=suite_name)
    
    # Define Expectations
    expectations = [
        # Volume: Table should not be empty
        ExpectationConfiguration(
            expectation_type="expect_table_row_count_to_be_between",
            kwargs={"min_value": 1, "max_value": None}
        ),
        # Integrity: Revenue should be positive (or zero)
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "total_revenue", 
                "min_value": 0, 
                "mostly": 1.0 # 100% strict
            }
        ),
        # Sanity: Avg Fare usually < $500
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "avg_fare",
                "min_value": 0,
                "max_value": 500
            }
        ),
        # Schema: Critical columns must exist and not be null
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={"column": "pickup_date"}
        )
    ]
    
    for exp in expectations:
        suite.add_expectation(exp)
    
    context.save_expectation_suite(suite, overwrite_existing=True)
    
    # 4. Create Checkpoint
    checkpoint_name = "checkpoint_critical"
    print(f"Creating/Updating Checkpoint: {checkpoint_name}")
    
    checkpoint_config = {
        "name": checkpoint_name,
        "config_version": 1,
        "class_name": "Checkpoint",
        "validations": [
            {
                "batch_request": {
                    "datasource_name": datasource_name,
                    "data_asset_name": asset_name
                },
                "expectation_suite_name": suite_name
            }
        ],
        "action_list": [
            {
                "name": "store_validation_result",
                "action": {"class_name": "StoreValidationResultAction"}
            },
            {
                "name": "update_data_docs",
                "action": {"class_name": "UpdateDataDocsAction"}
            }
        ]
    }
    
    context.add_or_update_checkpoint(**checkpoint_config)
    print("✅ GX Setup Complete.")

if __name__ == "__main__":
    setup_gx()
