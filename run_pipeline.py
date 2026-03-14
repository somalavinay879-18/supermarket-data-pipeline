import pandas as pd
import duckdb

print("\nStarting Supermarket Data Pipeline...\n")

sales = pd.read_csv("data/SuperMarket Analysis.csv")
products = pd.read_csv("data/product_costs.csv")

sales.columns = sales.columns.str.lower().str.replace(" ", "_")
products.columns = products.columns.str.lower().str.replace(" ", "_")

merged = sales.merge(products, on="product_line")

merged["profit"] = merged["sales"] - (merged["quantity"] * merged["cost_price"])

conn = duckdb.connect("warehouse.duckdb")

conn.execute("CREATE OR REPLACE TABLE sales_data AS SELECT * FROM merged")

avg_sales = conn.execute("SELECT AVG(sales) FROM sales_data").fetchone()[0]
avg_cost = conn.execute("SELECT AVG(cost_price) FROM sales_data").fetchone()[0]
total_sales = conn.execute("SELECT SUM(sales) FROM sales_data").fetchone()[0]

print("Average Sales:", round(avg_sales, 2))
print("Average Product Cost:", round(avg_cost, 2))
print("Total Sales:", round(total_sales, 2))
print("Rows processed:", len(merged))

conn.close()

print("\nPipeline executed successfully!")
print("DuckDB warehouse updated: warehouse.duckdb\n")