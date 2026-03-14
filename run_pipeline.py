import pandas as pd
import duckdb

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

print("Average Sales:", avg_sales)
print("Average Product Cost:", avg_cost)
