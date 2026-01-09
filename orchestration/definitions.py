from dagster import Definitions, load_assets_from_modules, AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets, DbtProject

from pathlib import Path

# Define paths
DBT_PROJECT_DIR = Path(__file__).parent.parent / "dbt"

# Define dbt resource
dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
)

@dbt_assets(manifest=dbt_project.manifest_path)
def analytics_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()

# Definitions
defs = Definitions(
    assets=[analytics_dbt_assets],
    resources={
        "dbt": DbtCliResource(project_dir=dbt_project),
    },
)
