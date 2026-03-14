
                                               Supermarket Data Pipeline

This project implements a simple local data engineering pipeline using Python, DuckDB, SQL and Streamlit. 
The goal of the project is to process supermarket sales data, store the processed data in a database and 
visualize business metrics through a dashboard. The pipeline reads raw CSV files, merges datasets, 
calculates profit and loads the processed result into a DuckDB warehouse table. The dashboard then reads 
the processed data and displays key metrics and visualizations.

The project uses two datasets. The first dataset is SuperMarket Analysis.csv, which contains transaction 
level information such as invoice id, branch, city, customer type, gender, product line, unit price, 
quantity, sales and payment method. The second dataset is product_costs.csv, which contains the cost price 
for each product line. These two datasets are merged inside the pipeline using the product_line column.

The pipeline is implemented in run_pipeline.py. When the pipeline runs, it reads the two datasets using 
pandas, standardizes the column names, merges the datasets, calculates profit using the formula:

profit = sales - (quantity * cost_price)

The final dataset is loaded into a DuckDB database file called warehouse.duckdb. Inside the database a 
table called sales_data is created or replaced each time the pipeline runs. SQL queries are then used to 
calculate metrics such as average sales, average product cost and total sales.

How to Run the Project

1. Clone the repository and open the project folder.

git clone https://github.com/somalavinay879-18/supermarket-data-pipeline.git
cd supermarket-data-pipeline

2. Create a virtual environment.

python -m venv venv

3. Activate the virtual environment.

Linux / Mac:
source venv/bin/activate

Windows:
venv\Scripts\activate

4. Install the required dependencies.

pip install -r requirements.txt

5. Run the data pipeline.

python run_pipeline.py

Example output:

Starting Supermarket Data Pipeline...
Average Sales: 322.97
Average Product Cost: 37.51
Total Sales: 322966.75
Rows processed: 1000
Pipeline executed successfully!

Running SQL Queries

You can open the DuckDB console to run SQL queries on the warehouse database.

duckdb warehouse.duckdb

Example SQL queries:

SELECT COUNT(*) FROM sales_data;
SELECT AVG(sales) FROM sales_data;
SELECT product_line, SUM(sales) FROM sales_data GROUP BY product_line;
SELECT city, SUM(profit) FROM sales_data GROUP BY city;

Running the Dashboard

To start the dashboard:

streamlit run dashboard.py

Open your browser and go to:
http://localhost:8501

The dashboard displays metrics such as average sales, average product cost, total sales and total profit. 
It also shows charts such as sales by product line and sales by city.

Testing the Pipeline

To test the pipeline, add a new row to the dataset located in:

data/SuperMarket Analysis.csv

After adding a new record, run the pipeline again:

python run_pipeline.py

You should see the row count increase and the metrics update. Refresh the Streamlit dashboard and the 
values will update automatically, confirming that the pipeline processes new data correctly.
