-- Show available tables
SHOW TABLES;

-- Preview data
SELECT * FROM sales_data LIMIT 10;

-- Average sales
SELECT AVG(sales) AS avg_sales
FROM sales_data;

-- Average product cost
SELECT AVG(cost_price) AS avg_product_cost
FROM sales_data;

-- Total sales by product line
SELECT product_line, SUM(sales) AS total_sales
FROM sales_data
GROUP BY product_line
ORDER BY total_sales DESC;

-- Total profit by city
SELECT city, SUM(profit) AS total_profit
FROM sales_data
GROUP BY city
ORDER BY total_profit DESC;

-- Top 5 profitable product lines
SELECT product_line, SUM(profit) AS profit
FROM sales_data
GROUP BY product_line
ORDER BY profit DESC
LIMIT 5;

-- Sales by payment method
SELECT payment, SUM(sales) AS total_sales
FROM sales_data
GROUP BY payment
ORDER BY total_sales DESC;
