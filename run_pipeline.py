import sys

from pipeline import DataQualityError, run

print("\nStarting Supermarket Data Pipeline...\n")
try:
    stats = run()
except DataQualityError as error:
    print("Data quality check failed:", error)
    sys.exit(1)

print("Average Sales:", round(stats["avg_sales"], 2))
print("Average Product Cost:", round(stats["avg_cost"], 2))
print("Total Sales:", round(stats["total_sales"], 2))
print("Total Profit:", round(stats["total_profit"], 2))
print("Rows processed:", stats["rows"])
print("\nPipeline executed successfully!")
print("DuckDB warehouse updated: warehouse.duckdb\n")
