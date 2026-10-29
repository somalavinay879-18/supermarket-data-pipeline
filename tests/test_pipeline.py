import pandas as pd
import pytest

from pipeline import DataQualityError, clean_columns, read_sources, run, transform

SALES = pd.DataFrame({
    "invoice_id": ["a", "b", "c"],
    "city": ["X", "X", "Y"],
    "product_line": ["food", "food", "toys"],
    "quantity": [2, 1, 4],
    "sales": [100.0, 60.0, 200.0],
})
COSTS = pd.DataFrame({"product_line": ["food", "toys"], "cost_price": [10.0, 20.0]})


def test_clean_columns_lowercases_and_replaces_spaces():
    df = pd.DataFrame(columns=[" Invoice ID", "Product line", "Tax 5%"])
    assert list(clean_columns(df).columns) == ["invoice_id", "product_line", "tax_5%"]


def test_profit_is_sales_minus_quantity_times_cost():
    out = transform(SALES, COSTS).set_index("invoice_id")
    assert out.loc["a", "profit"] == 100 - 2 * 10
    assert out.loc["b", "profit"] == 60 - 1 * 10
    assert out.loc["c", "profit"] == 200 - 4 * 20


def test_merge_keeps_every_sales_row():
    assert len(transform(SALES, COSTS)) == len(SALES)


def test_missing_cost_price_for_a_product_line_fails():
    with pytest.raises(DataQualityError, match="No cost price"):
        transform(SALES, COSTS[COSTS["product_line"] == "food"])


def test_duplicate_product_line_in_costs_fails():
    with pytest.raises(DataQualityError, match="more than once"):
        transform(SALES, pd.concat([COSTS, COSTS.iloc[:1]]))


def test_duplicate_invoice_fails():
    with pytest.raises(DataQualityError, match="duplicate invoice"):
        transform(pd.concat([SALES, SALES.iloc[:1]]), COSTS)


def test_non_positive_quantity_fails():
    bad = SALES.copy()
    bad.loc[0, "quantity"] = 0
    with pytest.raises(DataQualityError, match="above 0"):
        transform(bad, COSTS)


def test_missing_column_fails():
    with pytest.raises(DataQualityError, match="missing columns"):
        transform(SALES.drop(columns=["quantity"]), COSTS)


def test_read_sources_handles_bom_in_first_column(tmp_path):
    (tmp_path / "SuperMarket Analysis.csv").write_text(
        "Invoice ID,Product line,Quantity,Sales\nx1,food,2,100\n", encoding="utf-8-sig")
    (tmp_path / "product_costs.csv").write_text(
        "Product line,cost_price\nfood,10\n", encoding="utf-8-sig")
    sales, costs = read_sources(tmp_path)
    assert "invoice_id" in sales.columns
    assert list(costs.columns) == ["product_line", "cost_price"]


def test_full_run_loads_the_warehouse(tmp_path):
    pytest.importorskip("duckdb")
    (tmp_path / "SuperMarket Analysis.csv").write_text(
        "Invoice ID,City,Product line,Quantity,Sales\n"
        "a,X,food,2,100\nb,X,food,1,60\nc,Y,toys,4,200\n", encoding="utf-8-sig")
    (tmp_path / "product_costs.csv").write_text(
        "Product line,cost_price\nfood,10\ntoys,20\n", encoding="utf-8-sig")
    stats = run(tmp_path, tmp_path / "w.duckdb")
    assert stats["rows"] == 3
    assert stats["total_sales"] == pytest.approx(360)
    assert stats["total_profit"] == pytest.approx(360 - (20 + 10 + 80))
