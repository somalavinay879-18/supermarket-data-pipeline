"""Supermarket sales pipeline: read, clean, merge, validate, load into DuckDB.

Business rule (unchanged from the first version):
    profit = sales - quantity * cost_price
Note: in this dataset `sales` already includes the 5 % tax.
"""
from pathlib import Path

import pandas as pd

SALES_FILE = "SuperMarket Analysis.csv"
COSTS_FILE = "product_costs.csv"
REQUIRED_SALES_COLUMNS = {"invoice_id", "product_line", "quantity", "sales"}


class DataQualityError(ValueError):
    """Raised when the input data breaks a rule the pipeline relies on."""


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def read_sources(data_dir="data"):
    data_dir = Path(data_dir)
    # utf-8-sig removes the invisible BOM that the sales file starts with
    sales = pd.read_csv(data_dir / SALES_FILE, encoding="utf-8-sig")
    costs = pd.read_csv(data_dir / COSTS_FILE, encoding="utf-8-sig")
    return clean_columns(sales), clean_columns(costs)


def validate_inputs(sales: pd.DataFrame, costs: pd.DataFrame) -> None:
    missing = REQUIRED_SALES_COLUMNS - set(sales.columns)
    if missing:
        raise DataQualityError(f"Sales file is missing columns: {sorted(missing)}")
    if not {"product_line", "cost_price"} <= set(costs.columns):
        raise DataQualityError("Cost file needs the columns product_line and cost_price")
    if costs["product_line"].duplicated().any():
        raise DataQualityError("Cost file has a product line more than once (merge would duplicate sales)")
    if sales["invoice_id"].duplicated().any():
        raise DataQualityError("Sales file has duplicate invoice ids")
    if (sales["quantity"] <= 0).any() or (sales["sales"] <= 0).any():
        raise DataQualityError("Quantity and sales must be above 0")
    unknown = set(sales["product_line"]) - set(costs["product_line"])
    if unknown:
        raise DataQualityError(f"No cost price for product lines: {sorted(unknown)}")
    if costs["cost_price"].isna().any() or (costs["cost_price"] < 0).any():
        raise DataQualityError("cost_price must be a number of at least 0")


def transform(sales: pd.DataFrame, costs: pd.DataFrame) -> pd.DataFrame:
    validate_inputs(sales, costs)
    merged = sales.merge(costs, on="product_line", how="left", validate="many_to_one")
    if len(merged) != len(sales):
        raise DataQualityError("Merge changed the number of rows")
    merged["profit"] = merged["sales"] - merged["quantity"] * merged["cost_price"]
    return merged


def load_warehouse(df: pd.DataFrame, db_path="warehouse.duckdb") -> dict:
    import duckdb

    con = duckdb.connect(str(db_path))
    try:
        con.execute("CREATE OR REPLACE TABLE sales_data AS SELECT * FROM df")
        row = con.execute(
            "SELECT count(*), AVG(sales), AVG(cost_price), SUM(sales), SUM(profit) FROM sales_data"
        ).fetchone()
    finally:
        con.close()
    return {"rows": row[0], "avg_sales": row[1], "avg_cost": row[2],
            "total_sales": row[3], "total_profit": row[4]}


def run(data_dir="data", db_path="warehouse.duckdb") -> dict:
    sales, costs = read_sources(data_dir)
    merged = transform(sales, costs)
    return load_warehouse(merged, db_path)
