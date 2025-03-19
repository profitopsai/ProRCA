from data_generators.synthetic_sales_data import (
    generate_fashion_data_with_brand,
)


def test_generate_fashion_data():
    df = generate_fashion_data_with_brand(
        start_date="2023-01-01", end_date="2023-01-02"
    )
    assert not df.empty, "Generated DataFrame is empty"
    assert "ORDERDATE" in df.columns, "ORDERDATE column missing"
    assert "PROFIT_MARGIN" in df.columns, "PROFIT_MARGIN column missing"
